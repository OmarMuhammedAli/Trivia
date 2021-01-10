import os
from flask import Flask, json, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from ..models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def format_category_list(categories):
    cats = dict()
    for category in categories:
        cats[category.id] = category.type

    return cats


def paginate_questions(request, questions):
    """
    A helper method to return questions paginated
    """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    current_questions = [question.format()
                         for question in questions][start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # Allow all origins to access any endpoint by setting up CORS
    CORS(app, resources={'/*': {'origins': '*'}})
    '''
  @TODO-: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs(Done!)
  '''
    '''
  @TODO-: Use the after_request decorator to set Access-Control-Allow(Done!)
  '''
    # This method gets triggred after a request is made to the server. It add Allow-Access-Control headers.
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    '''
  @TODO-: 
  Create an endpoint to handle GET requests 
  for all available categories.(Done!)
  '''
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

    '''
  @TODO-: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. (Done!)
  '''
    @app.route('/questions')
    def retrieve_paginated_questions():

        try:
            questions = Question.query.order_by(Question.id).all()
            if len(questions) < 1:
                abort(404)
            paginated_questions = paginate_questions(request, questions)
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
            abort(500)

    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        exists = True
        try: 
            question = Question.query.get(question_id)
            if question is None: 
                abort(404)
                exists = False
            question.delete()
        except: 
            if not exists: abort(404)
            else: abort(500)
        
        return jsonify({
            'success': True,
            'total_question': len(Question.query.all())
        }), 200
    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(500)
    def server_error(erro):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        })
    return app
