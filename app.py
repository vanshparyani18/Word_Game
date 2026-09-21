import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from models import db, User


def create_app():
    """Application factory for the Guess the Word game."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'guess-the-word-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///guess_the_word.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'error'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.game import game_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(admin_bp)

    # Root route redirects to login
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
