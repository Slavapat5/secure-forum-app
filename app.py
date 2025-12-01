from flask import Flask, render_template
from secure_routes import secure
from database import init_db

app = Flask(__name__, template_folder="templates")
app.secret_key = "super-secret-key-123"  # hard-coded 

init_db()

# register blueprint
app.register_blueprint(secure)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
