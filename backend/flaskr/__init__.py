import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def category_to_dict(categories_all):
  categories = {}
  for category in categories_all:
    categories[category.id] = category.type
  return categories

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @DONE: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Accsses-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Accsses-Control-Allow-Methods', 'GET, POST, PATCH, OPTIONS, DELETE')
    return response


  '''
  @DONE: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrive_categories():
    categories_all = Category.query.all()
    if categories_all is None:
      abort(404)
    else:

      return jsonify({
        'success': True,
        'categories': category_to_dict(categories_all)
      })

  '''
  @DONE: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions') 
  def retrive_questions():
    selection = Question.query.order_by(Question.id).all()
    categories_all = Category.query.order_by(Category.id).all()
    current_questions = paginate_questions(request, selection)
      
    if len(current_questions) == 0:
      abort(404)
    else:
      return jsonify({
        'success': True,
        'total_questions': len(selection),
        'categories': category_to_dict(categories_all),
        'questions': current_questions
      })


  '''
  @DONE: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)
      else:
        question.delete()   
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
          'success': True,
          'deleted': f'question id = {question_id} deleted',
          'questions': current_questions,
          'total_questions': len(Question.query.all())
        })        
    except:
      abort(422)


  '''
  @DONE: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()
    if body:
      new_question = {
        'question': body.get('question', None),
        'answer': body.get('answer', None),
        'category': body.get('category', None),
        'difficulty': body.get('difficulty', None)
      }
      try:
        question = Question(question=new_question['question'], answer=new_question['answer'],
        category=new_question['category'], difficulty=new_question['difficulty'])
        question.insert()
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        return jsonify({
          'success': True,
          'created': question.id,
          'questions': current_questions,
          'total_questions': len(Question.query.all())
        })
      except:
        abort(422)

    else:
      abort(404)

  '''
  @DONE: Method is not allowed
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    data = request.get_json()
    search = data['searchTerm']
    questions = Question.query.filter(Question.question.ilike(f'%{search}%')).all()
    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)  
    else:
      return jsonify({
        'success': True,
        'current_questions': current_questions,
        'total_questions': len(questions)
      })  





  '''
  @DONE: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def questions_by_category(category_id):
    try:
      questions = Question.query.filter_by(category=str(category_id)).all()
      current_questions = paginate_questions(request, questions)

      if len(current_questions) == 0:
        abort(404)
      else:
        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(questions)
        })        
    except:
      abort(422)

  '''
  @DONE: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def quizzes():
    search = request.get_json()

    if (search is not None) and ('quiz_category' in search.keys()):
      quiz_category = search['quiz_category']
      previous_questions = []
      if  'previous_questions' in search.keys():
        previous_questions = search['previous_questions']  
        category_id = search['quiz_category']['id']
        unique_question = Question.id.notin_(previous_questions)
        question = Question.query.filter(Question.category == category_id, unique_question).first()
        return jsonify({
        'success': True,
        'question': question.format()
        })  
      else:
        abort(422)
    else:
      return abort(404)

    
    
    






  '''
  @DONE: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': "Resource is not found"
    }), 404


  @app.errorhandler(422)
  def not_found(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': "Unprocessable"
    }), 422

  @app.errorhandler(400)
  def not_found(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': "Bad request"
    }), 400

  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': "Method not allowed"
    }), 405
  
  return app

    