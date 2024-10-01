import sqlite3
import time, datetime
import discord

import sys, os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

import functions

BASE_HARVEST_TIME = 30
BASE_FARM_SIZE = 20

# initializes database (shouldn't be needed anymore)
def init_db():
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    # creates tables
    c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY, 
                potatoes INTEGER DEFAULT 0, 
                money INTEGER DEFAULT 0,
                message_count INTEGER DEFAULT 0
            )
        ''')
    c.execute('''CREATE TABLE IF NOT EXISTS farms (
                    user_id INTEGER PRIMARY KEY,
                    farm_created TIMESTAMP,
                    total_harvest_time TIMESTAMP DEFAULT 30,
                    harvest_time INTEGER DEFAUL 0,
                    farm_size INTEGER DEFAULT 20,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            ''')
    conn.commit()
    conn.close()

# gets user information using their discord ID
def get_user(user_id):
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
def set_user(user_id, potatoes, money):
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

def add_to_user(user_id, potatoes, money):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if row:
        # Update the potatoes count if the user exists
        c.execute("UPDATE users SET potatoes = potatoes + ?, money = money + ? WHERE user_id = ?", (potatoes, money, user_id))
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
        creation_date = row[0]
    else:
        timestamp = int(time.time())

        # Insert a new user with the potato count
        c.execute("INSERT INTO farms (user_id, farm_created) VALUES (?, ?)", (user_id, timestamp))

        conn.commit()
        creation_date = timestamp
    conn.close()
    return creation_date

# displays the user's stats
async def user_stats(interaction, user, client):
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
    embed = discord.Embed(title=f"Balance\n<:tater:1287472775900037182> {functions.format_large_number(potatoes, True)}\n<:coin2:1288478575825260544> {functions.format_large_number(money, True)}", color=color, timestamp=datetime.datetime.now())
    
    image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', 'logo.png'))
    picture = discord.File(image_path, filename="logo.png")
    embed.set_thumbnail(url="attachment://logo.png")
    embed.set_author(name=f"{user.display_name}'s Farm", icon_url=user.avatar.url)


    embed.set_footer(text=f"Farm created on {functions.timestamp_format(creation_date, 1)}")

    return embed, picture


# gets length of time full harvest will take (in seconds)
def get_total_harvest_time(user_id):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT total_harvest_time FROM farms WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if row and row[0] is not None:
        total_harvest_time = row[0]
    else:
        if row:
            c.execute("UPDATE farms SET total_harvest_time = ? WHERE user_id = ?", (BASE_HARVEST_TIME, user_id))
        else:
            c.execute("INSERT INTO farms (user_id, harvest_time) VALUES (?,?)", (user_id, BASE_HARVEST_TIME,))
        conn.commit()
        total_harvest_time = BASE_HARVEST_TIME
    conn.close()
    return total_harvest_time

# sets length of time full harvest will take (in seconds)
def set_total_harvest_time(user_id, total_harvest_time):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT total_harvest_time FROM farms WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if row:
        # Update the potatoes count if the user exists
        c.execute("UPDATE farms SET total_harvest_time = ? WHERE user_id = ?", (total_harvest_time, user_id))
    else:
        # Insert a new user with the potato count
        c.execute("INSERT INTO farms (user_id, total_harvest_time) VALUES (?, ?)", (user_id, total_harvest_time))
    
    conn.commit()
    conn.close()

# gets timestamp (UNIX time?) that full harvest will be ready at
def get_harvest_time(user_id):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT harvest_time FROM farms WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if row:
        conn.close()
        return row[0]
    else:
        c.execute("INSERT INTO farms (user_id, harvest_time) VALUES (?,?)", (user_id, 0))
        conn.commit()
        conn.close()

# sets timestamp (UNIX time?) that full harvest will be ready at
def set_harvest_time(user_id, timestamp):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT harvest_time FROM farms WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if row:
        # Update the potatoes count if the user exists
        c.execute("UPDATE farms SET harvest_time = ? WHERE user_id = ?", (timestamp, user_id))
    else:
        # Insert a new user with the potato count
        c.execute("INSERT INTO farms (user_id, harvest_time) VALUES (?, ?)", (user_id, timestamp))
    
    conn.commit()
    conn.close()

# gets user's farm size
def get_farm_size(user_id):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT farm_size FROM farms WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if row and row[0] is not None:
        farm_size = row[0]
    else:
        if row:
            c.execute("UPDATE farms SET farm_size = ? WHERE user_id = ?", (BASE_FARM_SIZE, user_id))
        else:
            c.execute("INSERT INTO farms (user_id, farm_size) VALUES (?, ?)", (user_id, BASE_FARM_SIZE))
        farm_size = BASE_FARM_SIZE

    conn.close()
    return farm_size

# sets user's farm size
def set_farm_size(user_id, farm_size):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT farm_size FROM farms WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if row:
        # Update the potatoes count if the user exists
        c.execute("UPDATE farms SET farm_size = ? WHERE user_id = ?", (farm_size, user_id))
    else:
        # Insert a new user with the potato count
        c.execute("INSERT INTO farms (user_id, farm_size) VALUES (?, ?)", (user_id, farm_size))
    
    conn.commit()
    conn.close()


# gets user's amount of potatoes ready
def get_potatoes_ready(user_id):
    total_harvest_time = get_total_harvest_time(user_id)
    harvest_time = get_harvest_time(user_id)

    current_time = int(time.time())
    farm_size = get_farm_size(user_id)

    equation = (total_harvest_time - (harvest_time - current_time)) / total_harvest_time * farm_size
    if equation > farm_size:
        equation = farm_size
    return equation



def get_user_message_count(user_id):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT message_count FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    conn.close()
    return row[0]

def add_user_message_count(user_id):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    c.execute("UPDATE users SET message_count = message_count + 1 WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()

print(get_user_message_count(747797252105306212))
'''set_harvest_time(747797252105306212, int(time.time()) + 30)
potatoes_ready = round(get_potatoes_ready(747797252105306212))
farm_size = get_farm_size(747797252105306212)
print(f"{potatoes_ready}/{farm_size}")
print(get_total_harvest_time(747797252105306212))'''