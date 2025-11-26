import sqlite3
from werkzeug.security import generate_password_hash

# connect to (or create) database
conn = sqlite3.connect("app.db")

# create cursor
cur = conn.cursor()

# drop old table if it exists (prevents mismatch of schema)
cur.execute("DROP TABLE IF EXISTS users")

# create secure users table
cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

print("Created users table.")

# insert a default admin account (optional)
admin_username = "admin"
admin_password = "AdminPassword123!"

hashed = generate_password_hash(admin_password, method="scrypt")

cur.execute(
 "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
 (admin_username, hashed, "admin")
)

print("Inserted default admin user.")
print("Username: admin")
print("Password:", admin_password)

# save changes
conn.commit()
conn.close()

print("Database setup complete.")
