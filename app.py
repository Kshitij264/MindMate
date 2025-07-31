from dotenv import load_dotenv
import os
import sqlite3
from datetime import timedelta, datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mail import Mail, Message
from chatbot import get_response, get_last_polarity
from database import init_db, register_user, validate_login

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.permanent_session_lifetime = timedelta(minutes=30)

# Mail configuration
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT"))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

mail = Mail(app)

# Initialize the database on startup
init_db()

# Helper: Save chat to DB
def save_chat_to_db(user_id, message, response):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        '''INSERT INTO chat_history (user_id, message, response, timestamp)
           VALUES (?, ?, ?, ?)''',
        (user_id, message, response, datetime.now())
    )
    conn.commit()
    conn.close()

@app.before_request
def before_request():
    if request.endpoint == 'welcome':
        session['mood_history'] = []

@app.route("/")  # Welcome Page
def welcome():
    return render_template("welcome.html")

@app.route("/menu")  # Menu Page
def menu():
    if 'user' not in session:
        return redirect(url_for('welcome'))
    return render_template("menu.html", user=session.get('user'))

@app.route("/home")  # Chat Page
def home():
    if 'user_name' not in session:
        return redirect(url_for('welcome'))
    return render_template("index.html", user_name=session.get('user_name'))

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form["message"]
    bot_reply = get_response(user_message)
    polarity = get_last_polarity()

    user_id = session.get("user_id")
    if user_id:
        save_chat_to_db(user_id, user_message, bot_reply)
        print("✅ Chat saved to DB")
    else:
        print("⚠️ User not logged in, chat not saved.")

    return jsonify({"reply": bot_reply, "polarity": polarity})

@app.route("/chat-history", methods=["GET"])
def chat_history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify([])

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        "SELECT message, response, timestamp FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10",
        (user_id,)
    )
    rows = c.fetchall()
    conn.close()

    history = [
        {"message": row[0], "response": row[1], "timestamp": row[2]}
        for row in rows
    ]
    return jsonify(history)

@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    user_id = register_user(name, email, password)
    if user_id:
        session['user'] = name
        session['email'] = email
        session['user_id'] = user_id
        session['user_name'] = name
        return redirect(url_for('menu'))
    else:
        return "User already exists. Try logging in.", 400

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    result = validate_login(email, password)

    if result:
        user_id, name = result
        session['user'] = name
        session['email'] = email
        session['user_id'] = user_id
        session['user_name'] = name
        session.permanent = True
        return redirect(url_for('menu'))
    else:
        return "Invalid credentials", 401

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/dismiss-greeting")
def dismiss_greeting():
    session.pop('show_greeting', None)
    return ('', 204)

@app.route("/send-chat-email", methods=["POST"])
def send_chat_email():
    user_id = session.get("user_id")
    user_email = session.get("email")

    if not user_id or not user_email:
        return "Unauthorized", 401

    # Fetch chat history
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT message, response FROM chat_history WHERE user_id = ? ORDER BY timestamp", (user_id,))
    chats = c.fetchall()
    conn.close()

    if not chats:
        return "No chat history to send.", 404

    chat_text = "\n\n".join([f"You: {msg}\nMindMate: {res}" for msg, res in chats])

    try:
        msg = Message("Your MindMate Chat Summary", recipients=[user_email])
        msg.body = f"Hello,\n\nHere is your recent chat with MindMate:\n\n{chat_text}"
        mail.send(msg)
        return "Chat email sent successfully!", 200
    except Exception as e:
        print("Mail sending failed:", e)
        return "Failed to send email.", 500

if __name__ == "__main__":
    app.run(debug=True)
