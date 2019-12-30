import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from enum import Enum
import random

from models import setup_db, Question, Category
from .utils import get_questions_list

QUESTIONS_PER_PAGE = 10


class StatusCode(Enum):
    """Enum to maintain status codes."""

    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_405_METHOD_NOT_ALLOWED = 405
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_500_INTERNAL_SERVER_ERROR = 500


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        """
        Handler for after a request has been made.

        :param response:
        """
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization'
        )
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        )
        return response

    @app.route('/categories')
    def get_categories():
        """
        Return the categories with id and type.

        :return:
        """
        try:
            result = {
                "success": True,
                "categories": {
                    category.id: category.type \
                        for category in Category.query.all()
                }
            }
            return jsonify(result)
        except Exception as exp:
            abort(exp.code)


    @app.route('/questions')
    def get_questions():
        """
        Get questions for a given page.

        :return:
        """
        try:
            page = request.args.get('page', 1, type=int)
            questions, total_questions_count = get_questions_list(page=page)
            categories = {
                category.id: category.type for category in Category.query.all()
            }

            if len(questions) == 0:
                abort(StatusCode.HTTP_404_NOT_FOUND.value)

            return jsonify({
                'success': True,
                'current_category': None,
                'categories': categories,
                'questions': questions,
                'total_questions': total_questions_count
            })
        except Exception as exp:
            abort(exp.code)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        Delete question by given id.

        :param question_id:
        :return:
        """
        try:
            question = Question.query.get(question_id)
            if not question:
                abort(StatusCode.HTTP_404_NOT_FOUND.value)

            question.delete()
            return jsonify({
                'success': True
            }), StatusCode.HTTP_204_NO_CONTENT.value
        except Exception as exp:
            abort(exp.code)

    @app.route('/questions', methods=['POST'])
    def add_question():
        """
        Add a question to database.

        :return:
        """
        try:
            question = request.get_json()

            if not question:
                abort(StatusCode.HTTP_400_BAD_REQUEST.value)

            question = Question(**question)
            question.insert()

            return jsonify({
                'success': True, 'id': question.id
            }), StatusCode.HTTP_201_CREATED.value
        except Exception as exp:
            abort(exp.code)

    @app.route('/questions/filter', methods=['POST'])
    def search_questions():
        """
        Return the list of questions after filteration.

        :return:
        """
        try:
            request_data = request.get_json()
            questions, total_questions_count = get_questions_list(
                query=request_data.get('searchTerm')
            )
            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': total_questions_count,
            })

        except Exception as exp:
            abort(exp.code)

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        """
        Get questions by category.

        :param category_id:
        :return:
        """
        try:
            category = Category.query.get(category_id)

            if not category:
                abort(StatusCode.HTTP_404_NOT_FOUND.value)

            questions, total_questions_count = get_questions_list(
                category_id=category_id
            )
            return jsonify({
                "success": True,
                "questions": questions,
                "total_questions": total_questions_count,
                "current_category": category.format(),
            })

        except Exception as exp:
            abort(exp.code)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        """
        Play quiz route to get questions for quizzes.
        :return:
        """
        try:
            request_data = request.get_json()
            previous_questions = request_data.get('previous_questions', [])
            quiz_category = request_data.get('quiz_category')

            if not quiz_category:
                abort(StatusCode.HTTP_400_BAD_REQUEST.value)

            category_id = quiz_category.get('id', None)
            questions, _ = get_questions_list(category_id=category_id)

            filtered_questions = [
                question for question in questions \
                    if question.get('id') not in previous_questions
            ]

            random_question = random.choice(filtered_questions) \
                if filtered_questions else None

            return jsonify({
                'question': random_question, 'success': True
            })
        except Exception as exp:
            abort(exp.code)

    @app.errorhandler(StatusCode.HTTP_400_BAD_REQUEST.value)
    def bad_request(error):
        """
        Error handler for bad request with status code 400.

        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': StatusCode.HTTP_400_BAD_REQUEST.value,
            'message': StatusCode.HTTP_400_BAD_REQUEST.name
        }), StatusCode.HTTP_400_BAD_REQUEST.value

    @app.errorhandler(StatusCode.HTTP_401_UNAUTHORIZED.value)
    def unauthorized(error):
        """
        Error handler for unauthorized with status code 401.

        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': StatusCode.HTTP_401_UNAUTHORIZED.value,
            'message': StatusCode.HTTP_401_UNAUTHORIZED.name
        }), StatusCode.HTTP_401_UNAUTHORIZED.value

    @app.errorhandler(StatusCode.HTTP_403_FORBIDDEN.value)
    def forbidden(error):
        """
        Error handler for forbidden with status code 403.

        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': StatusCode.HTTP_403_FORBIDDEN.value,
            'message': StatusCode.HTTP_403_FORBIDDEN.name
        }), StatusCode.HTTP_403_FORBIDDEN.value

    @app.errorhandler(StatusCode.HTTP_404_NOT_FOUND.value)
    def not_found(error):
        """
        Error handler for not found with status code 404.

        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': StatusCode.HTTP_404_NOT_FOUND.value,
            'message': StatusCode.HTTP_404_NOT_FOUND.name
        }), StatusCode.HTTP_404_NOT_FOUND.value

    @app.errorhandler(StatusCode.HTTP_405_METHOD_NOT_ALLOWED.value)
    def method_not_allowed(error):
        """
        Error handler for method not allowed with status code 405.

        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': StatusCode.HTTP_405_METHOD_NOT_ALLOWED.value,
            'message': StatusCode.HTTP_405_METHOD_NOT_ALLOWED.name
        }), StatusCode.HTTP_405_METHOD_NOT_ALLOWED.value

    @app.errorhandler(StatusCode.HTTP_422_UNPROCESSABLE_ENTITY.value)
    def unprocessable_entity(error):
        """
        Error handler for unprocessable entity with status code 422.

        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': StatusCode.HTTP_422_UNPROCESSABLE_ENTITY.value,
            'message': StatusCode.HTTP_422_UNPROCESSABLE_ENTITY.name
        }), StatusCode.HTTP_422_UNPROCESSABLE_ENTITY.value

    @app.errorhandler(StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.value)
    def internal_server_error(error):
        """
        Error handler for internal server error with status code 500.

        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.value,
            'message': StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.name
        }), StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.value

    return app
