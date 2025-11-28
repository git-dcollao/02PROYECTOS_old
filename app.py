from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DevelopmentConfig

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=None):
    app = Flask(__name__)
    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_object('config.DevelopmentConfig')

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from app import models

    return app

from app import create_app

# Crear la aplicación usando la función factory
app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5050)
#from app import models
#
#def create_app():
#    app = Flask(__name__)
#    app.config.from_object('config.Config')
#    db.init_app(app)
#    migrate.init_app(app, db)
#    return app

