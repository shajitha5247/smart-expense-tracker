from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key_change_this"

def init_db():
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER, type TEXT, category TEXT,
                  amount REAL, date TEXT)''')
    conn.commit()
    conn.close()

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("SELECT type, category, amount, date FROM transactions WHERE user_id=?",
              (session["user_id"],))
    transactions = c.fetchall()
    c.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND type='income'",
              (session["user_id"],))
    income = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND type='expense'",
              (session["user_id"],))
    expense = c.fetchone()[0] or 0
    conn.close()
    balance = income - expense
    return render_template("dashboard.html", transactions=transactions,
                           income=income, expense=expense, balance=balance)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("expenses.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username already exists!"
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("expenses.db")
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND password=?",
                  (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session["user_id"] = user[0]
            return redirect(url_for("home"))
        return "Invalid credentials!"
    return render_template("login.html")

@app.route("/add", methods=["POST"])
def add():
    t_type = request.form["type"]
    category = request.form["category"]
    amount = request.form["amount"]
    date = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("INSERT INTO transactions (user_id, type, category, amount, date) VALUES (?, ?, ?, ?, ?)",
              (session["user_id"], t_type, category, amount, date))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)