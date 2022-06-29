from flask import Blueprint, make_response, request
from pydantic import ValidationError
from ..database import db
from example_api.models.models import RefundModel
from example_api.db.orm import Payment, Loan, jsonify_refund
from example_api.db.crud import loan_getter, payment_getter, db_commit
from .helper_functions import timer

refund_blueprint = Blueprint("refund", __name__, url_prefix="/refund")

@timer
def request_refund(request):
    """
        This function takes a payment id and attempts to refund it. If the payment
        has already been refunded it will return an error.
        It expects a JSON of this format:
        {
            'payment_id' : <id of payment>
        }
    """
    input_json = request.get_json(force=True)
    try:
        # validate inputs.
        refund_data = RefundModel(**input_json)

        # Everything has been validated correctly.
        payment = payment_getter(refund_data.payment_id)
        loan = loan_getter(payment.loan_id)
        loan.amount_owed = loan.amount_owed + payment.payment_amount
        payment.refunded = True
        db_commit()
        return make_response(jsonify_refund(payment, loan), 200)
    except ValidationError as e:
        print(e)
        return make_response(e.json(), 400)

@refund_blueprint.route("/", methods=['POST'])
@refund_blueprint.route('/request_refund', methods=['POST'])
def request_refund_handler():
    return request_refund(request)