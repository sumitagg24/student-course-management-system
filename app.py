from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="student_management"
)
cursor = conn.cursor(dictionary=True)

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'sumit123':
            session['admin'] = True
            return redirect('/dashboard')
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/login')

    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cursor.fetchone()['total']

    cursor.execute("SELECT department, COUNT(*) AS count FROM students GROUP BY department")
    dept_data = cursor.fetchall()

    labels = [row['department'] for row in dept_data]
    counts = [row['count'] for row in dept_data]

    return render_template('index.html',
                           total_students=total_students,
                           labels=labels,
                           counts=counts)

@app.route('/view_students')
def view_students():
    if not session.get('admin'):
        return redirect('/login')
    return render_template('students.html')

@app.route('/api/students')
def api_students():
    if not session.get('admin'):
        return jsonify([])
    cursor.execute("SELECT * FROM students")
    return jsonify(cursor.fetchall())

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if not session.get('admin'):
        return redirect('/login')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        cursor.execute("INSERT INTO students (name, email, department) VALUES (%s, %s, %s)",
                       (name, email, department))
        conn.commit()
        return redirect('/view_students')
    return render_template('add_student.html')

@app.route('/delete_student/<int:id>')
def delete_student(id):
    if not session.get('admin'):
        return redirect('/login')
    cursor.execute("DELETE FROM students WHERE id = %s", (id,))
    conn.commit()
    return redirect('/view_students')

if __name__ == '__main__':
    app.run(debug=True)




