from flask import Blueprint, request, jsonify
from handlers.handlers import Handlers
from handlers.rag_handlers import QueryHandler
from handlers.lecture_tracking_handler import LectureTracker

# Create the Flask blueprint
Routes = Blueprint('routes', __name__)

# Initialize handler instances
handlers = Handlers()
query_handler = QueryHandler()
lecture_tracker = LectureTracker()

# Set up dependencies
lecture_tracker.set_query_handler(query_handler)
query_handler.set_lecture_tracker(lecture_tracker)

# Start the periodic database update
lecture_tracker.start_periodic_db_update()

@Routes.route('/', methods=['GET'])
def print_hello_world():
    return handlers.print_hello_world()

@Routes.route('/add_lecture_chunk', methods=['POST'])
def add_lecture_chunk():
    """
    Route for adding or updating a lecture chunk.
    """
    data = request.get_json()
    course_title = data.get('course_title')
    lecture_title = data.get('lecture_title')
    content = data.get('content')

    if not course_title or not lecture_title or not content:
        return jsonify({"error": "All fields 'course_title', 'lecture_title', and 'content' are required"}), 400

    session_key = lecture_tracker.add_or_update_lecture(course_title, lecture_title, content)
    return jsonify({"message": f"Content added to session '{session_key}'"}), 200

@Routes.route('/finalize_lecture', methods=['POST'])
def finalize_lecture():
    """
    Route for finalizing a lecture and pushing it to the database.
    """
    data = request.get_json()
    course_title = data.get('course_title')
    lecture_title = data.get('lecture_title')

    if not course_title or not lecture_title:
        return jsonify({"error": "Fields 'course_title' and 'lecture_title' are required"}), 400

    response = lecture_tracker.finalize_lecture(course_title, lecture_title)
    return jsonify(response), 200 if "message" in response else 400

@Routes.route('/query', methods=['POST'])
def query():
    """
    Route to query the vector database with option to prioritize recent content.
    """
    data = request.get_json()
    question = data.get('question')
    course_title = data.get('course_title')
    lecture_title = data.get('lecture_title')
    prefer_recent = data.get('prefer_recent', True)  # Default to True for prioritizing recent content

    if not question:
        return jsonify({"error": "The 'question' field is required"}), 400

    response = query_handler.handle_query(
        course_title=course_title, 
        lecture_title=lecture_title, 
        question=question,
        prefer_recent=prefer_recent
    )
    
    # Return appropriate status code based on response type
    if "answer" in response:
        return jsonify(response), 200
    elif "error" in response:
        return jsonify(response), 400
    else:
        return jsonify({"error": "Unexpected response format"}), 500