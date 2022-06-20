
from flask import Blueprint, make_response, request
from pydantic import ValidationError
from example_api.models.models import LoanCreateModel, LoanCreateModel

loan_blueprint = Blueprint("loan", __name__, url_prefix="/loan")

@loan_blueprint.route("/", methods=['POST'])
def loan_create_handler():
    data = request.get_json(force=True)
    try:
        loan_create_request = LoanCreateModel(**data)

        # new_loan = Loan(loan_amount = input_json['loan_amount'], amount_owed = input_json['loan_amount'])
        # db.session.add(new_loan)
        # db.session.commit()
        # return make_response(jsonify_loan(new_loan), 200)
        return loan_create_request.json()
    except ValidationError as e:
        return make_response(e.json(), 400)


@loan_blueprint.route("/", defaults={"loan_id": None})
@loan_blueprint.route("/<loan_id>", methods=['GET'])
def loan_get_handler(loan_id: str):
    if loan_id:
        return {"loan_id": loan_id}
    return make_response({"error": f"Must provide '/<loan_id>'"}, 400)