from fastapi.testclient import TestClient
from api import app
from dotenv import load_dotenv
import os
import json
load_dotenv()


client=TestClient(app)
def test_root_read():
    response=client.get("/")
    assert response.status_code==200
    assert response.json()=={"message":"Expense Tracker API is running"}
def test_expenses_requires_api_key():
    response=client.get("/expenses")
    assert response.status_code==422

def test_expenses_rejects_wrong_key():
    response=client.get("/expenses", headers={"x-api-key":"wrong_key"})
    assert response.status_code==401
def test_expenses_correct_key():
 
    realkey=os.getenv("API_SECRET_KEY")
    response=client.get("/expenses", headers={"x-api-key": realkey})
    assert response.status_code==200
def test_expenses_create():
    realkey=os.getenv("API_SECRET_KEY")
    response=client.post("/expenses", headers={"x-api-key":realkey}, 
    json={"amount": 10.0, "category": "test", "description": "pytest test insert"})
    assert response.status_code==200