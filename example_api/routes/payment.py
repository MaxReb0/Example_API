
from flask import Blueprint, make_response, request
from pydantic import ValidationError
from database import db
from example_api.models.models import PaymentModel, Get_PaymentModel, LoanCreateModel, Loan, Payment, jsonify_payment

payment_blueprint = Blueprint("payment", __name__, url_prefix="/payment")

@payment_blueprint.route("/", methods=['POST'])
@payment_blueprint.route('/create_payment', methods=['POST'])
def create_payment():
    """
        This function is used to make a payment. This API currently only supports
        paying off loans, and not other types of payments. If the payment requested
        is larger than the amount owed, it will be refunded. If it is less, it will
        simply process the payment and remove the amount owed. If the loan doesn't exist,
        it will simply return a 400 status code.
        It expects a JSON of the following format
        {
            "loan_id" : <loan_id of loan being payed.>
            "payment_amount" : <amount of loan being payed off>
        }
    """
    input_json = request.get_json(force=True)
    try:
        #Instantiate this class, and check if there are any issues.
        PaymentModel(**input_json)

        #Once validated, can simply create the payment, and add it to the database.
        loan = Loan.query.get(input_json['loan_id'])
        new_payment = Payment(payment_amount = input_json['payment_amount'], loan = loan, refunded = False)
        db.session.add(new_payment)
        loan.amount_owed = loan.amount_owed - new_payment.payment_amount
        db.session.commit()
        return make_response(jsonify_payment(new_payment, loan), 200)
    except ValidationError as e:
        print(e)
        return make_response(e.json(), 400)