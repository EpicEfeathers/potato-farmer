import discord
from discord import app_commands
import sqlite3
from typing import Optional
from PIL import Image
import requests
from io import BytesIO


#print(f"{'\033[1m'}{'\033[91m'}WRONG FILE!")

def get_dominant_color(url):
    response = requests.get(url)
    im = Image.open(BytesIO(response.content))

    im1 = im.resize((1,1))
    color = im1.getpixel((0,0))
    color = (color[0] << 16) + (color[1] << 8) + color[2]
    return color

def init_db():
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    # Create table with user_id (integer) and potatoes (integer)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, potatoes INTEGER)''')
    conn.commit()
    conn.close()

def get_potatoes(user_id):
    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    c.execute("SELECT potatoes FROM users WHERE user_id = ?", (user_id,))

    row = c.fetchone()
    conn.close()

    if row:
        return row[0]  # Return the potato count
    else:
        set_potatoes(user_id, 0)
        return 0
    
def set_potatoes(user_id, potatoes):
    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if row:
        # Update the potatoes count if the user exists
        c.execute("UPDATE users SET potatoes = ? WHERE user_id = ?", (potatoes, user_id))
    else:
        # Insert a new user with the potato count
        c.execute("INSERT INTO users (user_id, potatoes) VALUES (?, ?)", (user_id, potatoes))
    
    conn.commit()
    conn.close()

async def user_stats(interaction, user, client):

    if user:
        user_id = user.id
    else:
        user_id = interaction.user.id

    user = await client.fetch_user(user_id)
    print(f"User stuff: {user}")
    if user.accent_color:
        color = user.accent_color
    else:
        color = discord.Color(get_dominant_color(user.avatar.url))
    
    potatoes = get_potatoes(user_id)

    embed = discord.Embed(title="Title", description=f"<:tater:1287472775900037182>: {potatoes}", color=color)
    embed.set_author(name=f"{user.display_name}'s Farm", icon_url='https://cdn.discordapp.com/avatars/747797252105306212/5b95dcc9e05083615df5525de9f6059d.png?size=1024')

    return embed

def user(client):
    @client.tree.command()
    async def user(interaction: discord.Interaction, user: Optional[discord.User] = None):
        embed = await user_stats(interaction, user, client)
        await interaction.response.send_message(embed=embed)

def balance(client):
    @client.tree.command()
    async def balance(interaction: discord.Interaction, user: Optional[discord.User] = None):
        embed = await user_stats(interaction, user, client)
        await interaction.response.send_message(embed=embed)


def set(client):
    @client.tree.command()
    @app_commands.describe(potato_count='Set user\'s potatoes')
    async def set(interaction: discord.Interaction, user: Optional[discord.User], potato_count: int):
        if user:
            user = user.id
        else:
            user = interaction.user.id
        set_potatoes(user, potato_count)
        print(get_potatoes(interaction.user.id))
        await interaction.response.send_message(f"Set potato count to **{potato_count}**")