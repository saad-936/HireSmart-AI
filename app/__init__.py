import os
from flask import Flask
from dotenv import load_dotenv
from app.database import init_db

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "development-secret-key"
    )

    init_db()

    from app.routes import main
    app.register_blueprint(main)

    return app
