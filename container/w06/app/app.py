from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    version = os.getenv("APP_VERSION", "dev")
    return f"Hello Docker - version: {version}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
