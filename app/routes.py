from flask import render_template, flash, redirect, url_for, request, jsonify, make_response
from app import app
from app import db
from app.models import Loan, Loan_Validator, Payment, Payment_Validator, jsonify_loan, jsonify_payment, jsonify_refund
from pydantic import ValidationError

@app.route('/create_loan', methods=['POST'])
def create_loan():
    """
        The purpose of this function is to take in a JSON request that will be processed
        and append a loan to the loan table in the database. The goal here is that it
        will eventually be linked to the User that initiated the loan, as well as the 
        attempts to pay off the loan.
        Expects JSON of format:
        {
            "loan_amount" : <amount being requested for loan.>
        }
    """
    input_json = request.get_json(force=True)
    try:
        Loan_Validator(**input_json)
        new_loan = Loan(loan_amount = input_json['loan_amount'], amount_owed = input_json['loan_amount'])
        db.session.add(new_loan)
        db.session.commit()
        return make_response(jsonify_loan(new_loan), 200)
    except ValidationError as e:
        print(e)
        return make_response(e.json(), 400)

#Still needs work to support validators.
@app.route('/get_loan', methods=['GET'])
def get_loan():
    """
        This function is used to get a loan. This API currently only supports
        paying off loans, and not other types of payments. 
        It just expects a JSON of the following format:
        {
            'id' :  <id of loan>
        }
    """
    #can create problems if id not in json, use pydantic
    #Leaves vulnerable for SQL injection
    input_json = request.get_json(force=True)
    loan_exists = db.session.query(Loan.id).filter_by(id = input_json['id']).first() is not None
    if 'id' in input_json.keys() and loan_exists:
        loan = Loan.query.get(input_json['id'])
        return make_response(jsonify_loan(loan), 200)
    else:
        return make_response(jsonify({
            'Error' : "Error with request, could not find ID provided to database."
        }), 400)

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
            "id" : <id of loan being payed.>
            "payment_amount" : <amount of loan being payed off>
        }
    """
    input_json = request.get_json(force=True)
    try:
        #Instantiate this class, and check if there are any issues.
        Payment_Validator(**input_json)

        #Once validated, can simply create the payment, and add it to the database.
        loan = Loan.query.get(input_json['id'])
        new_payment = Payment(payment_amount = input_json['payment_amount'], loan = loan, refunded = False)
        db.session.add(new_payment)
        loan.amount_owed = loan.amount_owed - new_payment.payment_amount
        db.session.commit()
        return make_response(jsonify_payment(new_payment, loan), 200)
    except ValidationError as e:
        print(e)
        return make_response(e.json(), 400)

# Still needs work to support validators
@app.route("/get_payment", methods=["GET"])
def get_payment():
    """
        This function is used to get a payment. This API currently only supports
        paying off loans, and not other types of payments. 
        It just expects a JSON of the following format:
        {
            'id' :  <id of payment>
        }
    """
    input_json = request.get_json(force=True)
    payment_exists = db.session.query(Payment.id).filter_by(id = input_json['id']).first() is not None
    if 'id' in input_json.keys() and payment_exists:
        payment = Payment.query.get(input_json['id'])
        loan = Loan.query.get(payment.loan_id)
        return make_response(jsonify_payment(payment, loan), 200)
    else:
        return make_response(jsonify({
            'Error' : "Error with request, could not find ID provided to database."
        }), 400)
    
#Still needs work to support validators.
@app.route("/request_refund", methods=["POST"])
def request_refund():
    """
        This function takes a payment id and attempts to refund it. If the payment
        has already been refunded it will return an error.
        It expects a JSON of this format:
        {
            'id' : <id of payment>
        }
    """
    input_json = request.get_json(force=True)
    payment_exists = db.session.query(Payment.id).filter_by(id = input_json['id']).first() is not None
    if "id" in input_json.keys() and payment_exists:
        payment = Payment.query.get(input_json['id'])
        loan = Loan.query.get(payment.loan_id)

        #Check if payment has already been refunded
        if not payment.refunded:
            loan.amount_owed = loan.amount_owed + payment.payment_amount
            payment.refunded = True
            db.session.commit()
            #clean this up.
            return make_response(jsonify_refund(payment, loan), 200)
        else:
            return make_response(jsonify({
                "Error": "Requested payment refund has already been refunded."
            }), 400)
    else:  
        return make_response(jsonify({"Error" : "ID wasn't recognized as entry in database."}), 400)


        