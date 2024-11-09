from flask import Flask
from flask_cors import CORS
from routes.routes import Routes
from config.config import Config

def create_app():
    app = Flask(__name__)

    # Enable CORS
    CORS(app)

    # Load the configuration
    app.config.from_object(Config)

    # Register the blueprint
    app.register_blueprint(Routes)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=Config.PORT_NUMBER, debug=Config.DEBUG)
