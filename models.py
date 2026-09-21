from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for both Admin and Player users."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    game_sessions = db.relationship('GameSession', backref='user', lazy=True)

    def set_password(self, password):
        """Hash and store the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Word(db.Model):
    """Five-letter word stored in uppercase."""
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(5), unique=True, nullable=False)

    def __repr__(self):
        return f'<Word {self.word}>'


class GameSession(db.Model):
    """A single game session: one word for a user to guess."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    is_won = db.Column(db.Boolean, nullable=True)        # None = in progress
    is_complete = db.Column(db.Boolean, default=False)

    guesses = db.relationship('Guess', backref='session', lazy=True,
                              order_by='Guess.guess_number')
    word_obj = db.relationship('Word', backref='sessions')

    def __repr__(self):
        return f'<GameSession {self.id} user={self.user_id}>'


class Guess(db.Model):
    """A single guess within a game session."""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('game_session.id'), nullable=False)
    guess_word = db.Column(db.String(5), nullable=False)
    guess_number = db.Column(db.Integer, nullable=False)  # 1-5
    result = db.Column(db.JSON, nullable=False)            # [{letter, status}, ...]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Guess {self.guess_word} #{self.guess_number}>'
