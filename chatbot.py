from textblob import TextBlob
import random
import os

# Persistent polarity tracker
_last_polarity = 0.0

quotes = [
    "You’ve survived 100% of your worst days.",
    "You are stronger than you think.",
    "This too shall pass.",
    "Every day may not be good, but there’s something good in every day.",
    "Keep going. You’re doing better than you think.",
    "You are not alone. There is help. There is hope."
]

sad_keywords = ["sad", "nothing", "lost", "hopeless", "tired", "alone", "depressed", "empty", "miserable"]
anxiety_keywords = ["anxious", "anxiety", "panic", "stressed", "stress", "overwhelmed", "nervous"]
summary_keywords = ["summary", "how was i", "how am i", "how was my day", "end"]

# Mood tracker (per session)
mood_history = []

anxious_replies = [
    "It sounds like you're feeling anxious. 🧘‍♀️",
    "I can sense some anxiety. It's okay to feel this way.",
    "You're overwhelmed — that's completely valid. Let's calm it down a bit."
]

neutral_replies = [
    "I understand things feel heavy. You're not alone. 🌿",
    "That's totally okay. We all have off days.",
    "Hmm, sounds like you're holding a lot inside. I'm here to listen."
]

positive_replies = [
    "I'm glad you're feeling okay. 😊 I'm always here if you need to talk.",
    "That's good to hear. Stay strong!",
    "You're doing well. Keep taking care of yourself 💚"
]

def get_response(user_input):
    global _last_polarity

    blob = TextBlob(user_input)
    polarity = blob.sentiment.polarity
    _last_polarity = polarity
    mood_history.append(polarity)

    words = user_input.lower().split()

    if any(phrase in user_input.lower() for phrase in summary_keywords):
        return summarize_mood()

    try:
        import cohere
        api_key = os.environ.get("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY not found in environment.")

        co = cohere.Client(api_key)

        print("🤖 Sending message to Cohere...")
        response = co.chat(
            model="command-nightly",
            message=user_input
        )
        return response.text

    except Exception as e:
        print("⚠️ Cohere fallback:", e)

        # Local fallback based on polarity and keywords
        if any(word in words for word in anxiety_keywords):
            return random.choice(anxious_replies)
        elif polarity < -0.3 or any(word in words for word in sad_keywords):
            quote = random.choice(quotes)
            return f"I'm really sorry you're feeling this way. 💙 Here's something for you:<br>\"{quote}\""
        elif polarity < 0.1:
            return random.choice(neutral_replies)
        else:
            return random.choice(positive_replies)

def summarize_mood():
    if not mood_history:
        return "We haven't really talked yet. Say something first 😊"

    avg = sum(mood_history) / len(mood_history)

    if avg < -0.3:
        mood = "mostly low"
    elif avg < 0.1:
        mood = "neutral"
    else:
        mood = "mostly positive"

    return (
        f"Here's your mood summary for this session: 📝<br>"
        f"Your mood was {mood}, based on {len(mood_history)} messages.<br>"
        f"I'm glad you opened up. Be kind to yourself 💙"
    )

def get_last_polarity():
    return _last_polarity
