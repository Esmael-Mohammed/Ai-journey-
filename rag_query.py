from groq import Groq
import os
import json
from dotenv import load_dotenv
load_dotenv()
client=Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_query_intent(question):
    response=client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You extract query filters from questions about expense data.
                Respond with ONLY a JSON object with these keys:
                - category (string or null if not mentioned)
                - description_keyword (string or null - a keyword to search for in the description, or null)
                No other text, just the JSON object."""
            },
            {"role": "user", "content": question}
        ]
    )
    return json.loads(response.choices[0].message.content)

def retrieve_expenses(category=None, description_keyword=None):
    from db_tracker import db_connection  # or whatever your connection function is named
    conn = db_connection()
    cursor = conn.cursor()
    
    term = category or description_keyword
    if term:
        cursor.execute(
            "SELECT * FROM expenses WHERE category = %s OR description ILIKE %s",
            (term, f"%{term}%")
        )
    else:
        cursor.execute("SELECT * FROM expenses")
    
    result = cursor.fetchall()
    conn.close()
    return result
def generate_answer(question, retrieved_rows):
    context = "\n".join([f"Amount: {row[1]}, Category: {row[2]}, Description: {row[3]}" for row in retrieved_rows])
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Answer the user's question using ONLY the expense data provided below. If the data doesn't contain enough information to answer, say so clearly rather than guessing."
            },
            {
                "role": "user",
                "content": f"Expense data:\n{context}\n\nQuestion: {question}"
            }
        ]
    )
    return response.choices[0].message.content
if __name__ == "__main__":
    question = "how much did I spend on video games?"
    intent = extract_query_intent(question)
    rows = retrieve_expenses(category=intent["category"], description_keyword=intent["description_keyword"])
    print("Retrieved rows:", rows)
    answer = generate_answer(question, rows)
    print(answer)