from flask import Flask, render_template, session
from dotenv import load_dotenv
import os
from routes.auth import auth_bp
from routes.entries import entries_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(entries_bp)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    # Check if user is authenticated
    if 'user_id' not in session:
        return render_template("index.html")  # Will show auth screen
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)