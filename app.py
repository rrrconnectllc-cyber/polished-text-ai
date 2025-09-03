# app.py (Final version with Welcome Email)
import sqlite3
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from werkzeug.security import generate_password_hash, check_password_hash
from ai_core import polish_text
import functools
from dotenv import load_dotenv
import os
from flask_mail import Mail, Message

# --- App Setup and Configuration ---
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-super-secret-key-for-dev'
DB_FILE = "polished_text.db"
MONTHLY_QUOTA = 10

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

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
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

# --- Main Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    original_text = ''
    polished_text = ''
    quota_left = 0
    if g.user:
        today = date.today()
        last_reset = date.fromisoformat(g.user['last_quota_reset'])
        if today.month != last_reset.month or today.year != last_reset.year:
            db = get_db()
            db.execute('UPDATE users SET usage_count = ?, last_quota_reset = ? WHERE id = ?', (0, today.isoformat(), g.user['id']))
            db.commit()
            g.user = get_db().execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        usage_count = g.user['usage_count'] if g.user['usage_count'] is not None else 0
        quota_left = MONTHLY_QUOTA - usage_count
        if request.method == 'POST':
            if quota_left > 0:
                original_text = request.form['original_text']
                polished_text = polish_text(original_text)
                db = get_db()
                db.execute('UPDATE users SET usage_count = usage_count + 1 WHERE id = ?', (g.user['id'],))
                db.execute('INSERT INTO documents (user_id, original_text, polished_text, created_at) VALUES (?, ?, ?, ?)',
                           (g.user['id'], original_text, polished_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                db.commit()
                quota_left -= 1
            else:
                flash("You have used your monthly quota. Upgrade to Pro for unlimited access!")
                original_text = request.form['original_text']
    elif request.method == 'POST':
        original_text = request.form['original_text']
        polished_text = polish_text(original_text)
    return render_template('index.html', original_text=original_text, polished_text=polished_text, quota_left=quota_left)

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    documents = db.execute(
        'SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC', (g.user['id'],)
    ).fetchall()
    docs_with_dates = []
    for doc in documents:
        doc_dict = dict(doc)
        try:
            doc_dict['created_at'] = datetime.strptime(doc_dict['created_at'], '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            pass
        docs_with_dates.append(doc_dict)
    return render_template('dashboard.html', documents=docs_with_dates)

# --- Auth Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')
        if not email:
            flash("An email address is required.")
            return render_template('register.html')
        password_hash = generate_password_hash(password)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today_str = date.today().isoformat()
        initial_usage = 0
        db = get_db()
        try:
            db.execute(
                """INSERT INTO users (username, password_hash, created_at, usage_count, last_quota_reset, email)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (username, password_hash, created_at, initial_usage, today_str, email)
            )
            db.commit()
            try:
                msg = Message('Welcome to PolishedText.ai!',
                              sender=app.config['MAIL_USERNAME'],
                              recipients=[email])
                msg.html = render_template('welcome_email.html', username=username)
                mail.send(msg)
            except Exception as e:
                print(f"Error sending email: {e}")
        except db.IntegrityError:
            flash("Username or email already taken.")
            return render_template('register.html')
        flash("Registration successful! Please log in.")
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
