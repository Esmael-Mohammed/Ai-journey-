from dotenv import load_dotenv
from groq import Groq
import os
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_expense(text):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You extract structured expense data from natural language. Respond with ONLY a JSON object with exactly these keys: amount (number), category (string), description (string). No other text, no markdown formatting, just the raw JSON object."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )
    raw_reply = response.choices[0].message.content
    return raw_reply

result = extract_expense("spent 200 birr on lunch with the team")
paresd=json.loads(result)
print(type(paresd))
print(paresd["amount"])
print(paresd["category"])
print(paresd["description"])