from flask import Blueprint, make_response, request
from pydantic import ValidationError
from database import db
from example_api.models.models import RefundModel, Payment, Loan, jsonify_refund

refund_blueprint = Blueprint("refund", __name__, url_prefix="/refund")

@refund_blueprint.route("/", methods=['POST'])
@refund_blueprint.route('/request_refund', methods=['POST'])
def request_refund():
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
        payment = Payment.query.get(refund_data.payment_id)
        loan = Loan.query.get(payment.loan_id)
        loan.amount_owed = loan.amount_owed + payment.payment_amount
        payment.refunded = True
        db.session.commit()
        return make_response(jsonify_refund(payment, loan), 200)
    except ValidationError as e:
        print(e)
        return make_response(e.json(), 400)