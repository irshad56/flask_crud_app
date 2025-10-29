# =====================================================
# 1️⃣ Importing necessary modules
# =====================================================
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# 🔹 Flask → lightweight web framework (used to create web apps quickly)
# 🔹 render_template → links backend (Python) with frontend (HTML via Jinja2)
# 🔹 request → captures data from forms (GET, POST)
# 🔹 redirect → sends user to another route after success/failure
# 🔹 url_for → dynamically generates URLs (avoids hardcoding links)

# =====================================================
# 2️⃣ Initialize Flask app and configure the database
# =====================================================
app = Flask(__name__)  # __name__ helps Flask locate templates/static folder

# Configure database path and settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
# 'sqlite:///' → means using SQLite file (lightweight, local DB)
# 'students.db' → the database file stored in your project folder

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Prevents SQLAlchemy from unnecessarily tracking every change (saves resources)

# Initialize ORM (Object Relational Mapper)
db = SQLAlchemy(app)
# ORM lets us use Python classes instead of writing raw SQL commands

# =====================================================
# 3️⃣ Define the Database Model (Table)
# =====================================================
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)          # Auto-increment unique ID
    name = db.Column(db.String(100), nullable=False)      # Cannot be empty
    email = db.Column(db.String(120), unique=True, nullable=False)  # Must be unique
    age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Student {self.name}>"
    # This special method helps when printing objects in debugging

# =====================================================
# 4️⃣ Create database tables (run once)
# =====================================================
with app.app_context():
    db.create_all()
# app_context() gives Flask access to configuration and database connections

# =====================================================
# 5️⃣ Home Page (Read Operation)
# =====================================================
@app.route('/')
def index():
    # Fetch all students
    students = Student.query.all()
    # Renders the list on index.html
    return render_template('index.html', students=students)

# =====================================================
# 6️⃣ Add Student (Create Operation)
# =====================================================
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        # Fetch form data
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']

        # Create new student object
        new_student = Student(name=name, email=email, age=age)

        # Add to session → commit to database
        db.session.add(new_student)
        db.session.commit()

        # Redirect to homepage
        return redirect(url_for('index'))

    # On GET → show empty add form
    return render_template('add.html')

# =====================================================
# 7️⃣ Edit Student (Update Operation)
# =====================================================
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    # Fetch student using ID or show 404 if not found
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        # Update values with form data
        student.name = request.form['name']
        student.email = request.form['email']
        student.age = request.form['age']

        # Check if email already exists for another student
        existing = Student.query.filter(
            Student.email == student.email,
            Student.id != id
        ).first()

        if existing:
            return render_template('edit.html', student=student, error="Email already exists!")

        try:
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            return render_template('edit.html', student=student, error=f"Update failed: {e}")

    # For GET → show pre-filled form
    return render_template('edit.html', student=student)

# =====================================================
# 8️⃣ Delete Student (Delete Operation)
# =====================================================
@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()

    # After deleting, reassign IDs sequentially
    students = Student.query.order_by(Student.id).all()
    for i, s in enumerate(students, start=1):
        s.id = i
    db.session.commit()

    return redirect(url_for('index'))

# =====================================================
# 9️⃣ Run Flask Server
# =====================================================
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
# debug=True → auto reloads the server when code changes

