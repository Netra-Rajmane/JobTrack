from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from datetime import date

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")
DATABASE = os.path.join(app.instance_path, "jobtracker.db")
STATUSES = ["Applied", "Shortlisted", "Interview", "Selected", "Rejected"]
JOB_TYPES = ["Full-time", "Part-time", "Internship", "Remote", "Contract"]

os.makedirs(app.instance_path, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                location TEXT DEFAULT '',
                salary TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Applied',
                applied_date TEXT NOT NULL,
                job_type TEXT DEFAULT '',
                job_link TEXT DEFAULT '',
                notes TEXT DEFAULT ''
            )
        """)

@app.route("/health")
def health():
    return jsonify(status="healthy", app="JobTrack")

@app.route("/")
def dashboard():
    with get_db_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        interviews = conn.execute("SELECT COUNT(*) FROM applications WHERE status='Interview'").fetchone()[0]
        selected = conn.execute("SELECT COUNT(*) FROM applications WHERE status='Selected'").fetchone()[0]
        rejected = conn.execute("SELECT COUNT(*) FROM applications WHERE status='Rejected'").fetchone()[0]
        recent = conn.execute("SELECT * FROM applications ORDER BY id DESC LIMIT 5").fetchall()
        status_counts = [
            {"status": row["status"], "count": row["count"]}
            for row in conn.execute(
                "SELECT status, COUNT(*) AS count FROM applications GROUP BY status"
            ).fetchall()
        ]
    stats = {"total": total, "interviews": interviews, "selected": selected, "rejected": rejected}
    return render_template("dashboard.html", stats=stats, recent=recent, status_counts=status_counts)

@app.route("/applications")
def applications():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    query = "SELECT * FROM applications WHERE 1=1"
    params = []
    if search:
        query += " AND (company LIKE ? OR role LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if status in STATUSES:
        query += " AND status=?"
        params.append(status)
    query += " ORDER BY id DESC"
    with get_db_connection() as conn:
        records = conn.execute(query, params).fetchall()
    return render_template("applications.html", applications=records, statuses=STATUSES,
                           search=search, selected_status=status)

@app.route("/add", methods=["GET", "POST"])
def add_application():
    if request.method == "POST":
        data = read_form()
        if not data["company"] or not data["role"]:
            flash("Company name and job role are required.", "error")
            return render_template("add_application.html", statuses=STATUSES,
                                   job_types=JOB_TYPES, today=date.today().isoformat(),
                                   application=data)
        if data["status"] not in STATUSES:
            data["status"] = "Applied"
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO applications
                (company, role, location, salary, status, applied_date, job_type, job_link, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(data[k] for k in ["company", "role", "location", "salary", "status",
                                         "applied_date", "job_type", "job_link", "notes"]))
        flash("Application added successfully.", "success")
        return redirect(url_for("applications"))
    return render_template("add_application.html", statuses=STATUSES, job_types=JOB_TYPES,
                           today=date.today().isoformat(), application=None)

def read_form():
    return {
        "company": request.form.get("company", "").strip(),
        "role": request.form.get("role", "").strip(),
        "location": request.form.get("location", "").strip(),
        "salary": request.form.get("salary", "").strip(),
        "status": request.form.get("status", "Applied"),
        "applied_date": request.form.get("applied_date", date.today().isoformat()),
        "job_type": request.form.get("job_type", "").strip(),
        "job_link": request.form.get("job_link", "").strip(),
        "notes": request.form.get("notes", "").strip()
    }

@app.route("/edit/<int:application_id>", methods=["GET", "POST"])
def edit_application(application_id):
    with get_db_connection() as conn:
        record = conn.execute("SELECT * FROM applications WHERE id=?", (application_id,)).fetchone()
    if record is None:
        flash("Application not found.", "error")
        return redirect(url_for("applications"))
    if request.method == "POST":
        data = read_form()
        if not data["company"] or not data["role"] or data["status"] not in STATUSES:
            flash("Please provide a company, role and valid status.", "error")
            return redirect(url_for("edit_application", application_id=application_id))
        with get_db_connection() as conn:
            conn.execute("""
                UPDATE applications SET company=?, role=?, location=?, salary=?, status=?,
                applied_date=?, job_type=?, job_link=?, notes=? WHERE id=?
            """, tuple(data[k] for k in ["company", "role", "location", "salary", "status",
                                         "applied_date", "job_type", "job_link", "notes"]) + (application_id,))
        flash("Application updated successfully.", "success")
        return redirect(url_for("applications"))
    return render_template("add_application.html", statuses=STATUSES, job_types=JOB_TYPES,
                           today=date.today().isoformat(), application=record)

@app.route("/delete/<int:application_id>", methods=["POST"])
def delete_application(application_id):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM applications WHERE id=?", (application_id,))
    flash("Application deleted.", "success")
    return redirect(url_for("applications"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("FLASK_DEBUG") == "1")
else:
    init_db()
