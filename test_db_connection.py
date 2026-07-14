from dotenv import load_dotenv
import os 
import psycopg2
load_dotenv()

def db_connection():
conn=psycopg2.connect(os.getenv("DATABASE_URL"))

def create_table():
    conn= db_connection()
    cursor=conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS expenses(
                   id SERIAL PRIMARY KEY,
                   amount TEXT NOT NULL,
                   category TEXT NOT NULL<
                   description TEXT,
                   )
                   """)
print("Database Connected")
conn.close()