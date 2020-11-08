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
        self.database_name = "trivia_test"
        self.database_user = "postgres"
        self.database_password = "Passasdk"
        self.database_host = "localhost"
        self.database_port = "5432"
        self.database_path = f'postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}'
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": 'Which planet has a moon named The Moon?',
            "answer": "Earth",
            "difficulty": 3,
            "category": 1
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

    """
    TODO
    Write at least one test for each test for successful 
    operation and for expected errors.
    """
    #... Test for catrgory
    def test_retrive_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_sent_request_beyond_valid_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')            


    #... Test for questions paginations
    def test_retrive_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['current_questions']), 10)
        #... the rest for the page

    def test_404_sent_request_beyond_valid_page(self):
        res = self.client().get('/questions?page=500', json={'category': str(2)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource is not found')    

    def test_422_sent_request_page_0(self):
        res = self.client().get('/questions?page=0', json={'category': str(2)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource is not found')  

    # def test_422_sent_request_page_below_zero(self):
    #     res = self.client().get('/questions?page=-1', json={'category': str(2)})
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 422)
    #     self.assertEqual(data['success'], False)
    #     self.assertEqual(data['message'], 'Unprocessable')      


    #... Test for deletion
    def test_delete_question(self):
        question = Question.query.order_by(Question.id.desc()).first()
        question_id = question.id

        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)
        question_state = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], f'question id = {question_id} deleted')
        self.assertEqual(question_state, None)


    #... Test for creation
    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        new_question = Question.query.order_by(Question.id.desc()).first()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['created'], new_question.id)


    #... Test for searching 
    def test_search_questions(self):
        res = self.client().post('/questions/search',  json={"search_term": 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['current_questions'])

    def test_search_questions_success_no_results(self):
        response = self.client().post('/questions/search', json={"search_term": 'xxxxxxx'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource is not found')



    #... Test for quizz
    def test_quizzes(self):
        category = Category.query.first()
        res = self.client().post('/quizzes', json={'quiz_category': category.format()})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()