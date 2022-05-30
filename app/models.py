from datetime import datetime
from app import db
from flask import jsonify
from pydantic import BaseModel, validator
import uuid

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_amount = db.Column(db.Integer)
    amount_owed = db.Column(db.Integer)
    payments = db.relationship('Payment', backref='loan', lazy='dynamic')

class Loan_Validator(BaseModel):
    loan_amount: int

class Get_Loan_Validator(BaseModel):
    loan_id : int

    @validator("loan_id")
    def does_loan_exist(cls, loan_id):
        if db.session.query(Loan.id).filter_by(id = loan_id).first() is None:
            raise ValueError(f"Error, id : {loan_id} is not in the database!")
        return loan_id

class Payment(db.Model):
    #Add timestamp
    #Check if there was a payment for the loan in the last x minutes
    id = db.Column(db.Integer, primary_key=True)
    payment_amount = db.Column(db.Integer)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))
    refunded = db.Column(db.Boolean)

class Payment_Validator(BaseModel):
    # Need to verify that this loan exists in the database.
    loan_id: int
    payment_amount: int

    @validator("loan_id")
    def id_must_be_in_database(cls, loan_id):
        if db.session.query(Loan.id).filter_by(id = loan_id).first() is None:
            raise ValueError(f"Error, loan id : {loan_id} is not in the database of loans!")
        return loan_id
    
    @validator('payment_amount')
    def payment_greater_than_amount_owed(cls, payment_amount, values):
        if "loan_id" in values.keys():
            loan_id = values["loan_id"]
            if db.session.query(Loan.id).filter_by(id = loan_id).first() is not None:
                loan = Loan.query.get(loan_id)
                if loan.amount_owed < payment_amount:
                    raise ValueError(f"Error, loan {loan_id} only needs {loan.amount_owed}, but the payment amount is {payment_amount}.")
                return payment_amount

class Get_Payment_Validator(BaseModel):
    payment_id: int

    @validator("payment_id")
    def does_payment_exist(cls, payment_id):
        if db.session.query(Payment.id).filter_by(id = payment_id).first() is None:
            raise ValueError(f"Error, id : {payment_id} is not in the payment database!")

class Refund_Validator(BaseModel):
    payment_id: int

    @validator("payment_id")
    def id_must_be_in_database(cls, payment_id):
        if db.session.query(Payment.id).filter_by(id = payment_id).first() is None:
            raise ValueError(f"Error, payment id : {payment_id} is not in the database of payments!")
        return payment_id
    
    @validator("payment_id")
    def payment_must_not_be_already_refunded(cls, payment_id):
        existance = db.session.query(Payment.id).filter_by(id = payment_id).first()
        if existance is not None:
            payment = Payment.query.get(payment_id)
            if payment.refunded:
                raise ValueError(f"Error, payment id : {payment_id} has already been refunded!")



def jsonify_payment(payment, loan):
    return jsonify(
        {
            "loan_amount" : loan.loan_amount,
            "payment_id" : payment.id,
            "payment_amount" : payment.payment_amount,
            "loan_id" : loan.id,
            "amount_owed" : loan.amount_owed,
            "refunded" : payment.refunded
        }
    )

def jsonify_loan(loan):
    return jsonify({
            'loan_id' : loan.id,
            'loan_amount' : loan.loan_amount,
            'amount_owed' : loan.amount_owed
        })

def jsonify_refund(payment, loan):
    return jsonify(
        {
            "Success" : "Payment: " + str(payment.id) + " has been refunded successfully.",
            "Payment Information" : {
                "payment_id" : payment.id,
                "payment_amount" : payment.payment_amount,
                "loan_id" : loan.id,
                "refunded" : payment.refunded
            },
            "Loan Information" : {
                'loan_id' : loan.id,
                'loan_amount' : loan.loan_amount,
                'amount_owed' : loan.amount_owed
            }
        }
    )
