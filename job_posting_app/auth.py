import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from job_posting_app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')



@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        roles = request.form['roles']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif len(password) < 8 :
            error = 'Password must be 8 characters.'
        elif roles == 'no_role':
            error = 'Select a role.'


        if error is None:
            try:
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, roles) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), roles),
                )
                user_id = cursor.lastrowid
                print(user_id)
                if roles == 'applicant':
                    cursor.execute("INSERT INTO applicant (user_id) VALUES (?) ", (user_id,))
                if roles == 'company':
                    cursor.execute("INSERT INTO company (user_id) VALUES (?) ", (user_id,))
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
            
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']

            if user['roles'] == 'company':
                return redirect(url_for('admin.admin'))
            else:
                return redirect(url_for('jobs'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view

def admin_middleware(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user["roles"] != 'company':
            return redirect(url_for('jobs'))
        return view(**kwargs)
    
    return wrapped_view

def applicant_middleware(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user["roles"] != 'applicant':
            return redirect(url_for('admin.admin'))
        return view(**kwargs)
    
    return wrapped_view