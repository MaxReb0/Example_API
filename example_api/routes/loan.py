
from flask import Blueprint, make_response, request
from pydantic import ValidationError
from database import db
from example_api.models.models import LoanCreateModel, Get_LoanModel, Loan, jsonify_loan

loan_blueprint = Blueprint("loan", __name__, url_prefix="/loan")

@loan_blueprint.route("/", methods=['POST'])
def loan_create_handler():
    data = request.get_json(force=True)
    try:
        loan_create_request = LoanCreateModel(**data)

        new_loan = Loan(loan_amount = loan_create_request.loan_amount, amount_owed = loan_create_request.loan_amount)
        db.session.add(new_loan)
        db.session.commit()
        return make_response(jsonify_loan(new_loan), 200)
    except ValidationError as e:
        return make_response(e.json(), 400)


@loan_blueprint.route("/", defaults={"loan_id": None})
@loan_blueprint.route("/<loan_id>", methods=['GET'])
def loan_get_handler(loan_id: str):
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
        
        loan = Loan.query.get(loan_data.loan_id)
        return make_response(jsonify_loan(loan), 200)
    except ValidationError as e:
        print(e)
        return make_response(e.json(), 400)
"""
    if loan_id:
        return {"loan_id": loan_id}
    return make_response({"error": f"Must provide '/<loan_id>'"}, 400)
"""