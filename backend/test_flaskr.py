import os
import sys
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from flaskr.models import setup_db, Question, Category

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}@{}/{}".format(
            'horizon:0105415595', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # sample question for use in tests
        self.new_question = {
            'question': 'In which year did the Egyptian revolution "25th of January" occur?',
            'answer': '2011',
            'difficulty': 2,
            'category': '4'
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

    def test_retrieve_paginated_questions(self):
        """Tests success of question pagination"""

        # get response and load data
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(data['success'], True)
        self.assertEqual(response.status_code, 200)
        
        # check that total_questions and questions return data
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        

    def test_retrieve_paginated_question_fails_404(self):
        """Tests failure 404 question pagination"""

        # send request with bad page data, load response
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_delete_question_success(self):
        """Tests question deletion success"""
        
        # create a new question to be deleted
        question = Question(
            question=self.new_question['question'], 
            answer=self.new_question['answer'], 
            category=self.new_question['category'], 
            difficulty=self.new_question['difficulty']
            )
        question.insert()

        # total questions before deletion
        questions_before = Question.query.all()
        question_id = question.id

        # delete the question and store response
        response = self.client().delete(f'/questions/{question_id}')
        data = json.loads(response.data)

        # total questions after deletion
        questions_after = Question.query.all()

        # check status code and success message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # Check difference in total question after deletion
        self.assertTrue(len(questions_before) - len(questions_after) == 1)

        # check if question equals None after deletion
        question = Question.query.get(question_id)
        self.assertEqual(question, None)


    def test_delete_question_fails_404(self):
        """Tests if deletion of a non-existing question fails"""

        # Delete non-existing question and store response
        response = self.client().delete(f'questions/100000')
        data = json.loads(response.data)

        # Check status code, success and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')


    def test_create_new_question(self):
        """Tests question creation success"""

        # Total questions before posting a new question
        questions_before = Question.query.all()

        # create new question and load response data
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        # Total questions after posting a new question
        questions_after = Question.query.all()

        # check status code and success message
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)

        # Check difference in total question after posting
        self.assertTrue(len(questions_after) - len(questions_before) == 1)

        # check that question is not None
        question = Question.query.get(data['question_id'])
        self.assertIsNotNone(question)

    def test_400_if_question_creation_fails(self):
        """Tests question creation failure 400"""

        # get number of questions before post
        questions_before = Question.query.all()

        # create new question without json data, then load response data
        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        # get number of questions after post
        questions_after = Question.query.all()

        # check status code and success message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEquals(data['message'], 'Bad request')

        # check if questions_after and questions_before are equal
        self.assertTrue(len(questions_after) == len(questions_before))


    def test_search_questions(self):
        """Tests search questions success"""

        # send post request with search term
        response = self.client().post('/search',
                                      json={'searchTerm': 'What'})
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)

        # Check that number of results = 8
        self.assertEqual(len(data['questions']), 8)

        # Check the id of the first result in response
        self.assertEqual(data['questions'][0]['id'], 2)


    def test_404_if_search_questions_fails(self):
        """Tests search questions failure 404"""

        # send post request with search term that should fail
        response = self.client().post('/search',
                                      json={'searchTerm': 'randomrandomrandom'})
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')


    def test_get_questions_by_category(self):
        """Tests getting questions by category success"""

        # send request with category id 4 for History
        response = self.client().get('/categories/4/questions')
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # Check that the category has questions
        self.assertNotEqual(len(data['questions']), 0)

        # check that current category returned is History
        self.assertEqual(data['current_category'], 'History')


    def test_404_if_questions_by_category_fails(self):
        """Tests getting questions by category failure 404"""

        # send request with category id 0
        response = self.client().get('/categories/0/questions')
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_play_quiz_game(self):
        """Tests playing quiz game success"""

        # send post request with category and previous questions
        response = self.client().post('/quizzes',
                                      json={'previous_questions': [9, 5, 12],
                                            'quiz_category': {'type': 'History', 'id': '4'}})
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        # Check that the question returned is in the correct category
        self.assertEqual(data['question']['category'], 4)

        # Question returned is not in the previous questions list
        self.assertNotEqual(data['question']['id'], 9)
        self.assertNotEqual(data['question']['id'], 5)
        self.assertNotEqual(data['question']['id'], 12)


    def test_play_quiz_fails(self):
        """Tests playing quiz game failure 400"""

        # send post request without json data
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()