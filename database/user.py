import discord
from discord import app_commands
import sqlite3
from typing import Optional
from PIL import Image
import requests
from io import BytesIO


#print(f"{'\033[1m'}{'\033[91m'}WRONG FILE!")

# obtains dominant color of image (resizing to 1x1 using PIL)
class Database:
    def get_dominant_color(self, url):
        response = requests.get(url)
        im = Image.open(BytesIO(response.content))

        im1 = im.resize((1,1))
        color = im1.getpixel((0,0))
        color = (color[0] << 16) + (color[1] << 8) + color[2]
        return color

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
        print(f"User stuff: {user}")
        if user.accent_color:
            color = user.accent_color
        else:
            color = discord.Color(self.get_dominant_color(user.avatar.url))
        
        potatoes, money = self.get_user(user_id)

        embed = discord.Embed(title=f"<:tater:1287472775900037182> {potatoes}\n<:coin1:1288225115368067073> {money}\n<:coin2:1288225986663682202> {money}", color=color)
        embed.set_author(name=f"{user.display_name}'s Farm", icon_url='https://cdn.discordapp.com/avatars/747797252105306212/5b95dcc9e05083615df5525de9f6059d.png?size=1024')

        return embed



# COMMANDS
# user command
def user(client):
    @client.tree.command()
    async def user(interaction: discord.Interaction, user: Optional[discord.User] = None):
        embed = await db.user_stats(interaction, user, client)
        await interaction.response.send_message(embed=embed)

# balance command
def balance(client):
    @client.tree.command()
    async def balance(interaction: discord.Interaction, user: Optional[discord.User] = None):
        embed = await db.user_stats(interaction, user, client)
        await interaction.response.send_message(embed=embed)

# set command
def set(client):
    @client.tree.command()
    @app_commands.describe(potato_count='Set user\'s potatoes')
    async def set(interaction: discord.Interaction, user: Optional[discord.User], potato_count: int):
        if user:
            user = user.id
        else:
            user = interaction.user.id
        db.set_user(user, potato_count, 0)
        print(db.get_user(interaction.user.id))
        await interaction.response.send_message(f"Set potato count to **{potato_count}**")


db = Database()
db.init_db()