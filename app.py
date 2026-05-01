from dotenv import load_dotenv
import os
import sqlite3
import datetime
from datetime import datetime, timedelta
from database import create_gratitude_table
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mail import Mail, Message
from chatbot import get_response, get_last_polarity
from database import init_db, register_user, validate_login

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.permanent_session_lifetime = timedelta(minutes=30)
create_gratitude_table()
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
    conn = sqlite3.connect("mindmate.db")
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

# 🔥 SAVE MOOD TO DB (ONLY IF USER EXISTS)
    if user_id:
        conn = sqlite3.connect("mindmate.db")
        c = conn.cursor()
        c.execute("INSERT INTO mood (user_id, mood) VALUES (?, ?)", (user_id, str(polarity)))
        conn.commit()
        conn.close()
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

    conn = sqlite3.connect("mindmate.db")
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
    conn = sqlite3.connect("mindmate.db")
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
@app.route("/mental-health-facts")
def mental_health_facts():
    if 'user' not in session:
        return redirect(url_for('welcome'))
    return render_template("mental_health_facts.html")
@app.route("/explain-fact", methods=["POST"])
def explain_fact():
    data = request.get_json()
    fact = data.get("fact")

    explanation = get_response(f"Explain this mental health fact simply: {fact}")

    return jsonify({"explanation": explanation})
@app.route("/save-fact", methods=["POST"])
def save_fact():
    data = request.get_json()
    fact = data.get("fact")
    user_id = session.get("user_id")

    conn = sqlite3.connect("mindmate.db")
    c = conn.cursor()

    # ✅ prevent duplicates
    c.execute("SELECT * FROM saved_facts WHERE user_id=? AND fact=?", (user_id, fact))
    if not c.fetchone():
        c.execute("INSERT INTO saved_facts (user_id, fact) VALUES (?, ?)", (user_id, fact))

    conn.commit()
    conn.close()

    return jsonify({"status": "saved"})
@app.route("/remove-fact", methods=["POST"])
def remove_fact():
    data = request.get_json()
    fact = data.get("fact")
    user_id = session.get("user_id")

    conn = sqlite3.connect("mindmate.db")
    c = conn.cursor()

    c.execute("DELETE FROM saved_facts WHERE user_id=? AND fact=?", (user_id, fact))

    conn.commit()
    conn.close()

    return jsonify({"status": "removed"})
@app.route("/get-saved-facts")
def get_saved_facts():
    user_id = session.get("user_id")

    conn = sqlite3.connect("mindmate.db")
    c = conn.cursor()

    c.execute("SELECT fact FROM saved_facts WHERE user_id = ?", (user_id,))
    rows = c.fetchall()

    conn.close()

    return jsonify([row[0] for row in rows])
import random
from datetime import date

@app.route("/fact-of-the-day")
def fact_of_the_day():

    facts = [
        "Deep breathing reduces stress",
        "Exercise lowers anxiety",
        "Sleep affects mood",
        "Journaling helps clarity",
        "Nature reduces stress",
        "Limiting caffeine helps"
    ]

    # 🔥 same fact per day
    today = date.today().toordinal()
    fact = facts[today % len(facts)]

    return jsonify({"fact": fact})
@app.route("/recommended-facts")
def recommended_facts():

    polarity = get_last_polarity()

    if polarity < 0:
        facts = [
            "Deep breathing reduces stress",
            "Nature helps calm your mind",
            "Journaling reduces emotional overload"
        ]
    elif polarity > 0:
        facts = [
            "Exercise boosts happiness",
            "Gratitude improves mental well-being",
            "Helping others increases joy"
        ]
    else:
        facts = [
            "Sleep improves emotional balance",
            "Routine builds stability",
            "Mindfulness improves focus"
        ]

    return jsonify(facts)
@app.route('/guided-activities')
def guided_activities():
    return render_template('guided_activities.html')
@app.route('/save_gratitude', methods=['POST'])
def save_gratitude():
    data = request.get_json()
    text = data.get("text")

    user_email = session.get("user")  # assuming login exists

    conn = sqlite3.connect("mindmate.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO gratitude (user_email, text) VALUES (?, ?)",
        (user_email, text)
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})
@app.route('/get_gratitude')
def get_gratitude():
    user_email = session.get("user")

    conn = sqlite3.connect("mindmate.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT text, created_at FROM gratitude WHERE user_email=? ORDER BY created_at DESC LIMIT 5",
        (user_email,)
    )

    rows = cursor.fetchall()
    conn.close()

    data = [{"text": r[0], "time": r[1]} for r in rows]

    return jsonify(data)
@app.route('/get_streak')
def get_streak():
    user_email = session.get("user")

    conn = sqlite3.connect("mindmate.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DATE(created_at) FROM gratitude 
        WHERE user_email=? 
        ORDER BY created_at DESC
    """, (user_email,))

    dates = [row[0] for row in cursor.fetchall()]
    conn.close()

    streak = 0
    current = datetime.date.today()

    for d in dates:
        if str(current) == d:
            streak += 1
            current -= datetime.timedelta(days=1)
        else:
            break

    return jsonify({"streak": streak})
@app.route('/journal')
def journal():
    return render_template('journal.html')
@app.route('/save_journal', methods=['POST'])
def save_journal():
    data = request.get_json()

    text = data.get('text')
    mood = data.get('mood')

    user_id = 1

    conn = sqlite3.connect('mindmate.db')
    c = conn.cursor()

    c.execute("""
        INSERT INTO journal (user_id, text, mood)
        VALUES (?, ?, ?)
    """, (user_id, text, mood))

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

@app.route('/get_journal')
def get_journal():
    user_id = 1

    conn = sqlite3.connect('mindmate.db')
    c = conn.cursor()

    c.execute("""
    SELECT id, text, mood, created_at
    FROM journal
    WHERE user_id = ?
    ORDER BY created_at DESC
""", (user_id,))

    rows = c.fetchall()
    conn.close()

    result = []

    from datetime import datetime, timedelta

    for row in rows:
        entry_id = row[0]
        text = row[1]
        mood = row[2]
        time_str = row[3]

        utc_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        ist_time = utc_time + timedelta(hours=5, minutes=30)

        formatted_time = ist_time.strftime("%d %b %Y, %I:%M %p")

        result.append({
            "id": entry_id,   # 🔥 THIS WAS MISSING
            "text": text,
            "mood": mood,
            "time": formatted_time
        })

    return jsonify(result)

    
@app.route('/save_mood', methods=['POST'])
def save_mood():
    data = request.json
    mood = data['mood']

    conn = sqlite3.connect('mindmate.db')
    c = conn.cursor()

    c.execute("INSERT INTO mood (mood) VALUES (?)", (mood,))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route('/mood_stats')
def mood_stats():
    user_id = 1

    conn = sqlite3.connect('mindmate.db')
    c = conn.cursor()

    # Last 7 days mood count
    c.execute("""
        SELECT mood, COUNT(*)
        FROM journal
        WHERE user_id = ?
        AND DATE(created_at) >= DATE('now', '-7 day')
        GROUP BY mood
    """, (user_id,))

    rows = c.fetchall()
    conn.close()

    stats = {
        "sad": 0,
        "neutral": 0,
        "happy": 0,
        "excited": 0
    }

    for mood, count in rows:
        if mood:
            stats[mood] = count

    return jsonify(stats)

@app.route('/mood_insight')
def mood_insight():
    from flask import session, jsonify
    import sqlite3

    user_id = session.get("user_id", 1)

    conn = sqlite3.connect('mindmate.db')
    c = conn.cursor()

    c.execute("""
        SELECT mood
        FROM journal
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 5
    """, (user_id,))

    moods = [row[0] for row in c.fetchall()]
    conn.close()

    if not moods:
        return jsonify({"insight": "Start journaling to unlock meaningful insights 🌱"})

    happy = moods.count("happy") + moods.count("excited")
    sad = moods.count("sad")

    # 🔥 TREND DETECTION
    if len(moods) >= 3:
        if moods[0] in ["happy", "excited"] and moods[-1] == "sad":
            trend = "improving"
        elif moods[0] == "sad" and moods[-1] in ["happy", "excited"]:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"

    # 🔥 SMART INSIGHT
    if happy > sad:
        insight = "You've been feeling more positive lately. There's a noticeable emotional improvement — keep building on this momentum 🌟"
    elif sad > happy:
        insight = "Recent entries suggest you've been going through some low moments. Taking small breaks and expressing yourself can really help 💙"
    else:
        insight = "Your emotions seem to fluctuate, but you're maintaining balance. Staying consistent with journaling will help you understand yourself better ✨"

    return jsonify({"insight": insight, "trend": trend})

@app.route('/delete_journal', methods=['POST'])
def delete_journal():
    data = request.get_json()
    entry_id = data.get('id')

    conn = sqlite3.connect('mindmate.db')
    c = conn.cursor()

    c.execute("DELETE FROM journal WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

    return jsonify({"status": "deleted"})

@app.route('/journal_summary')
def journal_summary():
    from flask import session, jsonify
    import sqlite3
    import cohere
    import os
    import json

    user_id = session.get("user_id", 1)

    conn = sqlite3.connect('mindmate.db')
    c = conn.cursor()

    c.execute("""
        SELECT text 
        FROM journal 
        WHERE user_id=? 
        ORDER BY created_at DESC 
        LIMIT 5
    """, (user_id,))

    rows = c.fetchall()
    conn.close()

    if not rows:
        return jsonify({
            "summary": "Start writing journals to get AI insights 🌱",
            "emotion": "N/A",
            "trend": "N/A"
        })

    entries = [r[0] for r in rows if r[0]]
    combined_text = "\n".join(entries)

    co = cohere.Client(os.getenv("COHERE_API_KEY"))

    prompt = f"""
Analyze the emotional state of the user based on these journal entries:

{combined_text}

IMPORTANT:
- Return ONLY valid JSON
- Do NOT add any explanation
- Do NOT add text before or after JSON

Format:
{{
  "summary": "...",
  "emotion": "...",
  "trend": "improving / declining / stable"
}}
"""
    import re

    try:
        response = co.chat(message=prompt)
        text = response.text.strip()

        json_text = re.search(r'\{.*\}', text, re.DOTALL).group()
        result = json.loads(json_text)

        return jsonify(result)

    except Exception as e:
        print("AI Summary Error:", e)

        return jsonify({
            "summary": "You're reflecting consistently. Keep going 💙",
            "emotion": "Mixed",
            "trend": "Stable"
        })

if __name__ == "__main__":
    app.run(debug=True)
