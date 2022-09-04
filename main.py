import os
import traceback

import jishaku
import discord
from discord.ext import commands

from utilities import NormoBot

bot = NormoBot(command_prefix='>')

@bot.event
async def on_ready():
    print('-')
    print(f'Logged in as "{bot.user.name}" - User ID : {bot.user.id}')
    print(f'Command Prefix: {bot.command_prefix}')
    print('Guilds:')
    print('\n'.join([f'"{guild.name}"' for guild in bot.guilds]))
    print('-')	

if __name__ == '__main__':
    bot.run('...')
