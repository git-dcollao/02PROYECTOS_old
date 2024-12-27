import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from os import environ

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class='config.DevelopmentConfig'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = environ.get('SECRET_KEY')

    db.init_app(app)
    migrate.init_app(app, db)

    from app.controllers import controllers_bp
    app.register_blueprint(controllers_bp)
    
    from app.handlers import handlers_bp
    app.register_blueprint(handlers_bp)

    return app
