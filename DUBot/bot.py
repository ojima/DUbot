'''
Created on 9 Aug 2018

@author: ojima
'''

import asyncio
import discord
import sys

from democratiauniversalis.banking import Banking
from democratiauniversalis.reminder import Reminder

token = 'NDYxNTgxMjA4NzkxNTQ3OTA3.DifrTg.6uzbfDDYl8bqMaC7dHeVrnBEkl0'

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
    
    if message.clean_content.startswith('$') or (message.mention)

client.run(token)