
# Student Performance Tracker (Flask + SQLite)

A web app to add students, record subject-wise grades, view details, compute averages, and find toppers.

## Features
- Add students (unique roll number)
- Add grades per subject (0–100 validation)
- View student details and average
- Search students
- Class average dashboard
- Topper by subject
- SQLite persistence

## Run Locally
```bash
# 1) Create venv and install deps
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) Initialize DB and run
python app.py
# visit http://127.0.0.1:5000
```

Alternatively initialize via Flask CLI:
```bash
flask --app app init-db
flask --app app run
```

## Deploy (Heroku-style)
- `requirements.txt` and `Procfile` included.
- Set `WEB_CONCURRENCY` if needed.
- Entry point: `app:app`

## Project Structure
```
student_tracker/
  app.py
  templates/
    base.html, index.html, list_students.html, add_student.html,
    student_details.html, add_grades.html, average.html, topper.html
  static/
    style.css
  requirements.txt
  Procfile
  README.md
```

## Notes
- Default SECRET_KEY is for demo; set a secure value in production.
