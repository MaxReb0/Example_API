import requests
import requests_mock
import pytest
import json
from unittest.mock import patch
from flask import Flask, json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from app import app as application

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

def test_create_small_loan(client):
    test_data = {"loan_amount" : 2}
    resp = client.post("/create_loan", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['amount_owed'] == 2
    assert resp['loan_amount'] == 2
    assert status_code == 200

def test_create_negative_loan(client):
    test_data = {"loan_amount" : -12}
    resp = client.post("/create_loan", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    print(resp)
    assert resp == [{'loc': ['loan_amount'], 'msg': 'ensure this value is greater than 0', 'type': 'value_error.number.not_gt', 'ctx': {'limit_value': 0}}]
    assert status_code == 400

def test_create_and_get_loan(client):
    test_data = {"loan_amount" : 2}
    resp = client.post("/create_loan", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['amount_owed'] == 2
    assert resp['loan_amount'] == 2
    assert status_code == 200
    old_loan = resp
    test_data = {"loan_id" : resp['loan_id']}
    resp = client.get("/get_loan", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp == old_loan

def test_create_large_loan(client):
    test_data = {"loan_amount" : 25000}
    resp = client.post("/create_loan", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['amount_owed'] == 25000
    assert resp['loan_amount'] == 25000
    assert status_code == 200

def test_create_loan_and_payment(client):
    test_data = {"loan_amount" : 25000}
    resp = client.post("/create_loan", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['amount_owed'] == 25000
    assert resp['loan_amount'] == 25000
    assert status_code == 200
    # Now that we have the proper loan, we should pay it off.
    test_data = {"loan_id" : resp['loan_id'], "payment_amount" : 20000}
    resp = client.post("/create_payment", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['amount_owed'] == 5000
    assert resp['loan_amount'] == 25000
    assert resp['payment_amount'] == 20000
    assert not resp['refunded']
    assert status_code == 200

def test_get_payment(client):
    test_data = {"loan_amount" : 25000}
    resp = client.post("/create_loan", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['amount_owed'] == 25000
    assert resp['loan_amount'] == 25000
    assert status_code == 200
    # Now that we have the proper loan, we should pay it off.
    loan_id = resp['loan_id']
    test_data = {"loan_id" : resp['loan_id'], "payment_amount" : 20000}
    resp = client.post("/create_payment", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['amount_owed'] == 5000
    assert resp['loan_amount'] == 25000
    assert resp['payment_amount'] == 20000
    assert not resp['refunded']
    assert status_code == 200
    payment_id = resp["payment_id"]
    test_data = {"payment_id" : resp["payment_id"]}
    resp = client.get("get_payment", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp == {'amount_owed': 5000, 'loan_amount': 25000, 'loan_id': loan_id, 'payment_amount': 20000, 'payment_id': payment_id, 'refunded': False}
    assert status_code == 200

def test_create_nonexistant_payment(client):
    test_data = {"loan_id" : -1, "payment_amount" : 20000}
    resp = client.post("/create_payment", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert status_code == 400
    print(resp)
    assert resp == [{'loc': ['loan_id'], 'msg': 'Error, loan id : -1 is not in the database of loans!', 'type': 'value_error'}]


def test_create_payment_greater_than_loan(client):
    test_data = {"loan_amount" : 25000}
    resp = client.post("/create_loan", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['amount_owed'] == 25000
    assert resp['loan_amount'] == 25000
    assert status_code == 200
    # Now that we have the proper loan, we should pay it off.
    test_data = {"loan_id" : resp['loan_id'], "payment_amount" : 30000}
    loan_id = resp['loan_id']
    resp = client.post("/create_payment", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp == [{'loc': ['payment_amount'], 'msg': f'Error, loan {loan_id} only needs 25000, but the payment amount is 30000.', 'type': 'value_error'}]
    assert status_code == 400

def test_create_negative_payment(client):
    test_data = {"loan_amount" : 25000}
    resp = client.post("/create_loan", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['amount_owed'] == 25000
    assert resp['loan_amount'] == 25000
    assert status_code == 200
    # Now that we have the proper loan, we should pay it off.
    test_data = {"loan_id" : resp['loan_id'], "payment_amount" : -1}
    resp = client.post("/create_payment", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    print(resp)
    assert resp == [{'loc': ['payment_amount'], 'msg': 'ensure this value is greater than 0', 'type': 'value_error.number.not_gt', 'ctx': {'limit_value': 0}}]
    assert status_code == 400

def test_create_refund(client):
    test_data = {"loan_amount" : 25000}
    resp = client.post("/create_loan", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['amount_owed'] == 25000
    assert resp['loan_amount'] == 25000
    assert status_code == 200
    # Now that we have the proper loan, we should pay it off.
    test_data = {"loan_id" : resp['loan_id'], "payment_amount" : 20000}
    resp = client.post("/create_payment", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['amount_owed'] == 5000
    assert resp['loan_amount'] == 25000
    assert resp['payment_amount'] == 20000
    assert not resp['refunded']
    assert status_code == 200
    #Now that we have payed it off, we should refund the payment.
    test_data = {"payment_id" : resp['payment_id']}
    resp = client.post("/request_refund", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp['Loan Information']['amount_owed'] == 25000
    assert resp['Loan Information']['loan_amount'] == 25000
    assert resp['Payment Information']['payment_amount'] == 20000
    assert resp['Loan Information']['loan_id'] == resp['Payment Information']['loan_id']
    assert resp['Payment Information']['refunded'] == True
    assert status_code == 200

def test_create_nonexistant_refund(client):
    test_data = {"payment_id" : -32}
    resp = client.post("/request_refund", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp == [{'loc': ['payment_id'], 'msg': 'Error, payment id : -32 is not in the database of payments!', 'type': 'value_error'}]
    assert status_code == 400

def test_create_faulty_id_for_refund(client):
    test_data = {"payment_id" : "trying to break the API"}
    resp = client.post("/request_refund", json = test_data)
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert resp == [{'loc': ['payment_id'], 'msg': 'value is not a valid integer', 'type': 'type_error.integer'}]
    assert status_code == 400