'''
Created on 9 Aug 2018

@author: ojima
'''

import asyncio
import json
import queue
import shlex

import discord

from democratiauniversalis.banking import Banking
from democratiauniversalis.metagame.game import Game
from democratiauniversalis.rolemanager import RoleManager
import multiprocessing as Mp
import utils


async def responder(queue):
    await client.wait_until_ready()
    
    print('Starting response loop.')
    
    while True:
        got_reply = False
        while not queue.empty():
            event = queue.get()
            await client.send_message(event['to'], event['message'])
            got_reply = True
            
            print('Sent message {0} to {1}'.format(event['message'], event['to']))
        
        if not got_reply:
            await asyncio.sleep(1)

with open('settings.json', 'r') as tfile:
    settings = json.load(tfile)

token = settings['token']
gamefile = settings['gamefile']
owners = settings['owners']

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
                desc = utils.get_help(command, game.is_owner(player))
                respondqueue.put({ 'to' : message.channel, 'message' : desc })

print('Running client...')
client.loop.create_task(responder(respondqueue))
client.run(token)