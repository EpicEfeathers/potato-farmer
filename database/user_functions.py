import sqlite3
import time, datetime
import discord

import sys, os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

import functions

# initializes database (shouldn't be needed anymore)
def init_db():
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
def get_user( user_id):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT potatoes, money FROM users WHERE user_id = ?", (user_id,))

    result = c.fetchone()
    conn.close()

    if result:
        potatoes, money = result  # Return the potato count
        return potatoes, money
    else:
        set_user(user_id, 0, 0)
        return 0, 0

# sets user information using their discord ID
def set_user( user_id, potatoes, money):
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

# gets the user's farm creation date
def farm_creation_date(user_id):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT farm_created FROM farms WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if row:
        return row[0]
    else:
        timestamp = int(time.time())

        # Insert a new user with the potato count
        c.execute("INSERT INTO farms (user_id, farm_created) VALUES (?, ?)", (user_id, timestamp))

        conn.commit()
        conn.close()
        return timestamp

# displays the user's stats
async def user_stats( interaction, user, client):
    # checks to see if user passed in another user
    if user:
        user_id = user.id
    else:
        user_id = interaction.user.id

    # Embed highlight based on profile picture (or banner color, if set)
    user = await client.fetch_user(user_id)
    if user.accent_color:
        color = user.accent_color
    else:
        color = discord.Color(functions.get_dominant_color(user.avatar.url))
    
    potatoes, money = get_user(user_id)
    creation_date = farm_creation_date(user_id)

    # Created visual embed
    embed = discord.Embed(title=f"Balance\n<:tater:1287472775900037182> {functions.format_large_number(potatoes, True)}\n<:coin2:1288478575825260544> {money}", color=color, timestamp=datetime.datetime.now())
    
    image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', 'logo.png'))
    picture = discord.File(image_path, filename="logo.png")
    embed.set_thumbnail(url="attachment://logo.png")
    embed.set_author(name=f"{user.display_name}'s Farm", icon_url=user.avatar.url)


    embed.set_footer(text=f"Farm created on {functions.timestamp_format(creation_date, 1)}")

    return embed, picture



# gets time when the harvest is ready
def get_harvest_time( user_id):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT farm_harvestable FROM farms WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    return row[0]

# sets time when the harvest is ready
def set_harvest_time( user_id, timestamp):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT farm_harvestable FROM farms WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    c.execute("UPDATE farms SET farm_harvestable = ? WHERE user_id = ? ", (timestamp, user_id))

    conn.commit()
    conn.close()

def check_harvest_time(user_id, add_minutes):
    timestamp = get_harvest_time(user_id)

    if int(time.time()) > timestamp:
        new_timestamp = int(time.time() + (60 * add_minutes))
        set_harvest_time(user_id, new_timestamp)
        return new_timestamp
    else:
        return timestamp