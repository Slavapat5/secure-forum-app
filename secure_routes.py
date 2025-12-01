from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from database import get_db


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

# INSECURE REGISTER
@secure.route("/secure/register", methods=["GET", "POST"])
def secure_register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password required", "error")
            return redirect(url_for("secure.secure_register"))

        conn = get_db()
        try:
            # insecure - store plaintext password
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password, "user")
            )
            conn.commit()
            flash("Registered (INSECURE – plaintext password).", "success")
            return redirect(url_for("secure.secure_login"))
        except Exception:
            flash("Username already exists or registration failed.", "error")
            return redirect(url_for("secure.secure_register"))

    return render_template("secure_register.html")




# insecure login – sql injection
@secure.route("/secure/login", methods=["GET", "POST"])
def secure_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password")

        conn = get_db()

        # insecure SQL injection using string concatenation
        query = (
            f"SELECT id, username, password_hash "
            f"FROM users WHERE username = '{username}' "
            f"AND password_hash = '{password}'"
        )
        print("INSECURE LOGIN QUERY:", query) 

        user = conn.execute(query).fetchone()

        if user:
            session.clear()
            session["user_id"] = user["id"]
            flash("Logged in (INSECURE – SQLi possible).", "success")
            return redirect(url_for("secure.secure_dashboard"))
        else:
            flash("Invalid username or password (insecure login).", "error")
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



# insecure comment – STORED XSS
@secure.route("/secure/comment", methods=["POST"])
def secure_comment():
    user = current_user()
    if not user:
        return redirect(url_for("secure.secure_login"))

    # insecure - no sanitisation
    raw = request.form.get("comment", "")

    conn = get_db()
    conn.execute(
        "INSERT INTO messages (content, user_id) VALUES (?, ?)",
        (raw, user["id"])
    )
    conn.commit()

    flash("Comment posted (INSECURE – stored XSS possible).", "success")
    return redirect(url_for("secure.secure_dashboard"))


# search (SQL injection-safe)
@secure.route("/secure/search")
def secure_search():
    q = request.args.get("q", "").strip()
    conn = get_db()

    # insecure direct string concatenation
    sql = f"SELECT * FROM messages WHERE content LIKE '%{q}%'"
    print("INSECURE SEARCH SQL:", sql)

    rows = conn.execute(sql).fetchall()

    return render_template("secure_search.html", q=q, rows=rows)


# logout
@secure.route("/secure/logout")
def logout():
    session.clear()
    return redirect(url_for("secure.secure_login"))