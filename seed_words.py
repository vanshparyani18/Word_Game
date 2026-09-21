"""
Seed script: populates the database with 20 five-letter words and one admin user.

Usage:
    python seed_words.py
"""
from app import create_app
from models import db, Word, User

WORDS = [
    'APPLE', 'BRAVE', 'CHARM', 'CRANE', 'DANCE',
    'EAGLE', 'FLAME', 'GRAPE', 'HOUSE', 'JOKER',
    'KNEEL', 'LEMON', 'MANGO', 'NOBLE', 'OLIVE',
    'PEARL', 'QUEEN', 'RAVEN', 'TOWER', 'UNITY',
]


def seed():
    app = create_app()
    with app.app_context():
        # Seed words
        added_words = 0
        for w in WORDS:
            if not Word.query.filter_by(word=w).first():
                db.session.add(Word(word=w))
                added_words += 1
        db.session.commit()
        print(f"Seeded {added_words} words (total: {Word.query.count()}).")

        # Create admin user if not exists
        admin_username = 'Admin1'
        if not User.query.filter_by(username=admin_username).first():
            admin = User(username=admin_username, is_admin=True)
            admin.set_password('Admin1$')
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user created: username='{admin_username}', password='Admin1$'")
        else:
            print(f"Admin user '{admin_username}' already exists.")


if __name__ == '__main__':
    seed()
