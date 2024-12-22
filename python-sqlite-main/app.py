from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
# Penambahan library
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
import secrets
import sqlite3
from markupsafe import escape

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# Penambahan kode untuk login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Penambahan class user untuk autentikasi
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Penambahan fungsi load_user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'
# Penambahan route untuk registrasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Cek apakah pengguna sudah ada
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username sudah ada. Silakan pilih yang lain.', 'danger')
            return redirect(url_for('register'))

        # Hash kata sandi
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Buat pengguna baru
        new_user = User(username=username, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Registrasi gagal: {}'.format(str(e)), 'danger')
            return redirect(url_for('register'))

        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# penambahan route untuk login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Username atau Password salah.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

# Before
# @app.route('/')
# def index():
#    # RAW Query
#    students = db.session.execute(text('SELECT * FROM student')).fetchall()
#    return render_template('index.html', students=students)
# After
@app.route('/') #87-89
# penambahan login_required untuk index
@login_required
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)



@app.route('/add', methods=['POST'])
# penambahan login_required untuk add
@login_required
def add_student():
    # before 
    # name = request.form['name']
    # age = request.form['age']
    # grade = request.form['grade']
    # after
    name = escape(request.form['name'])
    age = escape(request.form['age'])
    grade = escape(request.form['grade'])
    

    connection = sqlite3.connect('instance/students.db')
    cursor = connection.cursor()

    # RAW Query
    # db.session.execute(
    #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    #     {'name': name, 'age': age, 'grade': grade}
    # )
    # db.session.commit()
    # query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    # cursor.execute(query)
    # connection.commit()
    # affer
    query = text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)")
    params = {"name": name, "age": age, "grade": grade}
    db.session.execute(query, params)
    db.session.commit()
    connection.close()
    return redirect(url_for('index'))


@app.route('/delete/<string:id>') 
# penambahan login_required untuk add
@login_required
def delete_student(id):
    # RAW Query
    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
# penambahan login_required untuk add
@login_required
def edit_student(id):
    if request.method == 'POST':
        # before 
        # name = request.form['name']
        # age = request.form['age']
        # grade = request.form['grade']
        # after
        name = escape(request.form['name'])
        age = escape(request.form['age'])
        grade = escape(request.form['grade'])
        
        # RAW Query
        # before
        # db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
        # db.session.commit()
        # affer
        query = text("UPDATE student SET name=:name, age=:age, grade=:grade WHERE id=:id")
        params = {"name": name, "age": age, "grade": grade, "id": id}
        db.session.execute(query, params)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # RAW Query
        student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        return render_template('edit.html', student=student)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # before
    # app.run(host='0.0.0.0', port=5000, debug=True)
    # affer
    app.run(host='0.0.0.0', port=5000, debug=False)

