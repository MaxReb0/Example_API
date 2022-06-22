from ..database import db
from ..models.models import Loan, Payment

#Simply adds the data to the database.
def db_add(data):
    db.session.add(data)
    db.session.commit()

def db_commit():
    db.session.commit()

def loan_getter(loan_id):
    return Loan.query.get(loan_id)

def payment_getter(payment_id):
    return Payment.query.get(payment_id)

def check_payment_existence(payment_id):
    return db.session.query(Payment.id).filter_by(id = payment_id).first()

def check_loan_existence(loan_id):
    return db.session.query(Loan.id).filter_by(id = loan_id).first()