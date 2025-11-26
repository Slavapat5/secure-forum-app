from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
import bleach

secure = Blueprint("secure", __name__, template_folder="templates")

# helper – current logged in user
def current_user():
    uid = session.get("user_id")
    if not uid:
     return None

    conn = get_db()
    user = conn.execute(
     "SELECT id, username, role FROM users WHERE id=?",
     (uid,)
    ).fetchone()
    return user

# register
@secure.route("/secure/register", methods=["GET", "POST"])
def secure_register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password required", "error")
            return redirect(url_for("secure.secure_register"))

        hashed = generate_password_hash(password)
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hashed, "user")
            )
            conn.commit()
            flash("Registered successfully!", "success")
            return redirect(url_for("secure.secure_login"))
        except:
            flash("Username already exists!", "error")
            return redirect(url_for("secure.secure_register"))

    return render_template("secure_register.html")



# login
@secure.route("/secure/login", methods=["GET", "POST"])
def secure_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password")

        conn = get_db()
        user = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("secure.secure_dashboard"))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for("secure.secure_login"))

    return render_template("secure_login.html")


# dashboard
@secure.route("/secure/dashboard")
def secure_dashboard():
    user = current_user()
    if not user:
     return redirect(url_for("secure.secure_login"))

    conn = get_db()
    comments = conn.execute("""
        SELECT m.id, m.content, u.username
        FROM messages m
        JOIN users u ON u.id = m.user_id
        ORDER BY m.id DESC
    """).fetchall()

    return render_template("secure_dashboard.html", user=user, comments=comments)



# comment (protected and XSS filtered)
@secure.route("/secure/comment", methods=["POST"])
def secure_comment():
    user = current_user()
    if not user:
     return redirect(url_for("secure.secure_login"))

    raw = request.form.get("comment", "")
    safe = bleach.clean(raw, tags=["b","i","u","em","strong","p","br"], strip=True)

    conn = get_db()
    conn.execute(
        "INSERT INTO messages (content, user_id) VALUES (?, ?)",
        (safe, user["id"])
    )
    conn.commit()

    return redirect(url_for("secure.secure_dashboard"))


# search (SQL injection-safe)

@secure.route("/secure/search")
def secure_search():
    q = request.args.get("q", "").strip()
    conn = get_db()
    rows = conn.execute(
     "SELECT * FROM messages WHERE content LIKE ?",
      (f"%{q}%",)
    ).fetchall()

    return render_template("secure_search.html", q=q, rows=rows)

# logout
@secure.route("/secure/logout")
def logout():
    session.clear()
    return redirect(url_for("secure.secure_login"))