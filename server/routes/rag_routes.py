from flask import Blueprint, request, jsonify
from handlers.rag_handler import add_lecture_handler, query_handler_function

rag_routes = Blueprint('rag_routes', __name__)

@rag_routes.route('/add_lecture', methods=['POST'])
def add_lecture():
    data = request.get_json()
    course_title = data['course_title']
    lecture_title = data['lecture_title']
    content = data['content']
    
    response = add_lecture_handler(course_title, lecture_title, content)
    status_code = 200 if response['status'] == 'success' else 500
    return jsonify(response), status_code

@rag_routes.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    question = data['question']
    course_title = data['course_title']
    lecture_title = data['lecture_title']
    
    response = query_handler_function(question, course_title, lecture_title)
    status_code = 200 if 'answer' in response else 500
    return jsonify(response), status_code
