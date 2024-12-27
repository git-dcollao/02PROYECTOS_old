from flask import Flask
from .models import db, init_db
from .controllers import controllers_bp
import os, time
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)
    load_dotenv()
    
    # Configuración
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    db.init_app(app)
    
    # Esperar a que la base de datos esté lista
    with app.app_context():
        retries = 5
        while retries > 0:
            try:
                init_db()
                print("Base de datos inicializada correctamente")
                break
            except Exception as e:
                retries -= 1
                print(f"Intentando conectar a la base de datos... {retries} intentos restantes")
                print(f"Error: {str(e)}")
                if retries > 0:
                    time.sleep(5)
    
    app.register_blueprint(controllers_bp)
    return app