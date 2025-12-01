from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect, generate_csrf
import logging
from logging.handlers import RotatingFileHandler

from secure_routes import secure
from database import init_db

app = Flask(__name__, template_folder="templates")

# secret key
app.config["SECRET_KEY"] = "secretkey123"

# session security
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # True if HTTPS

# CSRF protection
csrf = CSRFProtect(app)

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

init_db()

app.register_blueprint(secure)

# logging & monitoring
handler = RotatingFileHandler("app_secure.log", maxBytes=2_000_000, backupCount=3)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s [in %(pathname)s:%(lineno)d]"
)
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
app.logger.info("Secure app starting up")

# security headers
@app.after_request
def set_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:;"
    )
    return response

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
