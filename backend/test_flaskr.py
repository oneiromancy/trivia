import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client

        # Database Credentials
        self.database_dialect = "postgres"
        self.database_username = "postgres"
        self.database_password = "postgres"
        self.database_hostname = "localhost"
        self.database_port = "5432"
        self.database_name = "trivia_test"

        self.database_path = "{}://{}:{}@{}:{}/{}".format(
            self.database_dialect,
            self.database_username,
            self.database_password,
            self.database_hostname,
            self.database_port,
            self.database_name,
        )

        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "What year was the first Toy Story film released in cinemas?",
            "answer": "1995",
            "category": "5",
            "difficulty": "2",
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    def test_get_questions_by_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))

    def test_400_get_questions_by_inexistent_category(self):
        res = self.client().get("/categories/8/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))
        self.assertEqual(data["current_category"], None)

    def test_404_get_questions_beyond_valid_page(self):
        res = self.client().get("/questions?page=101")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not Found")

    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        question = (
            Question.query.filter_by(question=self.new_question["question"])
            .order_by(Question.id.desc())
            .first()
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["created"], question.id)

    def test_400_missing_arguments_to_create_new_question(self):
        # Missing column
        res = self.client().post(
            "/questions", json={"question": self.new_question["question"]}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")

    def test_delete_question(self):
        deleted_question_id = 40

        res = self.client().delete(f"/questions/{deleted_question_id}")
        data = json.loads(res.data)

        question = Question.query.get(deleted_question_id)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], deleted_question_id)
        self.assertEqual(question, None)

    def test_404_delete_question(self):
        deleted_question_id = 1000

        res = self.client().delete(f"/questions/{deleted_question_id}")
        data = json.loads(res.data)

        question = Question.query.get(deleted_question_id)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not Found")
        self.assertEqual(question, None)

    def test_get_search_results(self):
        res = self.client().post("/search", json={"search_term": "title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))
        self.assertEqual(data["current_category"], None)
        self.assertTrue(data["total_questions"] > 0)

    def test_404_get_search_results_beyond_valid_page(self):
        res = self.client().post("/search", json={"search_term": "title", "page": 1000})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not Found")

    def test_get_random_question(self):
        res = self.client().post(
            "/quizzes",
            json={
                "previous_questions": [2, 4],
                "quiz_category": {"id": "5", "type": "Entertainment"},
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"] != None)

    def test_400_get_random_question(self):
        res = self.client().post("/quizzes", json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
