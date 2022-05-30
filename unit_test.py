import requests
import requests_mock
import pytest
import json

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
"""

def create_small_loan():
    test_data = {"loan_amount" : 2}
    resp = requests.post("http://localhost:5000/create_loan", data = json.dumps(test_data), headers={'Content-Type': 'application/json'})
    assert resp.json()['amount_owed'] == 2
    assert resp.json()['loan_amount'] == 2
    assert resp.status_code == 200

def create_and_get_loan():
    test_data = {"loan_amount" : 2}
    resp = requests.post("http://localhost:5000/create_loan", data = json.dumps(test_data), headers={'Content-Type': 'application/json'})
    assert resp.json()['amount_owed'] == 2
    assert resp.json()['loan_amount'] == 2
    assert resp.status_code == 200
    old_loan = resp.json()
    test_data = {"loan_id" : resp.json()['loan_id']}
    resp = requests.get("http://localhost:5000/get_loan", data = json.dumps(test_data), headers={'Content-Type': 'application/json'})
    new_loan = resp.json()
    assert new_loan == old_loan

def create_large_loan():
    test_data = {"loan_amount" : 25000}
    resp = requests.post("http://localhost:5000/create_loan", data = json.dumps(test_data), headers={'Content-Type': 'application/json'})
    assert resp.json()['amount_owed'] == 25000
    assert resp.json()['loan_amount'] == 25000
    assert resp.status_code == 200

def create_loan_and_payment():
    test_data = {"loan_amount" : 25000}
    resp = requests.post("http://localhost:5000/create_loan", data = json.dumps(test_data), headers={'Content-Type': 'application/json'})
    assert resp.json()['amount_owed'] == 25000
    assert resp.json()['loan_amount'] == 25000
    assert resp.status_code == 200
    # Now that we have the proper loan, we should pay it off.
    test_data = {"loan_id" : resp.json()['loan_id'], "payment_amount" : 20000}
    resp = requests.post("http://localhost:5000/create_payment", data = json.dumps(test_data), headers={'Content-Type': 'application/json'})
    assert resp.json()['amount_owed'] == 5000
    assert resp.json()['loan_amount'] == 25000
    assert resp.json()['payment_amount'] == 20000
    assert not resp.json()['refunded']
    assert resp.status_code == 200

def create_nonexistant_payment():
    test_data = {"loan_id" : -1, "payment_amount" : 20000}
    resp = requests.post("http://localhost:5000/create_payment", data = json.dumps(test_data), headers={'Content-Type': 'application/json'})
    assert resp.status_code == 400
    assert resp.json() == [{'loc': ['loan_id'], 'msg': 'Error, loan id : -1 is not in the database of loans!', 'type': 'value_error'}]

def create_payment_greater_than_loan():
    test_data = {"loan_amount" : 25000}
    resp = requests.post("http://localhost:5000/create_loan", data = json.dumps(test_data), headers={'Content-Type': 'application/json'})
    assert resp.json()['amount_owed'] == 25000
    assert resp.json()['loan_amount'] == 25000
    assert resp.status_code == 200
    # Now that we have the proper loan, we should pay it off.
    test_data = {"loan_id" : resp.json()['loan_id'], "payment_amount" : 30000}
    loan_id = resp.json()['loan_id']
    resp = requests.post("http://localhost:5000/create_payment", data = json.dumps(test_data), headers={'Content-Type': 'application/json'})
    print(resp.json())
    assert resp.json() == [{'loc': ['payment_amount'], 'msg': f'Error, loan {loan_id} only needs 25000, but the payment amount is 30000.', 'type': 'value_error'}]
    assert resp.status_code == 400

def create_refund():
    test_data = {"loan_amount" : 25000}
    resp = requests.post("http://localhost:5000/create_loan", data = json.dumps(test_data), headers={'Content-Type': 'application/json'})
    assert resp.json()['amount_owed'] == 25000
    assert resp.json()['loan_amount'] == 25000
    assert resp.status_code == 200
    # Now that we have the proper loan, we should pay it off.
    test_data = {"loan_id" : resp.json()['loan_id'], "payment_amount" : 20000}
    resp = requests.post("http://localhost:5000/create_payment", data = json.dumps(test_data), headers={'Content-Type': 'application/json'})
    assert resp.json()['amount_owed'] == 5000
    assert resp.json()['loan_amount'] == 25000
    assert resp.json()['payment_amount'] == 20000
    assert not resp.json()['refunded']
    assert resp.status_code == 200
    #Now that we have payed it off, we should refund the payment.
    test_data = {"payment_id" : resp.json()['payment_id']}
    resp = requests.post("http://localhost:5000/request_refund", data = json.dumps(test_data), headers={'Content-Type': 'application/json'})
    assert resp.json()['Loan Information']['amount_owed'] == 25000
    assert resp.json()['Loan Information']['loan_amount'] == 25000
    assert resp.json()['Payment Information']['payment_amount'] == 20000
    assert resp.json()['Loan Information']['loan_id'] == resp.json()['Payment Information']['loan_id']
    assert resp.json()['Payment Information']['refunded'] == True
    assert resp.status_code == 200

def create_nonexistant_refund():
    test_data = {"payment_id" : -32}
    resp = requests.post("http://localhost:5000/request_refund", data = json.dumps(test_data), headers={'Content-Type': 'application/json'})
    assert resp.json() == [{'loc': ['payment_id'], 'msg': 'Error, payment id : -32 is not in the database of payments!', 'type': 'value_error'}]
    assert resp.status_code == 400

def create_faulty_id_for_refund():
    test_data = {"payment_id" : "trying to break the API"}
    resp = requests.post("http://localhost:5000/request_refund", data = json.dumps(test_data), headers={'Content-Type': 'application/json'})
    assert resp.json() == [{'loc': ['payment_id'], 'msg': 'value is not a valid integer', 'type': 'type_error.integer'}]
    assert resp.status_code == 400

def test_small_loan():
    create_small_loan()
    #create_refund()
    #create_nonexistant_refund()
    #create_faulty_refund()

def test_create_and_get_loan():
    create_and_get_loan()

def test_large_loan():
    create_large_loan()

def test_loan_and_payment():
    create_loan_and_payment()

def test_create_nonexistant_payment():
    create_nonexistant_payment()

def test_create_payment_greater_than_loan():
    create_payment_greater_than_loan()

def test_create_refund():
    create_refund()

def test_create_nonexistant_refund():
    create_nonexistant_refund()

def test_create_faulty_id_for_refund():
    create_faulty_id_for_refund()