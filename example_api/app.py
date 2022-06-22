from flask import Flask, request, make_response
from example_api import db
from pydantic import ValidationError
from example_api.routes import blueprints
from example_api import app

#app = Flask(__name__)

