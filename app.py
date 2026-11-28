
import os
import sqlite3
from datetime import datetime
from contextlib import contextmanager

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, abort
)


def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = "studenthub-secret-key"

    app.config["DATABASE"] = os.path.join(
        app.instance_path, "students.db"
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    @contextmanager
    def database():
        db = sqlite3.connect(app.config["DATABASE"])
        db.row_factory = sqlite3.Row
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def init_db():
        with database() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT DEFAULT '',
                    course TEXT DEFAULT '',
                    status TEXT DEFAULT 'Active',
                    created_at TEXT NOT NULL
                )
            """)

    init_db()

    @app.route("/")
    def index():
        search = request.args.get("search", "").strip()

        with database() as db:
            if search:
                students = db.execute("""
                    SELECT * FROM students
                    WHERE name LIKE ?
                    OR email LIKE ?
                    OR course LIKE ?
                    ORDER BY id DESC
                """, (
                    f"%{search}%",
                    f"%{search}%",
                    f"%{search}%"
                )).fetchall()
            else:
                students = db.execute("""
                    SELECT * FROM students
                    ORDER BY id DESC
                """).fetchall()

            stats = db.execute("""
                SELECT
                    COUNT(*) AS total,
                    COALESCE(SUM(
                        CASE WHEN status = 'Active' THEN 1 ELSE 0 END
                    ), 0) AS active,
                    COALESCE(SUM(
                        CASE WHEN status = 'Inactive' THEN 1 ELSE 0 END
                    ), 0) AS inactive
                FROM students
            """).fetchone()

        return render_template(
            "index.html",
            students=students,
            search=search,
            stats=stats
        )

    @app.route("/students", methods=["POST"])
    def add_student():
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        course = request.form.get("course", "").strip()
        status = request.form.get("status", "Active")

        if not name:
            return "Name is required", 400

        if status not in ("Active", "Inactive"):
            status = "Active"

        with database() as db:
            db.execute("""
                INSERT INTO students
                (name, email, course, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                name,
                email,
                course,
                status,
                datetime.now().strftime("%Y-%m-%d")
            ))

        flash("Student added successfully!", "success")
        return redirect(url_for("index"))

    @app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
    def edit_student(student_id):
        with database() as db:
            student = db.execute(
                "SELECT * FROM students WHERE id = ?",
                (student_id,)
            ).fetchone()

        if student is None:
            abort(404)

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            course = request.form.get("course", "").strip()
            status = request.form.get("status", "Active")

            if not name:
                return "Name is required", 400

            if status not in ("Active", "Inactive"):
                status = "Active"

            with database() as db:
                db.execute("""
                    UPDATE students
                    SET name = ?, email = ?, course = ?, status = ?
                    WHERE id = ?
                """, (name, email, course, status, student_id))

            flash("Student updated successfully!", "success")
            return redirect(url_for("index"))

        return render_template("edit.html", student=student)

    @app.route("/students/<int:student_id>/delete", methods=["POST"])
    def delete_student(student_id):
        with database() as db:
            db.execute(
                "DELETE FROM students WHERE id = ?",
                (student_id,)
            )

        flash("Student deleted successfully!", "success")
        return redirect(url_for("index"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
