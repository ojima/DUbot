import asyncio
import datetime
import json
import shlex
import sys
import time

import discord

from democratiauniversalis.banking import Banking
from democratiauniversalis.metagame.game import Game
from democratiauniversalis.metagame.role import Role
from democratiauniversalis.rolemanager import RoleManager
import multiprocessing as Mp
import utils

def get_setting(settings, tag, default = None):
    if not tag in settings:
        if default is None:
            raise KeyError('Cannot get setting {0}: non-existent tag.'.format(tag))
        else:
            print('Cannot find setting {0}: using default {1}'.format(tag, default))
            return default

    return settings[tag]

async def responder(queue):
    await client.wait_until_ready()

    print('Starting response loop.')

    last = time.time()

    while True:
        got_reply = False
        while not queue.empty():
            event = queue.get()
            # TODO: nicely split messages into messages of no more than 2000 chars so that discord doesn't refuse too long messages.
            if isinstance(event['to'], list):
                for to in event['to']:
                    await client.send_message(to, event['message'])
            else:
                await client.send_message(event['to'], event['message'])

            got_reply = True

        if not got_reply:
            await asyncio.sleep(0.01)

        now = time.time()
        if now - last > save_timeout:
            last = now
            game.save(gamefile)

with open('settings.json', 'r') as tfile:
    settings = json.load(tfile)

token = get_setting(settings, 'token')
gamefile = get_setting(settings, 'gamefile')
bankfile = get_setting(settings, 'bankfile')
owners = get_setting(settings, 'owners')
save_timeout = get_setting(settings, 'save-timeout', 60.0)

respondqueue = Mp.Queue()

client = discord.Client()

game = Game()
for o in owners:
    game.add_owner(o)

banking = Banking(respondqueue, bankfile)
manager = RoleManager(game, respondqueue)

print('Initialized manager runnables.')

@client.event
async def on_ready():
    print('Starting bot loops.')

    game.load(gamefile)
    banking.load(bankfile)

    banking.start()
    manager.start()

    print('Done')
    print('------------------')

@client.event
async def on_message(message):
    if message.author.bot: return

    # Check for player
    player = game.get_player(message.author.id)
    if player is None:
        player = game.new_player(message.author.id, message.author.name)

    # Only respond if this is an explicit command [first character is a $] or if bot gets pinged and it is a command
    if message.clean_content.startswith('$') or (client.user in message.mentions and '$' in message.clean_content):
        s = message.clean_content.find('$')
        cmds = shlex.split(message.clean_content[s + 1:])

        command = utils.get_alias(cmds[0])

        if command is None:
            print('Failed to interpret command {0}.'.format(cmds[0]))
        elif not utils.can_do(command, player.roles):
            print('Player tried to execute command {0} without permission.'.format(cmds[0]))
        else:
            print('Running command {0}.'.format(command))

            if command == 'help':
                if len(cmds) > 1:
                    cmd = utils.get_alias(cmds[1])
                    desc = utils.get_help(cmd, player.roles)
                else:
                    desc = utils.get_help(command, player.roles)
                respondqueue.put({ 'to' : message.channel, 'message' : desc })
            elif command == 'all':
                desc = utils.get_all(player.roles)
                respondqueue.put({ 'to' : message.author, 'message' : desc })
            elif command == 'save':
                game.save(gamefile)
                banking.queue.put({ 'type' : 'save' })
                respondqueue.put({ 'to' : message.author, 'message' : 'Executing full save.' })
            elif command == 'stop':
                await client.logout()

                game.save(gamefile)
                banking.queue.put({ 'type' : 'save' })

                banking.stop()
                manager.stop()

                client.loop.call_soon(sys.exit, 0)
            elif command == 'kill':
                await client.logout()

                banking.stop()
                manager.stop()

                client.loop.call_soon(sys.exit, 0)
            elif command == 'roles':
                if len(cmds) > 1:
                    tgt = game.get_player(cmds[1])
                else:
                    tgt = player

                if tgt is None:
                    respondqueue.put({ 'to' : message.channel, 'message' : 'Cannot find player *{0}*'.format(cmds[1]) })
                elif len(tgt.roles) == 0:
                    respondqueue.put({ 'to' : message.channel, 'message' : '*{0}* has no roles.'.format(tgt.username) })
                else:
                    reply = '*{0}*\'s roles:'.format(tgt.username)
                    for i, r in enumerate(tgt.roles):
                        if r.term_length.total_seconds() > 0:
                            reply += '\n{0}. **{1}** [runs out {2}]'.format(i + 1, r.name.capitalize(), r.term_end.strftime('%d-%m'))
                        else:
                            reply += '\n{0}. **{1}**'.format(i + 1, r.name.capitalize())

                    respondqueue.put({ 'to' : message.channel, 'message' : reply })
            elif command == 'addrole':
                if len(cmds) < 3:
                    respondqueue.put({ 'to' : message.channel, 'message' : 'Usage: `{0}`'.format(utils.cmds[command]['example']) })
                    return

                tgt = game.get_player(cmds[1])
                role = Role(cmds[2])

                if tgt.has_role(role):
                    respondqueue.put({ 'to' : message.channel, 'message' : 'Player {0} already has role {1}'.format(tgt.username, role.name) })
                    return

                role.term_start = datetime.datetime.now()
                if len(cmds) < 4:
                    role.term_length = datetime.timedelta(days = -1)
                else:
                    try:
                        role.term_length = datetime.datetime.strptime(cmds[3], '%d-%m-%Y') - role.term_start
                    except Exception as e:
                        respondqueue.put({ 'to' : message.author, 'message' : 'Failed to interpret date format: {0}'.format(str(e)) })
                        return

                tgt.roles.append(role)
                respondqueue.put({ 'to' : message.channel, 'message' : 'Gave role {0} to player {1}'.format(role.name, tgt.username) })
            elif command == 'delrole':
                if len(cmds) < 3:
                    respondqueue.put({ 'to' : message.channel, 'message' : 'Usage: `{0}`'.format(utils.cmds[command]['example']) })
                    return

                tgt = game.get_player(cmds[1])
                role = Role(cmds[2])

                if not tgt.has_role(role):
                    respondqueue.put({ 'to' : message.channel, 'message' : 'Player {0} does not have role {1}'.format(tgt.username, role.name) })
                    return

                tgt.remove_role(role)
                respondqueue.put({ 'to' : message.channel, 'message' : 'Removed role {0} from player {1}'.format(role.name, tgt.username) })
            elif command == 'newaccount':
                if len(cmds) < 2:
                    respondqueue.put({ 'to' : message.channel, 'message' : 'Usage: `{0}`'.format(utils.cmds[command]['example']) })
                    return

                banking.queue.put({ 'type' : 'new', 'pid' : player.uid, 'name' : cmds[1], 'channel' : message.channel })
            elif command == 'balance':
                banking.queue.put({ 'type' : 'balance', 'pid' : player.uid, 'channel' : message.channel })
            elif command == 'transfer':
                if len(cmds) < 4:
                    respondqueue.put({ 'to' : message.channel, 'message' : 'Usage: `{0}`'.format(utils.cmds[command]['example']) })
                    return

                fromid = cmds[1]
                toid = cmds[2]
                amount = cmds[3]
                details = ''
                if len(cmds) > 4: details = cmds[4]

                targets = [ ]

                from_owners = banking.get_owners(fromid)
                to_owners = banking.get_owners(toid)

                if not from_owners is None:
                    for u in from_owners:
                        user = await client.get_user_info(u)
                        if not user in targets:
                            targets.append(user)

                if not to_owners is None:
                    for u in to_owners:
                        user = await client.get_user_info(u)
                        if not user in targets:
                            targets.append(user)

                banking.queue.put({ 'type' : 'transfer', 'pid' : player.uid, 'from' : fromid, 'to' : toid, 'amount' : amount, 'details' : details, 'channel' : targets })

# EOF
print('Running client...')
client.loop.create_task(responder(respondqueue))
client.run(token)