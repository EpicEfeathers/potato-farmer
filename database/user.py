import discord
from discord import app_commands
import sqlite3
from typing import Optional
from PIL import Image
import datetime

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'functions')))
import functions



#print(f"{'\033[1m'}{'\033[91m'}WRONG FILE!")

# obtains dominant color of image (resizing to 1x1 using PIL)
class Database:
    '''def get_dominant_color(self, url):
        response = requests.get(url)
        im = Image.open(BytesIO(response.content))

        im1 = im.resize((1,1))
        color = im1.getpixel((0,0))
        color = (color[0] << 16) + (color[1] << 8) + color[2]
        return color'''

    # initializes database (shouldn't be needed anymore)
    def init_db(self):
        conn = sqlite3.connect('database/users.db')
        c = conn.cursor()
        # creates table with user_id (discord ID), potatoes (integer), money (integer)
        c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY, 
                    potatoes INTEGER DEFAULT 0, 
                    money INTEGER DEFAULT 0
                )
            ''')
        conn.commit()
        conn.close()

    # gets user information using their discord ID
    def get_user(self, user_id):
        conn = sqlite3.connect('database/users.db')
        c = conn.cursor()

        c.execute("SELECT potatoes, money FROM users WHERE user_id = ?", (user_id,))

        result = c.fetchone()
        conn.close()

        if result:
            potatoes, money = result  # Return the potato count
            return potatoes, money
        else:
            self.set_user(user_id, 0, 0)
            return 0, 0

    # sets user information using their discord ID
    def set_user(self, user_id, potatoes, money):
        conn = sqlite3.connect('database/users.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()

        if row:
            # Update the potatoes count if the user exists
            c.execute("UPDATE users SET potatoes = ?, money = ? WHERE user_id = ?", (potatoes, money, user_id))
        else:
            # Insert a new user with the potato count
            c.execute("INSERT INTO users (user_id, potatoes, money) VALUES (?, ?, ?)", (user_id, potatoes, money))
        
        conn.commit()
        conn.close()

    # displays the user's stats
    async def user_stats(self, interaction, user, client):

        if user:
            user_id = user.id
        else:
            user_id = interaction.user.id

        user = await client.fetch_user(user_id)
        if user.accent_color:
            color = user.accent_color
        else:
            color = discord.Color(functions.get_dominant_color(user.avatar.url))
        
        potatoes, money = self.get_user(user_id)

        embed = discord.Embed(title=f"<:tater:1287472775900037182> {functions.format_large_number(potatoes, True)}\n<:coin2:1288478575825260544> {money}", color=color, timestamp=datetime.datetime.now())
        
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', 'logo.png'))
        print(image_path)
        picture = discord.File(image_path, filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")

        embed.set_author(name=f"{user.display_name}'s Farm", icon_url=user.avatar.url)

        return embed, picture



# COMMANDS
# user command
def user(client):
    @client.tree.command()
    async def user(interaction: discord.Interaction, user: Optional[discord.User] = None):
        embed, thumbnail = await db.user_stats(interaction, user, client)
        await interaction.response.send_message(embed=embed, file=thumbnail)

# balance command
def balance(client):
    @client.tree.command()
    async def balance(interaction: discord.Interaction, user: Optional[discord.User] = None):
        embed, thumbnail = await db.user_stats(interaction, user, client)
        await interaction.response.send_message(embed=embed, file=thumbnail)

# set command
def set(client):
    @client.tree.command()
    @app_commands.describe(user='Who should I modify?',potato_count='Set user\'s potatoes',money='Set user\'s money')
    async def set(interaction: discord.Interaction, user: discord.User, potato_count: Optional[int], money: Optional[int]):
        # converts mentioned user to their discord ID
        user_id = user.id


        if potato_count is None and money is None:
            await interaction.response.send_message(":exclamation: You need to provide me something to update!",ephemeral=True)
        else:
            # gets user's data
            current_data = db.get_user(user_id)

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


            db.set_user(user_id, potato_count, money)

            embed, thumbnail = await db.user_stats(interaction, user, client)

            await interaction.response.send_message("\n".join(changes),embed=embed, file=thumbnail)
            #await interaction.response.send_message(embed=db.user_stats(user_id))


db = Database()
db.init_db()