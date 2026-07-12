from db_tracker import create_table,add_expenses,get_all_expenses,get_total_spending, get_spending_by_category

create_table()

while True:
    print("1:Add expenses")
    print("2:View all expenses")
    print("3:View all spending")
    print("4:View all expenses by category")
    print("5:Exits")
    
    choice =input("Enter an option:")
    
    if choice == "1":
        typed_amount=float(input("Enter the amount:"))
        typed_category=input("Enter the category:")
        typed_description=input("Enter the description:")
        add_expenses(typed_amount,typed_category,typed_description)
        print("Successfully Added the expenses")
    elif choice == "2":
        expenses=get_all_expenses()
        for exp in expenses:
            print(exp)
    elif choice == "3":
        print(get_total_spending())
    elif choice == "4":
        expenses=get_spending_by_category()
        for exp in expenses:
            print(exp)
    elif choice == "5":
        print("Good baye !")
        break
    else:
        print("Invalid option Try again!")
        
        