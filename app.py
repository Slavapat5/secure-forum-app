from flask import Flask, render_template
from secure_routes import secure
from database import init_db

app = Flask(__name__)
app.secret_key = "Secret-Key"   

# registering blueprint
app.register_blueprint(secure)

init_db()

@app.route("/")
def home():
 return render_template("index.html")

if __name__ == "__main__":
 app.run(debug=True)

app.register_blueprint(secure)