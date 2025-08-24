from dotenv import load_dotenv
load_dotenv()
# app.py (Final MVP with Dashboard)
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from werkzeug.security import generate_password_hash, check_password_hash
from ai_core import polish_text
import functools

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-super-secret-key-for-dev'
DB_FILE = "polished_text.db"

# --- Database Functions ---
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_FILE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

app.teardown_appcontext(close_db)

# --- User Session & Auth ---
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

def login_required(view):
    """A decorator to ensure a user is logged in before accessing a page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

# --- Main Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if g.user:
        if request.method == 'POST':
            original_text = request.form['original_text']
            polished_text = polish_text(original_text)
            db = get_db()
            db.execute(
                'INSERT INTO documents (user_id, original_text, polished_text, created_at) VALUES (?, ?, ?, ?)',
                (g.user['id'], original_text, polished_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            db.commit()
            return render_template('index.html', original_text=original_text, polished_text=polished_text)
    return render_template('index.html')

@app.route('/dashboard')
@login_required # Protect this page
def dashboard():
    """Shows a history of the logged-in user's documents."""
    db = get_db()
    documents = db.execute(
        'SELECT original_text, polished_text, created_at FROM documents WHERE user_id = ? ORDER BY created_at DESC',
        (g.user['id'],)
    ).fetchall()

    docs_with_dates = []
    for doc in documents:
        doc_dict = dict(doc)
        try:
            # Handle multiple potential datetime formats for robustness
            doc_dict['created_at'] = datetime.strptime(doc_dict['created_at'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            doc_dict['created_at'] = datetime.strptime(doc_dict['created_at'], '%Y-%m-%d %H:%M:%S.%f')
        docs_with_dates.append(doc_dict)

    return render_template('dashboard.html', documents=docs_with_dates)

# --- Auth Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)", (username, password_hash, created_at))
            db.commit()
        except db.IntegrityError:
            flash("Username already taken.")
            return render_template('register.html')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user is None or not check_password_hash(user['password_hash'], password):
            flash('Incorrect username or password.')
        else:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
