from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    data = (
        request.form['username'],
        request.form['password'],
        request.form['firstname'],
        request.form['lastname'],
        request.form['email'],
        request.form['address']
    )

    conn = sqlite3.connect(os.path.join(BASE_DIR, 'users.db'))
    c = conn.cursor()
    c.execute("INSERT INTO users (username,password,firstname,lastname,email,address) VALUES (?,?,?,?,?,?)", data)
    conn.commit()
    conn.close()

    return redirect(url_for('profile', username=data[0]))

@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'users.db'))
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(os.path.join(BASE_DIR, 'users.db'))
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        user = c.fetchone()
        conn.close()
        if user:
            return redirect(url_for('profile', username=username))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/upload/<username>', methods=['POST'])
def upload(username):
    file = request.files['file']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    with open(filepath, 'r') as f:
        word_count = len(f.read().split())

    conn = sqlite3.connect(os.path.join(BASE_DIR, 'users.db'))
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    return render_template('profile.html', user=user, word_count=word_count, filename=file.filename)

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
