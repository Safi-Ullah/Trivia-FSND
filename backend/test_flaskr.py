import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app, StatusCode
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    question = {
        "question": "Test 1",
        "answer": "Answer 1",
        "category": 1,
        "difficulty": 1
    }

    def setUp(self):
        """
        Setup db.

        :param self:
        """
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name
        )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """
        Executed after reach test

        :return:
        """
        pass

    def test_get_categories_success(self):
        """
        Success test case for get categories route.

        :return:
        """
        response = self.client().get('/categories')
        json_data = response.get_json()
        self.assertEqual(response.status_code, StatusCode.HTTP_200_OK.value)
        self.assertTrue(json_data.get('success'))

    def test_get_categories_failed(self):
        """
        Fail test case for get categories route.

        :return:
        """
        response = self.client().post('/categories')
        json_data = response.get_json()
        self.assertEqual(
            response.status_code,
            StatusCode.HTTP_405_METHOD_NOT_ALLOWED.value
        )
        self.assertFalse(json_data.get('success'))

    def test_get_questions_success(self):
        """
        Success case for get questions.

        :return:
        """
        response = self.client().get('/questions')
        json_data = response.get_json()
        self.assertEqual(response.status_code, StatusCode.HTTP_200_OK.value)
        self.assertTrue(json_data.get('success'))

    def test_get_questions_failed(self):
        """
        Fail case for get questions.

        :return:
        """
        response = self.client().get('/questions?page=-1000')
        json_data = response.get_json()
        self.assertEqual(
            response.status_code, StatusCode.HTTP_404_NOT_FOUND.value
        )
        self.assertFalse(json_data.get('success'))

    def test_delete_question_success(self):
        """
        Success case of delete question test case.

        :return:
        """
        response = self.client().post('/questions', json=self.question)
        json_data = response.get_json()
        response = self.client().delete(f'/questions/{json_data.get("id")}')

    def test_delete_question_failed_method_not_allowed(self):
        """
        Method not allowed failed case of delete question test case.

        :return:
        """
        response = self.client().get('/questions/14')
        json_data = response.get_json()
        self.assertFalse(json_data.get('success'))

    def test_delete_question_failed_not_found(self):
        """
        Not found failed case of delete question test case.

        :return:
        """
        response = self.client().delete('/questions/-1000')
        json_data = response.get_json()
        self.assertEqual(
            response.status_code, StatusCode.HTTP_404_NOT_FOUND.value
        )
        self.assertFalse(json_data.get('success'))

    def test_add_question_success(self):
        """
        Success case of add question test case.

        :return:
        """
        response = self.client().post('/questions', json=self.question)
        json_data = response.get_json()
        self.assertEqual(
            response.status_code, StatusCode.HTTP_201_CREATED.value
        )
        self.assertTrue(json_data.get('success'))

    def test_add_question_failed_method_not_allowed(self):
        """
        Fail case of add question test case with method not allowed error.

        :return:
        """
        response = self.client().put('/questions', json={})
        json_data = response.get_json()
        self.assertEqual(
            response.status_code, StatusCode.HTTP_405_METHOD_NOT_ALLOWED.value
        )
        self.assertFalse(json_data.get('success'))

    def test_add_question_failed_bad_request(self):
        """
        Fail case of add question test case with bad request error.

        :return:
        """
        response = self.client().post('/questions', json={})
        json_data = response.get_json()
        self.assertEqual(
            response.status_code, StatusCode.HTTP_400_BAD_REQUEST.value
        )
        self.assertFalse(json_data.get('success'))

    def test_search_questions_success(self):
        """
        Success case of search questions api.

        :return:
        """
        data = {
            "searchTerm": "The"
        }
        response = self.client().post('/questions/filter', json=data)
        json_data = response.get_json()
        self.assertEqual(response.status_code, StatusCode.HTTP_200_OK.value)
        self.assertTrue(json_data.get('success'))

    def test_search_questions_failed(self):
        """
        Success case of search questions api with method not allowed error.

        :return:
        """
        response = self.client().get('/questions/filter', json={})
        json_data = response.get_json()
        self.assertEqual(
            response.status_code, StatusCode.HTTP_405_METHOD_NOT_ALLOWED.value
        )
        self.assertFalse(json_data.get('success'))

    def test_get_questions_by_category_success(self):
        """
        Success case for get questions by category.

        :return:
        """
        response = self.client().get('/categories/1/questions')
        json_data = response.get_json()
        self.assertEqual(response.status_code, StatusCode.HTTP_200_OK.value)
        self.assertTrue(json_data.get('success'))

    def test_get_questions_by_category_failed_method_not_allowed(self):
        """
        Fail case for get questions by category with method not allowed error.

        :return:
        """
        response = self.client().post('/categories/1/questions')
        json_data = response.get_json()
        self.assertEqual(
            response.status_code, StatusCode.HTTP_405_METHOD_NOT_ALLOWED.value
        )
        self.assertFalse(json_data.get('success'))

    def test_get_questions_by_category_not_found(self):
        """
        Fail case for get questions by category with method not found.

        :return:
        """
        response = self.client().get('/categories/1000/questions')
        json_data = response.get_json()
        self.assertEqual(
            response.status_code, StatusCode.HTTP_404_NOT_FOUND.value
        )
        self.assertFalse(json_data.get('success'))

    def test_play_quiz_success(self):
        """
        Success case for play quiz api.

        :return:
        """
        data = {
            "quiz_category": {
                "id": 1
            },
            "previous_questions": []
        }
        response = self.client().post('/quizzes', json=data)
        json_data = response.get_json()
        self.assertEqual(response.status_code, StatusCode.HTTP_200_OK.value)
        self.assertTrue(json_data.get('success'))

    def test_play_quiz_failed_method_not_allowed(self):
        """
        Fail case for play quiz api with method not allowed error.

        :return:
        """
        response = self.client().get('/quizzes', json={})
        json_data = response.get_json()
        self.assertEqual(response.status_code, StatusCode.HTTP_405_METHOD_NOT_ALLOWED.value)
        self.assertFalse(json_data.get('success'))

    def test_play_quiz_failed_bad_request(self):
        """
        Fail case for play quiz api with method bad request.

        :return:
        """
        response = self.client().post('/quizzes', json={})
        json_data = response.get_json()
        self.assertEqual(response.status_code, StatusCode.HTTP_400_BAD_REQUEST.value)
        self.assertFalse(json_data.get('success'))

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
