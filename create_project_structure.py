# create_project_structure.py
import os

directories = ["static/css", "static/js", "templates"]
files = {
    "app.py": "# Main Flask application file",
    "database_setup.py": "# Script to initialize the database",
    "ai_core.py": "# Script for AI logic",
    ".gitignore": "venv/\n__pycache__/\n*.pyc\n*.db*\n.DS_Store\n.env",
    "requirements.txt": "Flask\nopenai\npython-dotenv\n",
    "templates/base.html": """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>PolishedText.ai</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
</head><body><nav class="container"><ul><li><strong><a href="/">🚀 PolishedText.ai</a></strong></li></ul><ul>{% if g.user %}<li><a href="/dashboard">Dashboard</a></li><li><a href="/logout">Logout</a></li>{% else %}<li><a href="/register">Register</a></li><li><a href="/login">Login</a></li>{% endif %}</ul></nav><main class="container">{% with messages = get_flashed_messages() %}{% if messages %}<div class="flash-error">{% for message in messages %}<span>{{ message }}</span>{% endfor %}</div>{% endif %}{% endwith %}{% block content %}{% endblock %}</main></body></html>""",
    "templates/index.html": "{% extends 'base.html' %}\n\n{% block content %}\n<h1>Welcome</h1>\n{% endblock %}",
    "templates/login.html": "{% extends 'base.html' %}\n\n{% block content %}\n<h2>Login</h2><form method='post'><label>Username</label><input name='username' required><label>Password</label><input name='password' type='password' required><button type='submit'>Login</button></form>\n{% endblock %}",
    "templates/register.html": "{% extends 'base.html' %}\n\n{% block content %}\n<h2>Register</h2><form method='post'><label>Username</label><input name='username' required><label>Password</label><input name='password' type='password' required><button type='submit'>Register</button></form>\n{% endblock %}",
    "static/css/style.css": "/* Your custom CSS will go here */"
}

for directory in directories:
    os.makedirs(directory, exist_ok=True)
for filepath, content in files.items():
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f: f.write(content.strip())
print("✅ Project structure created successfully!")
