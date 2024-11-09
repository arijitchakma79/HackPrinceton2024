from flask import Blueprint, request, jsonify
from handlers.rag_handler import (
    add_lecture_handler, 
    query_handler_function,
    finalize_lecture_handler,
    get_lecture_status_handler,
    get_session_stats_handler,
    cleanup_session_handler,
    recover_session_handler,
    get_complete_lecture_handler
)

rag_routes = Blueprint('rag_routes', __name__)

@rag_routes.route('/add_lecture', methods=['POST'])
def add_lecture():
    try:
        data = request.get_json()
        response = add_lecture_handler(
            data['course_title'],
            data['lecture_title'],
            data['content']
        )
        status_code = 200 if response['status'] == 'success' else 500
        return jsonify(response), status_code
    except KeyError as e:
        return jsonify({
            "status": "error",
            "message": f"Missing required field: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500

@rag_routes.route('/query', methods=['POST'])
def query():
    try:
        data = request.get_json()
        response = query_handler_function(
            data['question'],
            data['course_title'],
            data['lecture_title'],
            segment_id=data.get('segment_id'),
            prefer_recent=data.get('prefer_recent', True),
            limit=data.get('limit', 3)
        )
        status_code = 200 if 'answer' in response else 500
        return jsonify(response), status_code
    except KeyError as e:
        return jsonify({
            "status": "error",
            "message": f"Missing required field: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500

@rag_routes.route('/finalize_lecture', methods=['POST'])
def finalize_lecture():
    try:
        data = request.get_json()
        response = finalize_lecture_handler(
            data['course_title'],
            data['lecture_title']
        )
        status_code = 200 if response['status'] == 'success' else 500
        return jsonify(response), status_code
    except KeyError as e:
        return jsonify({
            "status": "error",
            "message": f"Missing required field: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500

@rag_routes.route('/lecture_status', methods=['GET'])
def get_lecture_status():
    try:
        course_title = request.args.get('course_title')
        lecture_title = request.args.get('lecture_title')
        
        if not course_title or not lecture_title:
            return jsonify({
                "status": "error",
                "message": "Missing course_title or lecture_title parameter"
            }), 400
            
        response = get_lecture_status_handler(course_title, lecture_title)
        status_code = 200 if response['status'] != 'error' else 404
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500

@rag_routes.route('/session_stats/<session_key>', methods=['GET'])
def get_session_stats(session_key):
    try:
        response = get_session_stats_handler(session_key)
        status_code = 200 if response['status'] != 'error' else 404
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500

@rag_routes.route('/cleanup_session/<session_key>', methods=['DELETE'])
def cleanup_session(session_key):
    try:
        response = cleanup_session_handler(session_key)
        status_code = 200 if response['status'] == 'success' else 500
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500

@rag_routes.route('/recover_session/<session_key>', methods=['POST'])
def recover_session(session_key):
    try:
        response = recover_session_handler(session_key)
        status_code = 200 if response['status'] == 'success' else 500
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500

@rag_routes.route('/complete_lecture', methods=['GET'])
def get_complete_lecture():
    try:
        course_title = request.args.get('course_title')
        lecture_title = request.args.get('lecture_title')
        
        if not course_title or not lecture_title:
            return jsonify({
                "status": "error",
                "message": "Missing course_title or lecture_title parameter"
            }), 400
            
        response = get_complete_lecture_handler(course_title, lecture_title)
        status_code = 200 if response['status'] == 'success' else 404
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500