import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from sqlalchemy.sql.expression import func
from flask_cors import CORS

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={"/": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Acces-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
        )

        return response

    @app.route("/categories")
    def get_categories():
        categories = Category.query.all()

        if len(categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": {category.id: category.type for category in categories},
            }
        )

    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):
        categories = Category.query.count()

        # throw error for inexistent categories
        if category_id < 1 or category_id > categories:
            abort(400)

        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        paginated_questions = (
            Question.query.filter(Question.category == category_id)
            .order_by(Question.id)
            .paginate(page, QUESTIONS_PER_PAGE, error_out=False)
        )

        # throw error for inexistent resources
        if paginated_questions.total == 0:
            abort(404)

        formatted_questions = list(map(Question.format, paginated_questions.items))

        return jsonify({"success": True, "questions": formatted_questions})

    @app.route("/questions")
    def get_questions():
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        paginated_questions = Question.query.order_by(Question.id).paginate(
            page, QUESTIONS_PER_PAGE, error_out=False
        )

        formatted_questions = list(map(Question.format, paginated_questions.items))
        categories = Category.query.all()

        if len(formatted_questions) == 0 or len(categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": formatted_questions,
                "total_questions": paginated_questions.total,
                "categories": {category.id: category.type for category in categories},
                "current_category": None,
            }
        )

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        try:
            question = body.get("question")
            answer = body.get("answer")
            category = body.get("category")
            difficulty = body.get("difficulty")

            if (
                (question is None)
                or (answer is None)
                or (category is None)
                or (difficulty is None)
            ):
                abort(400)

            question = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty,
            )

            question.insert()

            return jsonify({"success": True, "created": question.id})
        except:
            abort(400)

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        question.delete()
        return jsonify({"success": True, "deleted": question_id})

    @app.route("/search", methods=["POST"])
    def get_search_results():
        body = request.get_json()
        page = body.get("page", 1)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        search_term = body.get("search_term")

        paginated_questions = (
            Question.query.filter(Question.question.ilike(f"%{search_term}%"))
            .order_by(Question.id)
            .paginate(page, QUESTIONS_PER_PAGE, error_out=False)
        )

        formatted_questions = list(map(Question.format, paginated_questions.items))
        categories = Category.query.all()

        if len(formatted_questions) == 0 or len(categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": formatted_questions,
                "total_questions": paginated_questions.total,
                "categories": {category.id: category.type for category in categories},
                "current_category": None,
            }
        )

    @app.route("/quizzes", methods=["POST"])
    def get_random_question():
        body = request.get_json()

        previous_questions = body.get("previous_questions")
        quiz_category = body.get("quiz_category")

        if (previous_questions is None) or (quiz_category is None):
            abort(400)

        try:
            quiz_category_id = (
                ["1", "2", "3", "4", "5", "6"]
                # A zero-th id means all categories are included
                if quiz_category.get("id") == 0
                else quiz_category.get("id")
            )

            question = (
                Question.query.filter(
                    and_(
                        ~Question.id.in_(previous_questions),
                        Question.category.in_(quiz_category_id),
                    )
                )
                .order_by(func.random())
                .first()
            )

            return jsonify({"success": True, "question": question.format()})
        except:
            abort(404)

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "Bad Request"}),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Not Found"}),
            404,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "Method Not Allowed"}),
            405,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "Internal Server Error"}
            ),
            500,
        )

    return app
