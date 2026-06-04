from flask import Flask
import os
import psycopg2

app = Flask(__name__)

@app.route("/")
def home():
    return "Docker Compose Lab"

@app.route("/healthz")
def healthz():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dbname=os.getenv("DB_NAME")
        )
        conn.close()
        return "OK - DB connected", 200
    except Exception as e:
        return f"ERROR: {e}", 500

app.run(host="0.0.0.0", port=8080)

