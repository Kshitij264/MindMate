# 🧠 MindMate — Mental Wellness Platform

MindMate is a full-stack mental wellness web application designed to help users reflect, track their emotions, and improve their mental well-being through interactive and personalized features.

It provides a calm, visually immersive environment combined with intelligent backend processing to create a supportive digital companion.

---

## ✨ What MindMate Offers

MindMate is not just a chatbot — it is a **complete mental wellness system** that includes:

- 💬 AI-powered conversational support  
- 😊 Mood tracking and visualization  
- 📝 Personal journaling with insights  
- 🌿 Guided relaxation activities  
- 📚 Mental health facts and recommendations  
- 📧 Chat history export via email  
- 🎨 Beautiful, animated, responsive UI  

---

## 🧩 Features & Working

### 🏠 1. Welcome Screen
- Clean, calming UI with blurred glass effect
- Motivational message:
  > *“Your safe space to reflect, heal, and grow”*
- "Get Started" button opens authentication popup

---

### 🔐 2. Authentication System
- Login & Register functionality
- Secure user-based experience
- Each user gets:
  - Their own chat history
  - Personal mood tracking
  - Journal entries

---

### 📋 3. Main Menu Dashboard
After login, user sees 4 core sections:

- 💬 Chat with MindMate  
- 📚 Mental Health Facts  
- 🌿 Guided Activities  
- 📝 Journal & Mood Log  

Includes:
- Personalized greeting popup
- Smooth animated UI cards
- Logout option

---

### 💬 4. AI Chatbot (Core Feature)

#### ⚙️ Working:
- User sends message → Flask backend → Cohere API → Response returned
- Sentiment analysis applied on each message

#### 💡 Features:
- Real-time chat interface
- Typing animation
- Smart conversation flow
- Emoji support 😊
- Dynamic placeholder suggestions
- Auto-scroll and smooth UI

#### 📊 Mood Graph:
- Each message is analyzed for sentiment polarity
- Graph updates live based on emotional tone

#### 📜 Chat History:
- Previous chats shown in sidebar
- Stored per user

#### 📧 Email Feature:
- One-click button to send full chat transcript to user email

---

### 📚 5. Mental Health Facts Page

#### 💡 Features:
- 🟣 Fact of the Day section
- 🤖 Recommended facts based on usage
- 🔍 Category filters:
  - Stress
  - Anxiety
  - Sleep
  - Self Care

#### ⭐ Interactive Features:
- Save facts
- Remove saved facts
- Smooth card animations
- Expandable content

---

### 🌿 6. Guided Activities

#### Step 1: Choose Ambience
- Mountains 🏔️
- Beach 🌊
- Garden 🌿
- Rain 🌧️

#### Step 2: Relax Mode

Includes:
- Breathing exercise animation
- Ambient background visuals
- Sound controls (volume + mute)
- Session tracking (focus time)

#### Purpose:
Helps user calm down using guided breathing and environment simulation

---

### 📝 7. Journal & Mood Tracker

#### ✍️ Journal:
- Write daily thoughts
- Entries saved with timestamp
- Scrollable history

#### 😊 Mood Selection:
- Select mood using emoji
- Stored per entry

#### 📊 Mood Analytics:
- Weekly mood graph
- Tracks emotional trends

#### 🤖 Smart Insight:
- AI-generated summary of user mood patterns
- Detects:
  - Emotion type
  - Trend (improving/declining)
  - Short explanation

---

## 🎨 UI/UX Highlights

- Glassmorphism design (blur + transparency)
- Smooth animations and transitions
- Fully responsive layout
- Theme toggle (light/dark)
- Background-based emotional design

---

## ⚙️ Tech Stack

### Frontend:
- HTML
- CSS (External stylesheet)
- JavaScript

### Backend:
- Flask (Python)

### APIs & Libraries:
- Cohere API → chatbot responses
- TextBlob → sentiment analysis
- Chart.js → mood visualization
- Flask-Mail → email feature

---

## 🧠 How It Works (Flow)

1. User logs in  
2. Interacts with chatbot  
3. Sentiment is analyzed  
4. Mood graph updates  
5. Chat stored in database  
6. User can:
   - View history
   - Email chat
   - Track mood
   - Write journal
   - Explore activities

---

## 🚀 Project Goal

To create a **personal mental wellness companion** that:

- Encourages self-expression  
- Tracks emotional patterns  
- Provides supportive interaction  
- Promotes calmness and reflection  

---

## 📌 Note

This project is designed for:
- Learning full-stack development  
- Showcasing UI/UX skills  
- Demonstrating AI integration in real-world apps  

---

## 👨‍💻 Author

**Kshitij Shukla**

---

> 💙 “Small steps toward better mental health, every day.”