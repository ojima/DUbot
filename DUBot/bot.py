'''
Created on 9 Aug 2018

@author: ojima
'''

import asyncio
import json
import shlex

import discord

from democratiauniversalis.banking import Banking
from democratiauniversalis.metagame.game import Game
from democratiauniversalis.rolemanager import RoleManager
import multiprocessing as Mp
import utils

def get_setting(settings, tag):
    if not tag in settings:
        raise KeyError('Cannot get setting {0}: non-existent tag.')
    
    return settings[tag]

async def responder(queue):
    await client.wait_until_ready()
    
    print('Starting response loop.')
    
    while True:
        got_reply = False
        while not queue.empty():
            event = queue.get()
            # TODO: nicely split messages into messages of no more than 2000 chars so that discord doesn't refuse too long messages.
            await client.send_message(event['to'], event['message'])
            got_reply = True
        
        if not got_reply:
            await asyncio.sleep(1)

with open('settings.json', 'r') as tfile:
    settings = json.load(tfile)

token = get_setting(settings, 'token')
gamefile = get_setting(settings, 'gamefile')
owners = get_setting(settings, 'owners')

respondqueue = Mp.Queue()

client = discord.Client()

game = Game()
for o in owners:
    game.add_owner(o)

banking = Banking(respondqueue)
manager = RoleManager(game, respondqueue)

print('Initialized manager runnables.')

@client.event
async def on_ready():
    print('Starting bot loops.')

    game.load(gamefile)
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

    if message.clean_content.startswith('$') or (client.user in message.mentions and '$' in message.clean_content):
        s = message.clean_content.find('$')
        cmds = shlex.split(message.clean_content[s + 1:])

        command = utils.get_alias(cmds[0])

        if command is None:
            print('Failed to interpret command {0}.'.format(cmds[0]))
        else:
            print('Running command {0}.'.format(command))

            if command == 'help':
                if len(cmds) > 1:
                    cmd = utils.get_alias(cmds[1])
                    desc = utils.get_help(cmd, game.is_owner(player))
                else:
                    desc = utils.get_help(command, game.is_owner(player))
                respondqueue.put({ 'to' : message.channel, 'message' : desc })
            elif command == 'all':
                desc = utils.get_all(game.is_owner(player))
                respondqueue.put({ 'to' : message.author, 'message' : desc })

print('Running client...')
client.loop.create_task(responder(respondqueue))
client.run(token)