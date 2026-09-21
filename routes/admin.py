from datetime import date, datetime
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, GameSession

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator that restricts access to admin users only."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('game.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/daily_report', methods=['GET', 'POST'])
@admin_required
def daily_report():
    """
    Daily report: for a selected date, show:
    - Number of users who played
    - Number of correct guesses (games won)
    """
    selected_date = date.today().isoformat()

    if request.method == 'POST':
        selected_date = request.form.get('report_date', date.today().isoformat())

    try:
        report_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        report_date = date.today()
        selected_date = report_date.isoformat()

    # Get all sessions for the selected date
    sessions = GameSession.query.filter_by(date=report_date).all()

    unique_users = len(set(s.user_id for s in sessions))
    correct_guesses = sum(1 for s in sessions if s.is_won)

    report_data = {
        'date': selected_date,
        'num_users': unique_users,
        'correct_guesses': correct_guesses
    }

    return render_template('admin/daily_report.html',
                           report_data=report_data,
                           selected_date=selected_date)


@admin_bp.route('/user_report', methods=['GET', 'POST'])
@admin_required
def user_report():
    """
    User report: for a selected user, show per-date breakdown of:
    - Date
    - Number of words tried
    - Number of correct guesses
    """
    users = User.query.filter_by(is_admin=False).all()
    report_data = None
    selected_user_id = None

    if request.method == 'POST':
        selected_user_id = request.form.get('user_id')
        if selected_user_id:
            selected_user_id = int(selected_user_id)
            user = User.query.get(selected_user_id)

            if user:
                sessions = GameSession.query.filter_by(
                    user_id=selected_user_id
                ).order_by(GameSession.date.desc()).all()

                # Group by date
                date_data = {}
                for session in sessions:
                    d = session.date.isoformat()
                    if d not in date_data:
                        date_data[d] = {
                            'date': d,
                            'words_tried': 0,
                            'correct_guesses': 0
                        }
                    date_data[d]['words_tried'] += 1
                    if session.is_won:
                        date_data[d]['correct_guesses'] += 1

                report_data = {
                    'username': user.username,
                    'entries': sorted(date_data.values(),
                                      key=lambda x: x['date'], reverse=True)
                }

    return render_template('admin/user_report.html',
                           users=users,
                           report_data=report_data,
                           selected_user_id=selected_user_id)
