from flask import Flask, request, make_response
from example_api import db
from example_api.models.models import Loan, Payment, PaymentModel, Get_PaymentModel, RefundModel, jsonify_payment, jsonify_refund
from pydantic import ValidationError
from example_api.routes import blueprints

app = Flask(__name__)
app.url_map.strict_slashes = False

for _ in map(app.register_blueprint, blueprints): ...


@app.route('/create_payment', methods=['POST'])
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
        Payment_Validator(**input_json)

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

@app.route("/get_payment", methods=["GET"])
def get_payment():
    """
        This function is used to get a payment. This API currently only supports
        paying off loans, and not other types of payments. 
        It just expects a JSON of the following format:
        {
            'payment_id' :  <id of payment>
        }
    """
    input_json = request.get_json(force=True)
    try:
        # Validate inputs.
        Get_Payment_Validator(**input_json)
    
        payment = Payment.query.get(input_json['payment_id'])
        loan = Loan.query.get(payment.loan_id)
        return make_response(jsonify_payment(payment, loan), 200)
    except ValidationError as e:
        print(e)
        return make_response(e.json(), 400)

@app.route("/request_refund", methods=["POST"])
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
        Refund_Validator(**input_json)

        # Everything has been validated correctly.
        payment = Payment.query.get(input_json['payment_id'])
        loan = Loan.query.get(payment.loan_id)
        loan.amount_owed = loan.amount_owed + payment.payment_amount
        payment.refunded = True
        db.session.commit()
        return make_response(jsonify_refund(payment, loan), 200)
    except ValidationError as e:
        print(e)
        return make_response(e.json(), 400)


        