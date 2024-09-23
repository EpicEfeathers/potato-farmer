import sqlite3

def init_db():
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    # Create table with user_id (integer) and potatoes (integer)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, potatoes INTEGER)''')
    conn.commit()
    conn.close()

def add_to_db(user_id, potatoes):
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

def get_potatoes(user_id):
    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    c.execute("SELECT potatoes FROM users WHERE user_id = ?", (user_id,))

    row = c.fetchone()
    conn.close()

    if row:
        return row[0]  # Return the potato count
    else:
        return "User not found!"