import datetime

import pytz
import discord
from discord.ext import commands

class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
                'help': 'Shows help about the bot and its commands.'
        })

    def get_command_signature(self, command):
        return '{0.clean_prefix}{1.qualified_name} {1.signature}'.format(self, command)

    async def send_command_help(self, command):
        ctx = self.context

        embed = discord.Embed(
            title = f'{command.qualified_name.capitalize()} Command',
            colour = discord.Colour.from_rgb(80, 250, 123),
            timestamp = datetime.datetime.now(tz=pytz.timezone('Australia/NSW')
        )).set_author(
            name = ctx.me.name,
            icon_url = ctx.bot.user.avatar_url
        ).set_thumbnail(
            url = ctx.bot.user.avatar_url
        ).add_field(
            name='Description',
            value = command.help
        ).add_field(
            name='Usage',
            value = f'`{self.get_command_signature(command)}`'
        )

        await ctx.send(embed=embed)

    async def send_bot_help(self, mapping):
        ctx = self.context
        creator = ctx.bot.get_user(238899144457060352)

        embed = discord.Embed(
            description = '\n'.join((f'[Use this link to invite the bot.]({ctx.bot.invite_url})',
                                     'Use `>help <command>` for more info.',
                                     f'\n**Prefix:** `{ctx.bot.command_prefix}`')),
            colour = discord.Colour.from_rgb(80, 250, 123),
            timestamp = datetime.datetime.now(tz=pytz.timezone('Australia/NSW')
        )).set_author(
            name = ctx.me.name,
            icon_url = ctx.bot.user.avatar_url
        ).set_thumbnail(
            url = ctx.bot.user.avatar_url
        ).set_footer(
            text = f'Created by {creator}',
            icon_url = creator.avatar_url
        )

        for cog, commands in mapping.items():
            if cog and commands:
                embed.add_field(name = f'{cog.qualified_name} commands: ({len(commands)})',
                                value = ' | '.join([f'`{command.qualified_name}`' 
                                                  for command in commands]),
                                inline = False)

        await ctx.send(embed=embed)

class Information(commands.Cog):
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

def setup(bot):
    bot.add_cog(Information(bot))
