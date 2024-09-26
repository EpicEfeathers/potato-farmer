import discord
from discord import app_commands
import sqlite3
from typing import Optional
from PIL import Image
import datetime
import time

from database import user_functions

import sys, os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

import functions



#print(f"{'\033[1m'}{'\033[91m'}WRONG FILE!")

# COMMANDS
# user command
def user(client):
    @client.tree.command()
    async def user(interaction: discord.Interaction, user: Optional[discord.User] = None):
        embed, thumbnail = await user_functions.user_stats(interaction, user, client)
        await interaction.response.send_message(embed=embed, file=thumbnail)

# balance command
def balance(client):
    @client.tree.command()
    async def balance(interaction: discord.Interaction, user: Optional[discord.User] = None):
        start = time.time()
        embed, thumbnail = await user_functions.user_stats(interaction, user, client)
        await interaction.response.send_message(embed=embed, file=thumbnail)
        print(time.time() - start)

# set command
def set(client):
    @client.tree.command()
    @app_commands.describe(user='Who should I modify?',potato_count='Set user\'s potatoes',money='Set user\'s money')
    async def set(interaction: discord.Interaction, user: discord.User, potato_count: Optional[int], money: Optional[int]):
        # converts mentioned user to their discord ID
        if interaction.user.id == 747797252105306212:
            user_id = user.id

            if potato_count is None and money is None:
                await interaction.response.send_message(":exclamation: You need to provide me something to update!",ephemeral=True)
            else:
                # gets user's data
                current_data = user_functions.get_user(user_id)

                changes = []

                # checks to see if user inputted potato_count
                if potato_count is None:
                    potato_count = current_data[0]
                else:
                    changes.append(f"Set potato count to **{functions.format_large_number(potato_count, False)}** <:tater:1287472775900037182>")
                # checks to see if user inputted money
                if money is None:
                    money = current_data[1]
                else:
                    changes.append(f"Set money to **{functions.format_large_number(money, False)}** <:coin2:1288478575825260544>")


                user_functions.set_user(user_id, potato_count, money)

                embed, thumbnail = await user_functions.user_stats(interaction, user, client)

                await interaction.response.send_message("\n".join(changes),embed=embed, file=thumbnail)
        else:
            await interaction.response.send_message(f"{interaction.user.mention}, you do not have permission to do this!", ephemeral=True)