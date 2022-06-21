from flask import Flask
from example_api.routes import blueprints
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from database import db

app = Flask(__name__)
app.url_map.strict_slashes = False

for _ in map(app.register_blueprint, blueprints): ...
app.config.from_object(Config)
#db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

from example_api import routes, models