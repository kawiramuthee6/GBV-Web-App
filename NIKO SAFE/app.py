from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import africastalking

app = Flask(__name__)
app.secret_key = 'sharon2002'

africastalking.initialize(username="Sharon123", api_key="6ac512bbeb96c9dfb1027764e4099ebc0fdb09c4ee223403bf39590aab7fb0aa")
sms = africastalking.SMS

def create_connection():
    conn = sqlite3.connect('users.db')
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        firstname TEXT NOT NULL,
                        lastname TEXT NOT NULL,
                        email TEXT NOT NULL,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                    )''')
    conn.commit()
    conn.close()

def create_report_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        gender TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        location TEXT NOT NULL,
                        remain_anonymous TEXT,
                        description TEXT NOT NULL
                    )''')
    conn.commit()
    conn.close()

create_table()
create_report_table()

def insert_user(firstname, lastname, email, username, password):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO users (firstname, lastname, email, username, password) 
                        VALUES (?, ?, ?, ?, ?)''', (firstname, lastname, email, username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print("Error inserting user:", e)
        conn.rollback()
        conn.close()
        return False


def check_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

@app.route('/')
def index():
    return render_template('landing-page.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = check_user(username, password)
        if user:
            session['username'] = username
            session['fullname'] = user[1] + ' ' + user[2]
            session['email'] = user[3]
            return redirect(url_for('home'))
        else:
            flash('Incorrect username or password', 'error')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        if insert_user(firstname, lastname, email, username, password):
            flash('User registration was successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Failed to register the user', 'error')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/home/report', methods=['GET', 'POST'])
def report():
    if 'username' not in session:
        return redirect(url_for('login'))

        

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        age = request.form.get('age')
        gender = request.form.get('gender')
        
        phone = request.form.get('phone')
        location = request.form.get('location')
        remain_anonymous = request.form.get('remain_anonymous')
        description = request.form.get('desc')

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO reports (name, email, age, gender, phone, location, remain_anonymous, description) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (name, email, age, gender, phone, location, remain_anonymous, description))
            conn.commit()
            conn.close()
            flash('Your report has been submitted successfully!', 'success')
            #sendsms
            sms_message = f"Dear {name}, Thank you for sharing your story with us. We will connect you with one of our team members to guide you on the way forward. For emergiencies contact,The National GBV helpline 1195,Police helpline 999/112,Childline Kenya helpline 116 "
            response = sms.send(sms_message, [phone])
            print(response)#fordebugging
        
        except sqlite3.Error as e:
            print("Error inserting report:", e)
            conn.rollback()
            conn.close()
            flash('Failed to submit report.', 'error')

        return redirect(url_for('report'))

    return render_template('report.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
