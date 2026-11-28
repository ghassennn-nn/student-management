import unittest
import os
import tempfile
from app import create_app


class StudentAppTests(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()

        self.app = create_app({
            "TESTING": True,
            "DATABASE": self.temp_db.name
        })

        self.client = self.app.test_client()

    def tearDown(self):
        os.unlink(self.temp_db.name)

    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_add_student(self):
        response = self.client.post(
            "/students",
            data={"name": "Ahmed"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Ahmed", response.data)

    def test_empty_student_name(self):
        response = self.client.post(
            "/students",
            data={"name": ""}
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_student(self):
        self.client.post("/students", data={"name": "Ahmed"})

        with self.app.app_context():
            import sqlite3
            db = sqlite3.connect(self.temp_db.name)
            student_id = db.execute(
                "SELECT id FROM students WHERE name = 'Ahmed'"
            ).fetchone()[0]
            db.close()

        self.client.post(f"/students/{student_id}/delete")

        response = self.client.get("/")
        self.assertNotIn(b"Ahmed", response.data)


if __name__ == "__main__":
    unittest.main()
