from datetime import datetime
from ..database import db
from example_api.db.orm import Loan, Payment
from example_api.db.crud import check_loan_existence, loan_getter, payment_getter, check_payment_existence
from pydantic import BaseModel, validator, conint
from pydantic.fields import ModelField

class LoanCreateModel(BaseModel):
    loan_amount: int

    @validator("loan_amount")
    def greater_than_zero(cls, v, field: ModelField):
        if v > 0:
            return v
        raise ValueError(f"'{field.alias}' must be greater than 0")


class Get_LoanModel(BaseModel):
    loan_id : int

    @validator("loan_id")
    def does_loan_exist(cls, loan_id):
        if check_loan_existence(loan_id) is None:
            raise ValueError(f"Error, id : {loan_id} is not in the database!")
        return loan_id

class PaymentModel(BaseModel):
    # Need to verify that this loan exists in the database.
    loan_id: int
    payment_amount: conint(gt=0)

    @validator("loan_id")
    def id_must_be_in_database(cls, loan_id):
        if check_loan_existence(loan_id) is None:
            raise ValueError(f"Error, loan id : {loan_id} is not in the database of loans!")
        return loan_id
    
    @validator("loan_id")
    def cannot_make_duplicate_payments(cls, loan_id):
        current_time = datetime.utcnow()
        payments = Payment.query.filter(loan_id == Payment.loan_id)
        for p in payments:
            if (current_time - p.time_created).seconds < 30:
                raise ValueError(f"Error, a payment has already been made to loan {loan_id} in the past 30 seconds. ")
        return loan_id

    # Create another validator for payment values ( Not negative. )
    @validator('payment_amount')
    def payment_greater_than_amount_owed(cls, payment_amount, values):
        if "loan_id" in values.keys():
            loan_id = values["loan_id"]
            if check_loan_existence(loan_id) is not None:
                loan = loan_getter(loan_id)
                if loan.amount_owed < payment_amount:
                    raise ValueError(f"Error, loan {loan_id} only needs {loan.amount_owed}, but the payment amount is {payment_amount}.")
                return payment_amount


class Get_PaymentModel(BaseModel):
    payment_id: int

    @validator("payment_id")
    def does_payment_exist(cls, payment_id):
        if db.session.query(Payment.id).filter_by(id = payment_id).first() is None:
            raise ValueError(f"Error, id : {payment_id} is not in the payment database!")
        return payment_id

class RefundModel(BaseModel):
    payment_id: int

    @validator("payment_id")
    def id_must_be_in_database(cls, payment_id):
        if check_payment_existence(payment_id) is None:
            raise ValueError(f"Error, payment id : {payment_id} is not in the database of payments!")
        return payment_id
    
    @validator("payment_id")
    def payment_must_not_be_already_refunded(cls, payment_id):
        existance = check_payment_existence(payment_id)
        if existance is not None:
            payment = payment_getter(payment_id)
            if payment.refunded:
                raise ValueError(f"Error, payment id : {payment_id} has already been refunded!")
        return payment_id