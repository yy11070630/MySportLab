import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

#USER TABLE <LOGIN AND REGISTER>#

cursor.execute("""
CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
                #AUTO INCREASE123/
conn.commit()

#PROFILE TABLE#

cursor.execute("""
CREATE TABLE IF NOT EXISTS Profile(
    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTERGER UNIQUE,
    height REAL,
    weight REAL,
    preference  TEXT,
    FOREIGN KEY (user_id)REFERENCE User (user_id)
)
""")    

conn.commit



