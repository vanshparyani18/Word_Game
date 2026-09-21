from datetime import date
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy.sql.expression import func
from models import db, Word, GameSession, Guess

game_bp = Blueprint('game', __name__)


def evaluate_guess(guess, target):
    """
    Evaluate a guess against the target word.
    Returns a list of 5 dicts: [{letter, status}, ...].
    
    Status values:
    - 'green':  correct letter in correct position
    - 'orange': correct letter in wrong position
    - 'grey':   letter not in the word
    
    Handles duplicate letters correctly using a two-pass algorithm.
    """
    result = [None] * 5
    target_chars = list(target)
    guess_chars = list(guess)

    # First pass: mark exact matches (green)
    for i in range(5):
        if guess_chars[i] == target_chars[i]:
            result[i] = {'letter': guess_chars[i], 'status': 'green'}
            target_chars[i] = None   # consumed from target
            guess_chars[i] = None    # processed

    # Second pass: mark wrong-position (orange) and not-in-word (grey)
    for i in range(5):
        if guess_chars[i] is None:
            continue  # already matched as green
        if guess_chars[i] in target_chars:
            result[i] = {'letter': guess_chars[i], 'status': 'orange'}
            # Consume the first available occurrence in target
            target_chars[target_chars.index(guess_chars[i])] = None
        else:
            result[i] = {'letter': guess_chars[i], 'status': 'grey'}

    return result


@game_bp.route('/dashboard')
@login_required
def dashboard():
    """Show game dashboard: active game or option to start a new one."""
    # Check for an active (incomplete) game session
    active_session = GameSession.query.filter_by(
        user_id=current_user.id,
        is_complete=False
    ).first()

    if active_session:
        return redirect(url_for('game.play', session_id=active_session.id))

    # Count today's games
    today = date.today()
    today_count = GameSession.query.filter_by(
        user_id=current_user.id,
        date=today
    ).count()

    can_play = today_count < 3

    return render_template('game.html',
                           active_game=False,
                           can_play=can_play,
                           games_today=today_count,
                           guesses=[],
                           game_over=False,
                           won=False,
                           message='')


@game_bp.route('/start_game', methods=['POST'])
@login_required
def start_game():
    """Start a new game: pick a random word and create a session."""
    today = date.today()
    today_count = GameSession.query.filter_by(
        user_id=current_user.id,
        date=today
    ).count()

    if today_count >= 3:
        flash("You have reached the maximum of 3 words per day.", 'error')
        return redirect(url_for('game.dashboard'))

    # Pick a random word from the database
    word = Word.query.order_by(func.random()).first()
    if not word:
        flash("No words available in the database. Contact an administrator.", 'error')
        return redirect(url_for('game.dashboard'))

    session = GameSession(
        user_id=current_user.id,
        word_id=word.id,
        date=today,
        is_complete=False
    )
    db.session.add(session)
    db.session.commit()

    return redirect(url_for('game.play', session_id=session.id))


@game_bp.route('/play/<int:session_id>')
@login_required
def play(session_id):
    """Display the current game state with all previous guesses."""
    game_session = GameSession.query.get_or_404(session_id)

    # Ensure the session belongs to the current user
    if game_session.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('game.dashboard'))

    guesses = Guess.query.filter_by(
        session_id=session_id
    ).order_by(Guess.guess_number).all()

    guess_data = []
    for g in guesses:
        guess_data.append({
            'word': g.guess_word,
            'result': g.result
        })

    game_over = game_session.is_complete
    won = game_session.is_won if game_session.is_won is not None else False
    message = ''
    if game_over:
        if won:
            message = 'Congratulations! You guessed the word!'
        else:
            message = 'Better luck next time! The word was ' + game_session.word_obj.word + '.'

    return render_template('game.html',
                           active_game=True,
                           session_id=session_id,
                           guesses=guess_data,
                           guess_count=len(guesses),
                           game_over=game_over,
                           won=won,
                           message=message,
                           can_play=True)


@game_bp.route('/guess/<int:session_id>', methods=['POST'])
@login_required
def submit_guess(session_id):
    """Process a submitted guess."""
    game_session = GameSession.query.get_or_404(session_id)

    if game_session.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('game.dashboard'))

    if game_session.is_complete:
        flash('This game is already over.', 'error')
        return redirect(url_for('game.play', session_id=session_id))

    guess_word = request.form.get('guess', '').upper().strip()

    # Validate: exactly 5 alphabetic characters
    if len(guess_word) != 5 or not guess_word.isalpha():
        flash('Please enter exactly 5 letters.', 'error')
        return redirect(url_for('game.play', session_id=session_id))

    # Check max guesses
    existing_guesses = Guess.query.filter_by(session_id=session_id).count()
    if existing_guesses >= 5:
        flash('Maximum guesses reached.', 'error')
        return redirect(url_for('game.play', session_id=session_id))

    # Evaluate the guess
    target_word = game_session.word_obj.word
    result = evaluate_guess(guess_word, target_word)

    # Save the guess
    guess = Guess(
        session_id=session_id,
        guess_word=guess_word,
        guess_number=existing_guesses + 1,
        result=result
    )
    db.session.add(guess)

    # Check win/lose conditions
    if guess_word == target_word:
        game_session.is_won = True
        game_session.is_complete = True
    elif existing_guesses + 1 >= 5:
        game_session.is_won = False
        game_session.is_complete = True

    db.session.commit()

    return redirect(url_for('game.play', session_id=session_id))
