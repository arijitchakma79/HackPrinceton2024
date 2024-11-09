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
    title = data.get('title')
    content = data.get('content')
    
    response = query_handler.add_lecture_to_db(title, content)
    return jsonify(response), 201 if "message" in response else 400

@Routes.route('/query', methods=['POST'])
def query():
    """
    Route to query the vector database.
    Expects JSON payload with 'question' field.
    """
    data = request.get_json()
    question = data.get('question')
    
    response = query_handler.handle_query(question)
    return jsonify(response), 200 if "answer" in response else 400
