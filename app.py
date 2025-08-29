from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret'  # replace in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- Models --------------------
class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    grades = db.relationship("Grade", backref="student", cascade="all, delete-orphan")

    def average(self):
        if not self.grades:
            return None
        return sum(g.score for g in self.grades) / len(self.grades)

class Grade(db.Model):
    __tablename__ = "grades"
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Float, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)

# -------------------- CLI to init DB --------------------
@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Initialized the database.")


# -------------------- Routes --------------------
@app.route("/")
def index():
    total_students = Student.query.count()
    total_grades = Grade.query.count()
    class_avg = None
    if total_grades > 0:
        class_avg = db.session.query(func.avg(Grade.score)).scalar()
    return render_template("index.html",
                           total_students=total_students,
                           total_grades=total_grades,
                           class_avg=class_avg)

@app.route("/students")
def list_students():
    q = request.args.get("q", "").strip()
    if q:
        students = Student.query.filter(
            (Student.name.ilike(f"%{q}%")) | (Student.roll_number.ilike(f"%{q}%"))
        ).order_by(Student.name).all()
    else:
        students = Student.query.order_by(Student.name).all()
    return render_template("list_students.html", students=students, q=q)

@app.route("/students/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        roll = request.form.get("roll_number", "").strip()
        if not name or not roll:
            flash("Name and Roll Number are required.", "error")
            return redirect(url_for("add_student"))
        # ensure unique roll
        if Student.query.filter_by(roll_number=roll).first():
            flash("Roll number must be unique.", "error")
            return redirect(url_for("add_student"))
        s = Student(name=name, roll_number=roll)
        db.session.add(s)
        db.session.commit()
        flash("Student added.", "success")
        return redirect(url_for("list_students"))
    return render_template("add_student.html")

@app.route("/students/<int:student_id>")
def student_details(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template("student_details.html", student=student)

@app.route("/students/<int:student_id>/delete", methods=["POST"])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted.", "success")
    return redirect(url_for("list_students"))

@app.route("/grades/add/<int:student_id>", methods=["GET", "POST"])
def add_grades(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == "POST":
        subject = request.form.get("subject", "").strip()
        try:
            score = float(request.form.get("score", "").strip())
        except ValueError:
            flash("Score must be a number.", "error")
            return redirect(url_for("add_grades", student_id=student.id))

        if not subject:
            flash("Subject is required.", "error")
            return redirect(url_for("add_grades", student_id=student.id))
        if score < 0 or score > 100:
            flash("Score must be between 0 and 100.", "error")
            return redirect(url_for("add_grades", student_id=student.id))

        g = Grade(subject=subject, score=score, student=student)
        db.session.add(g)
        db.session.commit()
        flash("Grade added.", "success")
        return redirect(url_for("student_details", student_id=student.id))
    return render_template("add_grades.html", student=student)

@app.route("/grades/<int:grade_id>/delete", methods=["POST"])
def delete_grade(grade_id):
    grade = Grade.query.get_or_404(grade_id)
    sid = grade.student_id
    db.session.delete(grade)
    db.session.commit()
    flash("Grade deleted.", "success")
    return redirect(url_for("student_details", student_id=sid))

@app.route("/reports/average")
def average_report():
    students = Student.query.order_by(Student.name).all()
    return render_template("average.html", students=students)

@app.route("/reports/topper")
def topper_report():
    subject = request.args.get("subject", "").strip()
    topper = None
    if subject:
        topper = (
            db.session.query(Student, Grade)
            .join(Grade)
            .filter(Grade.subject.ilike(subject))
            .order_by(Grade.score.desc())
            .first()
        )
    subjects = [row[0] for row in db.session.query(Grade.subject).distinct().all()]
    return render_template("topper.html", subject=subject, topper=topper, subjects=subjects)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
