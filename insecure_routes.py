from flask import request, render_template_string, session
from app import app
from database import get_db

@app.route("/insecure/xss", methods=["GET", "POST"])
def insecure_xss():
    if request.method == "POST":
     comment = request.form["comment"]
     # reflected XSS
     return f"<h3>You wrote:</h3> {comment}"

    return """
    <h2>XSS Demo (Insecure)</h2>
    <form method="post">
        <textarea name="comment"></textarea>
        <button>Submit</button>
    </form>
    """

# insecure login - sql injection
@app.route("/insecure/login", methods=["GET", "POST"])
def insecure_login():
    if request.method == "POST":
     username = request.form["username"]
     password = request.form["password"]

        # vulnerable sql 
     query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
     conn = get_db()
     user = conn.execute(query).fetchone()

     if user:
         session["user_id"] = user["id"]
         return f"Logged in as {username} (INSECURE VERSION)"
     else:
         return "Invalid credentials (insecure)"
    
    return """
    <h2>Insecure Login</h2>
    <form method="post">
     Username: <input name="username">
     Password: <input name="password">
     <button>Login</button>
    </form>
    """
