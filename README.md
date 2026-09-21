# Guess the Word 🟩

A Wordle-style word guessing game built with Python Flask.

## Features

- **User Registration & Login** with password validation
- **Wordle-style game** with color-coded feedback (green/orange/grey)
- **Max 5 guesses** per word, **max 3 words per day**
- **Admin reports**: daily stats and per-user breakdown
- **20 pre-loaded 5-letter words**

## Setup & Installation

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Seed the database

This creates the database, loads 20 words, and creates an admin user:

```bash
python seed_words.py
```

### 3. Run the application

```bash
python app.py
```

The app will be available at **http://127.0.0.1:5000**

## Default Admin Credentials

| Username | Password |
|----------|----------|
| Admin1   | Admin1$  |

## How to Play

1. Register a new account or login
2. Click "Start New Game"
3. Enter a 5-letter word and submit
4. Letters are color-coded:
   - 🟩 **Green** — Correct letter, correct position
   - 🟧 **Orange** — Correct letter, wrong position
   - ⬜ **Grey** — Letter not in the word
5. You have **5 guesses** to find the word
6. You can play up to **3 words per day**

## Project Structure

```
├── app.py              # Flask app factory
├── models.py           # Database models
├── seed_words.py       # Seed data script
├── requirements.txt    # Dependencies
├── routes/
│   ├── auth.py         # Registration & login
│   ├── game.py         # Game logic
│   └── admin.py        # Admin reports
├── templates/
│   ├── base.html       # Base layout
│   ├── login.html      # Login page
│   ├── register.html   # Registration page
│   ├── game.html       # Game UI
│   └── admin/
│       ├── daily_report.html
│       └── user_report.html
└── static/
    └── style.css       # Wordle-style styling
```

## Tech Stack

- **Python 3** + **Flask**
- **SQLite** (via Flask-SQLAlchemy)
- **Flask-Login** for authentication
- **HTML/CSS/Jinja2** for the frontend
