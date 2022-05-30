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
            raise ValueError(f"Error, id : {loan_id} is not in  the database!")
        return loan_id
    
    @validator('payment_amount')
    def payment_greater_than_amount_owed(cls, payment_amount, values):
        print(values)
        loan_id = values["loan_id"]
        if db.session.query(Loan.id).filter_by(id = loan_id).first() is not None:
            loan = Loan.query.get(loan_id)
            if loan.amount_owed < payment_amount:
                raise ValueError(f"Error, loan {loan_id} only needs {loan.amount_owed}, but the payment amount is {payment_amount}.")

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
