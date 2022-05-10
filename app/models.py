from datetime import datetime
from app import db
from flask import jsonify

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_amount = db.Column(db.Integer)
    amount_owed = db.Column(db.Integer)
    payments = db.relationship('Payment', backref='loan', lazy='dynamic')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payment_amount = db.Column(db.Integer)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))
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
