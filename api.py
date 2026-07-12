from fastapi import FastAPI
from pydantic import BaseModel
from db_tracker import create_table,add_expenses,get_all_expenses,get_total_spending, get_spending_by_category ,get_expenses_by_category
from extract_expense import extract_expense
import json

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

@app.get("/")
def read_root():
    return {"message": "Expense Tracker API is running"}
@app.get("/expenses", response_model=list[Expense])
def list_expenses():
    raw = get_all_expenses()
    result_list = []
    for row in raw:
        result_list.append(Expense(id=row[0], amount=row[1], category=row[2], description=row[3]))
    return result_list
@app.get("/expenses/total")
def total():
    return {"totals":get_total_spending()}
@app.get("/expenses/by-category")
def by_category():
    return get_spending_by_category()
@app.get("/expenses/category/{category_name}",response_model=list[Expense])
def get_by_category(category_name:str):
    raw=get_expenses_by_category(category_name)
    result_list=[]
    for row in raw:
        result_list.append(Expense(id=row[0],amount =row[1],category=row[2],description=row[3]))
    return result_list
@app.post("/expenses")
def create_expenses(expenses:NewExpense):
    add_expenses(expenses.amount,expenses.category,expenses.description)
    return {"message":"Expenses added succesfully"}
@app.post("/expenses/from-text")
@app.post("/expenses/from-text")
def create_expense_from_text(payload: ExpenseText):
    raw_reply = extract_expense(payload.text)
    try:
        parsed = json.loads(raw_reply)
    except json.JSONDecodeError:
        return {"error": "Could not understand the expense from that text. Try rephrasing."}

    if parsed["category"].lower() == "unknown" or parsed["amount"] == 0:
        return {"error": "Could not extract a valid expense from that text. Try rephrasing."}

    add_expenses(parsed["amount"], parsed["category"], parsed["description"])
    return {"message": "Expense added from text", "parsed": parsed}
    
    