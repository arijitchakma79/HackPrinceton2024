from flask import Flask
from flask_cors import CORS
from routes.rag_routes import rag_routes 
from config.config import Config
from rag.rag import RAG
from rag.lecture_tracker import LectureTracker

def create_app():
    app = Flask(__name__)

    # Enable CORS
    CORS(app)

    # Load the configuration
    app.config.from_object(Config)

    # Register the blueprint
    app.register_blueprint(rag_routes)

    # Initialize the RAG and LectureTracker instances
    rag_instance = RAG()
    lecture_tracker = LectureTracker(rag_instance)

    # Start periodic updates
    lecture_tracker.start_periodic_db_update()

    # Return initialized app
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=Config.PORT_NUMBER, debug=Config.DEBUG)
