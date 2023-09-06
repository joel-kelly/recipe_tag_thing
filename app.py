from flask import Flask, g, request, redirect, url_for, render_template
import sqlite3

app = Flask(__name__)
app.template_folder = 'templates'

DATABASE = 'mydatabase.db'  # Change to your desired database filename

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initialize the database."""
    init_db()
    print('Initialized the database.')

@app.route('/adduser', methods=['GET','POST'])
def adduser():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute('INSERT INTO users (username, email) VALUES (?, ?)', (username, email))
            db.commit()
            return 'User added successfully! <a href="/users">View Users</a>'
        except sqlite3.Error as e:
            db.rollback()
            return 'Error adding user: ' + str(e)
    else:
        print("GET")
        return render_template('adduser.html')
        
@app.route('/users')
def list_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT username, email FROM users')
    users = cursor.fetchall()
    return render_template('users.html', users=users)

if __name__ == '__main__':
    app.run(port=8000,debug=True)
