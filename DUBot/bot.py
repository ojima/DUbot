'''
Created on 9 Aug 2018

@author: ojima
'''

import asyncio
import discord
import json
import shlex

import utils

from democratiauniversalis.banking import Banking
from democratiauniversalis.reminder import Reminder

with open('settings.json', 'r') as tfile:
    settings = json.load(tfile)

token = settings['token']

client = discord.Client()
banking = Banking()
reminder = Reminder()

@client.event
async def on_ready():
    print('Starting bot loops.')
    
    banking.start()
    reminder.start()
    
    print('Done')
    print('------------------')

@client.event
async def on_message(message):
    if message.author.bot: return
    
    if message.clean_content.startswith('$') or (client.user in message.mentions and '$' in message.clean_content):
        s = message.clean_content.find('$')
        cmds = shlex.split(message.clean_content[s+1:])
        
        command = utils.get_alias(cmds[0])
        
        if command is None:
            print('Failed to interpret command {0}.'.format(cmds[0]))
        else:
            print('Running command {0}.'.format(command))

client.run(token)