import sqlite3
import time

def init_db():
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    # Create table with user_id (integer) and potatoes (integer)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    potatoes INTEGER,
                    money INTEGER
                );
            ''')
    c.execute('''CREATE TABLE IF NOT EXISTS farms (
                    user_id INTEGER PRIMARY KEY,
                    farm_created TIMESTAMP,
                    farm_harvestable TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            ''')
    conn.commit()
    conn.close()

def add_to_db(user_id, potatoes):
    conn = sqlite3.connect('database/users.db')
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

def get_potatoes(user_id):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT potatoes FROM users WHERE user_id = ?", (user_id,))

    row = c.fetchone()
    conn.close()

    if row:
        return row[0]  # Return the potato count
    else:
        return "User not found!"

def farm_creation_date(user_id):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT farm_created FROM farms WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if row:
        return row
    else:
        timestamp = int(time.time())

        # Insert a new user with the potato count
        c.execute("INSERT INTO farms (user_id, farm_created) VALUES (?, ?)", (user_id, timestamp))

        conn.commit()
        conn.close()
        return timestamp
    



def get_harvest_time(user_id):
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()

    c.execute("SELECT farm_harvestable FROM farms WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    return row[0]

def set_harvest_time(user_id, timestamp):
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
        print("Updated")
        new_timestamp = int(time.time() + (60 * add_minutes))
        set_harvest_time(user_id, new_timestamp)
        return new_timestamp
    else:
        print("Did not update")
        return timestamp

'''print(farm_creation_date(747797252105306212)[0])
print(time.time())'''

timestamp = check_harvest_time(747797252105306212, 0.1)
print(f"Timestamp: {timestamp}")
#print(harvest_time(747797252105306212, int(time.time() + 60 * 5)))
print(f"Current time: {int(time.time())}\nSet time: {int(time.time() + 6)}")
