from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from db_tracker import create_table,add_expenses,get_all_expenses,get_total_spending, get_spending_by_category ,get_expenses_by_category
from extract_expense import extract_expense
import json
import os

app=FastAPI()
create_table()
class Expense(BaseModel):
    id:int
    amount:float
    category:str
    description:str
    
class NewExpense(BaseModel):
    amount:float
    category:str
    description:str
class ExpenseText(BaseModel):
    text: str
def verify_api_key(x_api_key:str = Header(...)):
    expected_api_key=os.getenv("API_SECRET_KEY")
    if x_api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.get("/debug-db")
def debug_db(auth: None = Depends(verify_api_key)):
    url = os.getenv("DATABASE_URL")
    if url and "@" in url:
        host_part = url.split("@")[1]
    else:
        host_part = "MISSING OR MALFORMED"
    return {"connected_host": host_part}

@app.get("/")
def read_root():
    return {"message": "Expense Tracker API is running"}

@app.get("/")
def read_root():
    return {"message": "Expense Tracker API is running"}
@app.get("/expenses", response_model=list[Expense])
def list_expenses(auth:None = Depends(verify_api_key)):
    raw = get_all_expenses()
    result_list = []
    for row in raw:
        result_list.append(Expense(id=row[0], amount=row[1], category=row[2], description=row[3]))
    return result_list
@app.get("/expenses/total")
def total(auth:None = Depends(verify_api_key)):
    return {"totals":get_total_spending()}
@app.get("/expenses/by-category")
def by_category(auth:None = Depends(verify_api_key)):
    return get_spending_by_category()
@app.get("/expenses/category/{category_name}",response_model=list[Expense])
def get_by_category(category_name:str,auth:None = Depends(verify_api_key)):
    raw=get_expenses_by_category(category_name)
    result_list=[]
    for row in raw:
        result_list.append(Expense(id=row[0],amount =row[1],category=row[2],description=row[3]))
    return result_list
@app.post("/expenses")
def create_expenses(expenses:NewExpense,auth:None = Depends(verify_api_key)):
    add_expenses(expenses.amount,expenses.category,expenses.description)
    return {"message":"Expenses added succesfully"}
@app.post("/expenses/from-text")
def create_expense_from_text(payload: ExpenseText,auth:None = Depends(verify_api_key)):
    raw_reply = extract_expense(payload.text)
    try:
        parsed = json.loads(raw_reply)
    except json.JSONDecodeError:
        return {"error": "Could not understand the expense from that text. Try rephrasing."}

    if parsed["category"].lower() == "unknown" or parsed["amount"] == 0:
        return {"error": "Could not extract a valid expense from that text. Try rephrasing."}

    add_expenses(parsed["amount"], parsed["category"], parsed["description"])
    return {"message": "Expense added from text", "parsed": parsed}
    
    