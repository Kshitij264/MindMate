import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('mindmate.db')
    c = conn.cursor()

    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 email TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL
    )''')

    # Create chat_history table
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER NOT NULL,
                 message TEXT NOT NULL,
                 response TEXT NOT NULL,
                 timestamp TEXT NOT NULL,
                 FOREIGN KEY (user_id) REFERENCES users(id)
    )''')

    conn.commit()
    conn.close()

def register_user(name, email, password):
    try:
        conn = sqlite3.connect('mindmate.db')
        c = conn.cursor()
        hashed_pw = generate_password_hash(password)
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_pw))
        conn.commit()

        # Return the new user's ID
        user_id = c.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None  # Email already exists
    finally:
        conn.close()

def validate_login(email, password):
    conn = sqlite3.connect('mindmate.db')
    c = conn.cursor()
    c.execute("SELECT id, name, password FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user[2], password):
        return (user[0], user[1])  # Return (user_id, name)
    return None
