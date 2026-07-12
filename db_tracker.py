import sqlite3
# connect databese if not exixts
    # execute sql commands
def create_table():
    conn=sqlite3.connect("expenses.db")
    cursor=conn.cursor()
    cursor.execute("""
        Create table IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT
            
               ) 
               """)
    conn.commit()
    conn.close()
def add_expenses(amount,category,description):
    conn=sqlite3.connect("expenses.db")
    cursor=conn.cursor()
    cursor.execute("insert into expenses (amount,category,description) values (?,?,?)",
    (amount,category,description))
    conn.commit()
    conn.close()
    
def get_all_expenses():
    conn=sqlite3.connect("expenses.db")
    cursor=conn.cursor()
    cursor.execute("select * from expenses")
    result=cursor.fetchall()
    conn.close()
    return result
def get_total_spending():
    conn=sqlite3.connect("expenses.db")
    cursor=conn.cursor()
    cursor.execute("select sum(amount) from expenses")
    result=cursor.fetchone()
    conn.commit()
    conn.close()
    return result[0]
def get_spending_by_category():
    conn=sqlite3.connect("expenses.db")
    cursor=conn.cursor()
    cursor.execute("select category, sum(amount) from expenses GROUP BY category")
    result=cursor.fetchall()
    conn.close()
    return result
def get_expenses_by_category(category_name):
    conn=sqlite3.connect("expenses.db")
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE category=?",(category_name,))
    result=cursor.fetchall()
    conn.close()
    return result

if __name__=="__main__":
    create_table()
    add_expenses(150.0,"breakfast","lounch in university")
    print(get_all_expenses())
    print(get_total_spending())
    print(get_spending_by_category())



