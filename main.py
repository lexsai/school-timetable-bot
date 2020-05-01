import os
import traceback

import jishaku
import discord
from discord.ext import commands

import custom_classes as cc

bot = cc.NormoBot(command_prefix='>')

@bot.event
async def on_ready():
    print('-')
    print(f'Logged in as "{bot.user.name}" - User ID : {bot.user.id}')
    print(f'Command Prefix: {bot.command_prefix}')
    print('Guilds:')
    print('\n'.join([f'"{guild.name}"' for guild in bot.guilds]))
    print('-')	

if __name__ == '__main__':
    #bot.run('Njk3Mjk2NzcxMTIyMDY5NTE1.Xo1Sww.bjFBDvKhOEF_YY2sPFsaIC8WeOk')
    bot.run('Njk3NTgwODI3OTY1NTIxOTQw.Xo5W-A.at8TJGL9KtEZmS0i6Q0jEMZAkHM')



