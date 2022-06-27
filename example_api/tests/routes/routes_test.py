import requests
import requests_mock
import pytest
import json
from unittest.mock import patch
from flask import Flask, json, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from example_api.config import Config
from example_api import app as application
from example_api.db.orm import Loan, Payment
import example_api.db

"""
    Write unit tests so that your server doesn't have to be actually running. Use request_mock. Reference Flask tutorial

    Use Pydantic -> Update: Have implemented pydantic for every route in the API. It is a little concerning with all
                        of the boiler plate code due to the need for both a database (SQLAlchemy) compatible class
                        as well as a Pydantic compatible class.
                            Is there a better way to do this?
    Write unit tests properly
    Use timing functions from tutorial to better time functionality of API
    Look into raising error properly from Flask tutorial chapter 7
    Remember the time a payment to a loan was made, and don't let another payment be made in the next 30s to prevent 
        duplicate charges.
    Eeno , also look into rust.
"""

@pytest.fixture()
def client():
    with application.test_client() as client:
        application.config.from_object(Config)
        db = SQLAlchemy(application)
        migrate = Migrate(application, db)
        yield client

@patch("example_api.routes.loan.db_add")
def test_create_small_loan(mocker, client):
    #mocked_loan_maker = mocker.patch("example_api.db.crud.db_add")
    #mocked_loan_maker.side_effect = [None]
    test_data = {"loan_amount" : 2}
    resp = client.post("loan/", json = test_data)
    status_code = resp.status_code
    print(resp.data)
    resp = json.loads(resp.data)
    print(resp)
    assert resp['amount_owed'] == 2
    assert resp['loan_amount'] == 2
    assert status_code == 200

@patch("example_api.routes.loan.db_add")
def test_create_negative_loan(mocker, client):
    test_data = {"loan_amount" : -12}
    resp = client.post("/loan", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    print(resp)
    assert resp == [{'loc': ['loan_amount'], 'msg': "'loan_amount' must be greater than 0", 'type': 'value_error'}]
    assert status_code == 400

@patch("example_api.routes.loan.db_add", return_value = [None])
@patch("example_api.models.models.check_loan_existence", return_value = (1,))
@patch("example_api.routes.loan.loan_getter", return_value = Loan(loan_amount = 2, amount_owed = 2))
def test_create_and_get_loan(mock1, mock2, mock3, client):
    data = json.dumps({'loan_id' : 142,'loan_amount' : 2,'amount_owed' : 2})
    with patch("example_api.routes.loan.jsonify_loan", return_value = data):
        test_data = {"loan_amount" : 2}
        resp = client.post("/loan", json = test_data)
        status_code = resp.status_code
        resp = json.loads(resp.data)
        assert resp['amount_owed'] == 2
        assert resp['loan_amount'] == 2
        assert status_code == 200
        old_loan = resp
        test_data = {"loan_id" : 142}
        resp = client.get("/loan", json = test_data)
        status_code = resp.status_code
        resp = json.loads(resp.data)
        assert resp == old_loan

@patch("example_api.routes.loan.db_add", return_value = [None])
def test_create_large_loan(mocker, client):
    test_data = {"loan_amount" : 25000}
    resp = client.post("/loan", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['amount_owed'] == 25000
    assert resp['loan_amount'] == 25000
    assert status_code == 200

@patch("example_api.routes.loan.db_add", return_value = [None])
@patch("example_api.models.models.check_loan_existence", return_value = (1,))
@patch("example_api.routes.payment.loan_getter", return_value = Loan(loan_amount = 25000, amount_owed = 25000))
@patch("example_api.models.models.loan_getter", return_value = Loan(loan_amount = 25000, amount_owed = 25000))
def test_create_payment(mock1, mock2, mock3, mock4, client):
    test_data = {"loan_id" : 12, "payment_amount" : 20000}
    resp = client.post("/payment/", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['amount_owed'] == 5000
    assert resp['loan_amount'] == 25000
    assert resp['payment_amount'] == 20000
    assert not resp['refunded']
    assert status_code == 200

@patch("example_api.models.models.check_loan_existence", return_value = None)
def test_create_nonexistant_payment(mocker, client):
    test_data = {"loan_id" : -1, "payment_amount" : 20000}
    resp = client.post("/payment", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert status_code == 400
    print(resp)
    assert resp == [{'loc': ['loan_id'], 'msg': 'Error, loan id : -1 is not in the database of loans!', 'type': 'value_error'}]

@patch("example_api.routes.loan.db_add", return_value = [None])
@patch("example_api.models.models.check_loan_existence", return_value = (1,))
@patch("example_api.routes.payment.loan_getter", return_value = Loan(loan_amount = 25000, amount_owed = 25000))
@patch("example_api.models.models.loan_getter", return_value = Loan(loan_amount = 25000, amount_owed = 25000))
def test_create_payment_greater_than_loan(mock1, mock2, mock3, mock4, client):
    test_data = {"loan_id" : 142, "payment_amount" : 30000}
    loan_id = 142
    resp = client.post("/payment", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp == [{'loc': ['payment_amount'], 'msg': f'Error, loan {loan_id} only needs 25000, but the payment amount is 30000.', 'type': 'value_error'}]
    assert status_code == 400

@patch("example_api.routes.loan.db_add", return_value = [None])
@patch("example_api.models.models.check_loan_existence", return_value = (1,))
@patch("example_api.routes.payment.loan_getter", return_value = Loan(loan_amount = 25000, amount_owed = 25000))
@patch("example_api.models.models.loan_getter", return_value = Loan(loan_amount = 25000, amount_owed = 25000))
def test_create_negative_payment(mock1, mock2, mock3, mock4, client):
    test_data = {"loan_id" : 150, "payment_amount" : -1}
    resp = client.post("/payment", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    print(resp)
    assert resp == [{'loc': ['payment_amount'], 'msg': 'ensure this value is greater than 0', 'type': 'value_error.number.not_gt', 'ctx': {'limit_value': 0}}]
    assert status_code == 400

########## FINISH THESE LAST 3 TESTS!!!!!!!!!! ##############

@patch("example_api.routes.refund.loan_getter", return_value = Loan(loan_amount = 25000, amount_owed = 5000))
@patch("example_api.routes.refund.payment_getter", return_value = Payment(payment_amount = 20000, loan = Loan(loan_amount = 25000, amount_owed = 25000), refunded = False))
@patch("example_api.routes.refund.db_commit")
@patch("example_api.models.models.check_payment_existence", return_value = (1,))
@patch("example_api.models.models.payment_getter", return_value = Payment(payment_amount = 20000, loan = Loan(loan_amount = 25000, amount_owed = 25000), refunded = False))
def test_create_refund(mock1, mock2, mock3, mock4, mock5, client):
    """
        test_data = {"loan_amount" : 25000}
        resp = client.post("/loan", json = test_data)
        status_code = resp.status_code
        resp = json.loads(resp.data)
        assert resp['amount_owed'] == 25000
        assert resp['loan_amount'] == 25000
        assert status_code == 200
        # Now that we have the proper loan, we should pay it off.
        test_data = {"loan_id" : resp['loan_id'], "payment_amount" : 20000}
        resp = client.post("/payment", json = test_data)
        status_code = resp.status_code
        resp = json.loads(resp.data)
        assert resp['amount_owed'] == 5000
        assert resp['loan_amount'] == 25000
        assert resp['payment_amount'] == 20000
        assert not resp['refunded']
        assert status_code == 200
    """

    #Now that we have payed it off, we should refund the payment.
    test_data = {"payment_id" : 12}
    resp = client.post("/refund", json = test_data)
    print(resp)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['Loan Information']['amount_owed'] == 25000
    assert resp['Loan Information']['loan_amount'] == 25000
    assert resp['Payment Information']['payment_amount'] == 20000
    assert resp['Loan Information']['loan_id'] == resp['Payment Information']['loan_id']
    assert resp['Payment Information']['refunded'] == True
    assert status_code == 200

@patch("example_api.routes.refund.db_commit")
def test_create_nonexistant_refund(mock, client):
    test_data = {"payment_id" : -32}
    resp = client.post("/refund", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp == [{'loc': ['payment_id'], 'msg': 'Error, payment id : -32 is not in the database of payments!', 'type': 'value_error'}]
    assert status_code == 400

@patch("example_api.routes.refund.db_commit")
def test_create_faulty_id_for_refund(mock, client):
    test_data = {"payment_id" : "trying to break the API"}
    resp = client.post("/refund", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp == [{'loc': ['payment_id'], 'msg': 'value is not a valid integer', 'type': 'type_error.integer'}]
    assert status_code == 400