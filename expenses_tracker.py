from db_tracker import conn,cursor

def add_expenses(amount,category,description):
    cursor.execute("insert into expenses (amount,category,description) values (?,?,?)",(amount,category,description))
    conn.commit()
    conn.close()
    
def get_all_expenses():
    cursor.execute("select * from expenses")
    result=cursor.fetchall()
    conn.commit()
    conn.close()
def total_spending():
    cursor.execute("select sum(amount) from expenses")
    conn.commit()
    conn.close()

    