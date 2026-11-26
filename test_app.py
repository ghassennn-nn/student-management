import unittest
from app import create_app

class StudentAppTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

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
        self.client.post("/students/1/delete")
        response = self.client.get("/")
        self.assertNotIn(b"Ahmed", response.data)

if __name__ == "__main__":
    unittest.main()
