"""Define ORM models here"""
from datetime import datetime
from ..database import db
from flask import jsonify

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_amount = db.Column(db.Integer)
    amount_owed = db.Column(db.Integer)
    time_created = db.Column(db.DateTime(timezone=True), default=datetime.now())
    time_updated = db.Column(db.DateTime(timezone=True), default=datetime.now(), onupdate=datetime.now())
    payments = db.relationship('Payment', backref='loan', lazy='dynamic')

class Payment(db.Model):
    #Add timestamp
    #Check if there was a payment for the loan in the last x minutes
    id = db.Column(db.Integer, primary_key=True)
    payment_amount = db.Column(db.Integer)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))
    time_created = db.Column(db.DateTime(timezone=True), default=datetime.now())
    time_updated = db.Column(db.DateTime(timezone=True), default=datetime.now(), onupdate=datetime.now())
    refunded = db.Column(db.Boolean)

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
