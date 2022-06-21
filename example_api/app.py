from flask import Flask, request, make_response
from example_api import db
from example_api.models.models import Loan, Payment, PaymentModel, Get_PaymentModel, RefundModel, jsonify_payment, jsonify_refund
from pydantic import ValidationError
from example_api.routes import blueprints
from example_api import app

#app = Flask(__name__)

