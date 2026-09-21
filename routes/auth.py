from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)


def validate_username(username):
    """
    Validate username:
    - At least 5 characters
    - Must contain both uppercase and lowercase letters
    """
    if len(username) < 5:
        return "Username must be at least 5 characters long."
    has_upper = any(c.isupper() for c in username)
    has_lower = any(c.islower() for c in username)
    if not (has_upper and has_lower):
        return "Username must contain both uppercase and lowercase letters."
    return None


def validate_password(password):
    """
    Validate password:
    - At least 5 characters
    - Must contain alphabetic characters
    - Must contain numeric characters
    - Must contain at least one special character from: $, %, *, &
    """
    if len(password) < 5:
        return "Password must be at least 5 characters long."
    has_alpha = any(c.isalpha() for c in password)
    has_numeric = any(c.isdigit() for c in password)
    special_chars = {'$', '%', '*', '&'}
    has_special = any(c in special_chars for c in password)
    if not has_alpha:
        return "Password must contain at least one letter."
    if not has_numeric:
        return "Password must contain at least one number."
    if not has_special:
        return "Password must contain at least one special character ($, %, *, &)."
    return None


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration with validation."""
    if current_user.is_authenticated:
        return redirect(url_for('game.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Validate username
        username_error = validate_username(username)
        if username_error:
            flash(username_error, 'error')
            return render_template('register.html', username=username)

        # Validate password
        password_error = validate_password(password)
        if password_error:
            flash(password_error, 'error')
            return render_template('register.html', username=username)

        # Check for duplicate username
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.', 'error')
            return render_template('register.html', username=username)

        # Create user
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', username='')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.daily_report'))
        return redirect(url_for('game.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin.daily_report'))
            return redirect(url_for('game.dashboard'))

        flash('Invalid username or password.', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
