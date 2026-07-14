import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()
def db_connection():
    conn=psycopg2.connect(os.getenv("DATABASE_URL"))
    return conn

def create_table():
    conn= db_connection()
    cursor=conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS expenses(
                   id SERIAL PRIMARY KEY,
                   amount REAL NOT NULL,
                   category TEXT NOT NULL,
                   description TEXT
                   )
                   """)
    conn.commit()
    conn.close()
def add_expenses(amount,category,description):
    conn=db_connection();
    cursor=conn.cursor()
    cursor.execute("insert into expenses (amount,category,description) values (%s,%s,%s)",
    (amount,category,description))
    conn.commit()
    cursor.close()
    conn.close()
    
def get_all_expenses():
    conn=db_connection();
    cursor=conn.cursor()
    cursor.execute("select * from expenses")
    result=cursor.fetchall()
    conn.close()
    return result
def get_total_spending():
    conn=db_connection()
    cursor=conn.cursor()
    cursor.execute("select sum(amount) from expenses")
    result=cursor.fetchone()
    conn.commit()
    conn.close()
    return result[0]
def get_spending_by_category():
    conn=db_connection()
    cursor=conn.cursor()
    cursor.execute("select category, sum(amount) from expenses GROUP BY category")
    result=cursor.fetchall()
    conn.close()
    return result
def get_expenses_by_category(category_name):
    conn=db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE category=%s",(category_name,))
    result=cursor.fetchall()
    conn.close()
    return result

if __name__=="__main__":
    create_table()
    add_expenses(150.0,"breakfast","lounch in university")
    print(get_all_expenses())
    print(get_total_spending())
    print(get_spending_by_category())



