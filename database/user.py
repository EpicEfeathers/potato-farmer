import discord
from discord import app_commands
import sqlite3
from typing import Optional


#print(f"{'\033[1m'}{'\033[91m'}WRONG FILE!")

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


def user(client):
    @client.tree.command()
    async def user(interaction: discord.Interaction, user: Optional[discord.User]):
        if user:
            user = user.id
        else:
            user = interaction.user.id
        potatoes = get_potatoes(user)
        await interaction.response.send_message(potatoes)


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