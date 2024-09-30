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

def add(client):
    @client.tree.command()
    @app_commands.describe(user='Who should I modify?',potato_count='Add to user\'s potatoes',money='Add to user\'s money')
    async def add(interaction: discord.Interaction, user: discord.User, potato_count: Optional[int], money: Optional[int]):
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
                    potato_count = 0
                else:
                    changes.append(f"Set potato count to **{functions.format_large_number(potato_count, False)}** <:tater:1287472775900037182>")
                # checks to see if user inputted money
                if money is None:
                    money = 0
                else:
                    changes.append(f"Set money to **{functions.format_large_number(money, False)}** <:coin2:1288478575825260544>")


                user_functions.add_to_user(user_id, potato_count, money)

                embed, thumbnail = await user_functions.user_stats(interaction, user, client)

                await interaction.response.send_message("\n".join(changes),embed=embed, file=thumbnail)
        else:
            await interaction.response.send_message(f"{interaction.user.mention}, you do not have permission to do this!", ephemeral=True)

# farm command
def farm(client):
    @client.tree.command()
    async def farm(interaction: discord.Interaction):
        user_id = interaction.user.id

        potatoes_ready = round(user_functions.get_potatoes_ready(user_id))
        farm_size = user_functions.get_farm_size(user_id)

        timestamp = user_functions.get_harvest_time(user_id)
        ready_timestamp = functions.create_timestamp(timestamp)

        # checking to see if potatoes have already been harvested or not
        if timestamp == 0:
            await interaction.response.send_message(f"Farm must be planted first.\nUse </plant:1288195246446084138> to plant.")
        else:
            await interaction.response.send_message(f"Farm ready: {ready_timestamp}\n{potatoes_ready}/{farm_size}")

def harvest(client):
    @client.tree.command()
    async def harvest(interaction: discord.Interaction):
        user_id = interaction.user.id
        sell_price = 1
        timestamp = user_functions.get_harvest_time(user_id)

        # checking to see if potatoes have already been harvested or not
        if timestamp == 0:
            await interaction.response.send_message(f"Potatoes already harvested!\nUse </plant:1288195246446084138> to plant again.")
        else:
            potatoes = round(user_functions.get_potatoes_ready(user_id))
            user_functions.add_to_user(user_id=user_id, potatoes=potatoes, money=0)
            await interaction.response.send_message(f"Harvested `{potatoes}` potatoes!\nFarm is now ready to plant again. Use </plant:1288195246446084138>")
            user_functions.set_harvest_time(user_id, 0)

def plant(client):
    @client.tree.command()
    async def plant(interaction: discord.Interaction):
        user_id = interaction.user.id
        # set harvest time to user's full harvest time plus the current time
        old_timestamp = user_functions.get_harvest_time(user_id)
        if old_timestamp == 0:
            timestamp = int(time.time()) + user_functions.get_total_harvest_time(user_id)
            user_functions.set_harvest_time(user_id, timestamp)

            farm_size = user_functions.get_farm_size(user_id)
            formatted_timestamp = functions.create_timestamp(timestamp)

            await interaction.response.send_message(f"Planted `{farm_size}` potatoes.\nFarm ready: {formatted_timestamp}")
        else:
            await interaction.response.send_message(f"Farm already planted.\nUse </farm:1289251039341711490> to see your farm.")