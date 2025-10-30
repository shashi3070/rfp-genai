from flask import Flask
from backend.config import Config
from backend.core.logger import get_logger
import backend.config as cred
logger = get_logger(__name__)

def create_app():
    app = Flask(__name__)

    

    logger.info("✅ Flask app initialized")
    return app


if __name__ == "__main__":
    app = create_app()
    logger.info(" Starting Flask server...")
    logger.info(Config.AZURE_OPENAI_API_KEY)
    
    app.run(host="0.0.0.0", port=Config.FLASK_PORT, debug=(Config.FLASK_ENV == "development"))
