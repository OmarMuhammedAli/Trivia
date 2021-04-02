from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from .models import setup_db, Question, Category
from .utils import *


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    ##### CORS SETUP #####
    # Allow all origins to access any endpoint by setting up CORS
    CORS(app, resources={'/*': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    ##### MAIN ENDPOINTS #####
    @app.route('/categories')
    def retrieve_categories():
        try:
            categories = Category.query.order_by(Category.id).all()

            if len(categories) < 1:
                abort(404)

            formatted_categories = format_category_list(categories)
            return jsonify({
                'success': True,
                'categories': formatted_categories,
                'total_categories': len(categories)
            })
        except:
            abort(500)

    @app.route('/questions')
    def retrieve_paginated_questions():

        try:
            questions = Question.query.order_by(Question.id).all()

            paginated_questions = paginate_questions(request, questions)
            if len(paginated_questions) < 1:
                abort(404)
            # print(paginated_questions)

            categories = Category.query.order_by(Category.id).all()
            formatted_categories = format_category_list(categories)

            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(questions),
                'current_category': None,
                'categories': formatted_categories
            }), 200
        except:
            abort(404)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        exists = True
        try:
            question = Question.query.get(question_id)
            if question is None:
                exists = False
                abort(404)

            question.delete()
        except:
            if not exists:
                abort(404)
            else:
                abort(500)

        return jsonify({
            'success': True,
            'total_question': len(Question.query.all())
        }), 200

    @app.route('/questions', methods=['POST'])
    def submit_question():

        question_objects = Question.query.all()
        questions_literals = [qn.format()['question']
                              for qn in question_objects]
        data = request.get_json()
        question = data.get('question', '')
        answer = data.get('answer', '')
        category = data.get('category', '')
        difficulty = data.get('difficulty', '')
        if len(question) < 1 or len(answer) < 1:
            abort(400)
        # Prevent addition of already existing questions
        if question in questions_literals:
            abort(400)
        new_question_id = None

        try:
            new_question = Question(
                question,
                answer,
                category,
                difficulty
            )
            new_question.insert()
            new_question_id = new_question.id

        except:
            abort(422)

        return jsonify({
            'success': True,
            'total_questions': len(Question.query.all()),
            'question_id': new_question_id
        }), 201

    @app.route('/search', methods=['POST'])
    def search_for_a_question():

        try:
            data = request.get_json()
            search_term = data.get('searchTerm', '')
            if len(search_term) < 1:
                abort(422)

            questions = Question.query.order_by(Question.id).filter(
                Question.question.ilike(f'%{search_term}%')).all()
            if len(questions) < 1:
                abort(404)
            formatted_questions = paginate_questions(request, questions)

            categories = Category.query.order_by(Category.id).all()
            formatted_categories = format_category_list(categories)
        except:
            abort(404)

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'categories': formatted_categories,
            'current_categroy': None
        }), 201

    @app.route('/categories/<int:category_id>/questions', methods=["GET"])
    def retrieve_questions_by_category(category_id):

        try:
            category = Category.query.get(category_id).type

            questions = Question.query.order_by(Question.id).filter(
                Question.category == str(category_id)).all()
            if len(questions) < 1:
                abort(404)

            formatted_question = paginate_questions(request, questions)
        except:
            abort(404)

        return jsonify({
            'success': True,
            'questions': formatted_question,
            'current_category': category,
            'total_questions': len(questions)
        }), 200

    @app.route('/quizzes', methods=['POST'])
    def get_random_question():

        data = request.get_json()
        previous_questions = data.get('previous_questions', None)
        category = data.get('quiz_category', None)

        if previous_questions is None or category is None:
            abort(400)
        questions = None
        question = None
        if category['id'] == 0:  # "All" category is selected
            questions = Question.query.all()
        else:
            questions = Question.query.filter(
                Question.category == category['id']).all()

        if len(questions) < 1:
            # If the selected category has no questions, the UI reflects that.
            abort(404)

        while True:
            # This condition is crucial for categories with question < 5
            if len(previous_questions) == len(questions):
                return jsonify({
                    'success': True
                }), 201
            # Get random question
            question = questions[random.randint(0, len(questions) - 1)]
            if question.id not in previous_questions:
                break

        return jsonify({
            'success': True,
            'question': question.format()
        }), 201

    ##### ERROR HANDLING #####

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
        }), 500

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(400)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request',
        }), 400

    return app
