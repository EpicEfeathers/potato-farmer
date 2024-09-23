# Discord imports
import discord
from discord import app_commands
from discord.ext import commands

import sqlite3

import logging

# other files
import misc
from database import database_functions, user

#handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

activity = discord.Activity(name = "my activity", type = discord.ActivityType.custom, state = "Farming taters! 🥔")

#bot = commands.Bot(command_prefix="",intents=intents,activity=activity)

MY_GUILD = discord.Object(id=915714438273826858)

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, activity: discord.Activity):
        super().__init__(intents=intents,activity=activity)

        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()
client = MyClient(intents=intents,activity=activity)

@client.event
async def on_ready():
    print(f'Successfully logged in as {'\033[1m'}{client.user}')




@client.tree.command()
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention}, bot is up and running!", ephemeral=True)

#ping command
misc.ping(client)

#user commands
user.user(client)
user.set(client)


# CHANGE SECRET ON RELEASE
client.run('client secret')#, log_handler = handler)