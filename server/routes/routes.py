from flask import Blueprint, request, jsonify
from handlers.handlers import Handlers
from handlers.rag_handlers import QueryHandler 

# Create the Flask blueprint
Routes = Blueprint('routes', __name__)

# Initialize handler instances
handlers = Handlers()
query_handler = QueryHandler() 

@Routes.route('/', methods=['GET'])
def print_hello_world():
    return handlers.print_hello_world()

@Routes.route('/add_lecture', methods=['POST'])
def add_lecture():

    data = request.get_json()
    course_title = data.get('course_title')
    lecture_title = data.get('lecture_title')
    content = data.get('content')

    if not course_title or not lecture_title or not content:
        return jsonify({"error": "All fields 'course_title', 'lecture_title', and 'content' are required"}), 400
    
    response = query_handler.add_lecture_to_db(course_title, lecture_title, content)
    return jsonify(response), 201 if "message" in response else 400

@Routes.route('/query', methods=['POST'])
def query():

    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({"error": "The 'question' field is required"}), 400
    
    response = query_handler.handle_query(question)
    return jsonify(response), 200 if "answer" in response else 400
