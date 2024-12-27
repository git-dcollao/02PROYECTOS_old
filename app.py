from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import models

#from app import create_app
#from config import DevelopmentConfig
#from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate
#
## Crear la instancia de la app
##app = create_app(config_class=DevelopmentConfig)
#
##if __name__ == "__main__":
#    # Ejecutar la app usando configuraciones globales
##    app.run(debug=DevelopmentConfig.DEBUG, host=DevelopmentConfig.HOST, port=DevelopmentConfig.PORT)
#
#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
#db = SQLAlchemy(app)
#migrate = Migrate(app, db)
#
#from app import models
#
#def create_app():
#    app = Flask(__name__)
#    app.config.from_object('config.Config')
#    db.init_app(app)
#    migrate.init_app(app, db)
#    return app

