from werkzeug.security import generate_password_hash
from database import get_db

def add_user(username, password):
    hashed = generate_password_hash(password)
    conn = get_db()
    try:
     conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed, "user"))
     conn.commit()
     print(f"Created user {username}")
    except Exception as e:
     print("Error:", e)

if __name__ == "__main__":
 add_user("user", "password123")
