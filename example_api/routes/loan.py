
from flask import Blueprint, make_response, request
from pydantic import ValidationError
from ..database import db
from example_api.models.models import LoanCreateModel, Get_LoanModel
from example_api.db.orm import Loan, jsonify_loan
from example_api.db.crud import db_add, loan_getter
from .helper_functions import timer

loan_blueprint = Blueprint("loan", __name__, url_prefix="/loan")

@timer
def create_loan(request):
    data = request.get_json(force=True)
    try:
        loan_create_request = LoanCreateModel(**data)

        new_loan = Loan(loan_amount = loan_create_request.loan_amount, amount_owed = loan_create_request.loan_amount)
        db_add(new_loan)
        return make_response(jsonify_loan(new_loan), 200)
    except ValidationError as e:
        return make_response(e.json(), 400)

@timer
def get_loan(request):
    """
        This function is used to get a loan. This API currently only supports
        paying off loans, and not other types of payments. 
        It just expects a JSON of the following format:
        {
            'id' :  <id of loan>
        }
    """
    input_json = request.get_json(force=True)
    try:
        #Validate inputs.
        loan_data = Get_LoanModel(**input_json)
        
        loan = loan_getter(loan_data.loan_id)
        return make_response(jsonify_loan(loan), 200)
    except ValidationError as e:
        print(e)
        return make_response(e.json(), 400)

@loan_blueprint.route("/", methods=['POST'])
def loan_create_handler():
    return create_loan(request)

@loan_blueprint.route("/", defaults={"loan_id": None})
@loan_blueprint.route("/<loan_id>", methods=['GET'])
def loan_get_handler(loan_id: str):
    return get_loan(request)