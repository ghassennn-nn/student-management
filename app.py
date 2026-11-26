from flask import Flask, render_template, request, redirect, url_for


def create_app():
    app = Flask(__name__)

    students = []
    next_id = 1

    @app.route("/")
    def index():
        return render_template("index.html", students=students)

    @app.route("/students", methods=["POST"])
    def add_student():
        nonlocal next_id

        name = request.form.get("name", "").strip()

        if not name:
            return "Name is required", 400

        students.append({
            "id": next_id,
            "name": name
        })

        next_id += 1
        return redirect(url_for("index"))

    @app.route("/students/<int:student_id>/delete", methods=["POST"])
    def delete_student(student_id):
        students[:] = [
            student for student in students
            if student["id"] != student_id
        ]

        return redirect(url_for("index"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
