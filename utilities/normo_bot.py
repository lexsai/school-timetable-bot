import os
import traceback

import jishaku
import discord
from discord.ext import commands

import utilities as util

class NormoBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invite_url = 'https://discordapp.com/api/oauth2/authorize?client_id=697296771122069515&permissions=8&scope=bot'

        extensions = sorted([f"cogs.{os.path.splitext(cog)[0]}" 
                             for cog in os.listdir("cogs") 
                             if os.path.splitext(cog)[1] == '.py'])
    
        #self.database = util.Database(self)

        self.load_extensions(extensions + ["jishaku"])
        
    def load_extensions(self, extensions):
        print("Loading extensions:")

        for extension in extensions:
            try:
                self.load_extension(extension)
                print(f"\"{extension}\" loaded. ({extensions.index(extension)+1}/{len(extensions)})")
            except:
                print(f"Failed to load extension {extension}.")
                traceback.print_exc()
