# Ai-journey
# Expense Tracker API

A backend API for tracking personal expenses, built with **Python**, **FastAPI**, and **SQLite** — with a natural-language expense entry feature powered by an LLM (via [Groq](https://console.groq.com)).

Instead of manually filling in amount/category/description every time, you can just say:

> "spent 30 dollars on coffee"

...and the API extracts the structured data and saves it for you.

## Features

- **CRUD-style expense tracking** backed by a real SQLite database (not a flat file)
- **Typed, validated API** using Pydantic models — every response is clean, labeled JSON
- **Filter by category** via a path parameter
- **Aggregate views** — total spending, and spending grouped by category
- **Natural language expense entry** — describe a purchase in plain English and have an LLM extract the amount, category, and description automatically
- **Guards against bad AI output** — rejects inputs the model can't confidently turn into a real expense, instead of silently saving garbage data

## Tech stack

- Python 3.12
- FastAPI + Pydantic
- SQLite (via the built-in `sqlite3` module)
- Groq API (Llama 3.3 70B) for natural language extraction
- `python-dotenv` for safe API key management

## Project structure

```
.
├── api.py              # FastAPI app — all endpoints
├── db_tracker.py        # Database layer (create_table, add_expenses, queries)
├── extract_expense.py    # LLM call that turns plain text into structured expense data
├── main.py               # CLI version of the tracker (menu-driven, no API)
├── requirements.txt      # Exact dependency versions
└── .env                  # Local secrets (NOT committed — see below)
```

## Setup

**1. Clone the repo and create a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Add your API key.**
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_actual_key_here
```
Get a free key (no credit card required) at [console.groq.com](https://console.groq.com).

> `.env` is listed in `.gitignore` and should never be committed. If you fork this repo, you must create your own `.env` file.

**4. Run the API:**
```bash
uvicorn api:app --reload
```

The API will be running at `http://127.0.0.1:8000`. Interactive docs are auto-generated at `http://127.0.0.1:8000/docs`.

## API Endpoints

| Method | Endpoint                          | Description                                      |
|--------|------------------------------------|---------------------------------------------------|
| GET    | `/`                                | Health check                                      |
| GET    | `/expenses`                        | List all expenses                                 |
| GET    | `/expenses/total`                  | Total spending across all expenses                |
| GET    | `/expenses/by-category`            | Spending totals grouped by category               |
| GET    | `/expenses/category/{category_name}` | All expenses in a specific category             |
| POST   | `/expenses`                        | Add an expense manually (amount, category, description) |
| POST   | `/expenses/from-text`              | Add an expense by describing it in plain English  |

### Example: adding an expense from natural language

```bash
curl -X POST http://127.0.0.1:8000/expenses/from-text \
  -H "Content-Type: application/json" \
  -d '{"text": "spent 30 dollars on coffee"}'
```

Response:
```json
{
  "message": "Expense added from text",
  "parsed": {
    "amount": 30,
    "category": "Food and Beverage",
    "description": "coffee"
  }
}
```

If the text doesn't describe a real expense, the API rejects it instead of saving nonsense data:
```bash
curl -X POST http://127.0.0.1:8000/expenses/from-text \
  -H "Content-Type: application/json" \
  -d '{"text": "asdkjaslkdj random gibberish"}'
```
```json
{"error": "Could not extract a valid expense from that text. Try rephrasing."}
```

## Running the CLI version

There's also a simple terminal menu (`main.py`) that uses the same database:
```bash
python3 main.py
```

## Notes on design decisions

- **SQLite over CSV**: enforces types, supports safe concurrent-ish access, and allows real querying (`WHERE`, `GROUP BY`) instead of loading everything into memory and filtering manually.
- **Parameterized queries only**: every SQL query uses `?` placeholders, never string formatting — this avoids SQL injection entirely.
- **Separate Pydantic models for input vs. output** (`NewExpense` vs. `Expense`): a new expense has no `id` yet (the database assigns it), while a stored expense does — the models reflect the actual shape of the data at each stage.
- **LLM output is never trusted blindly**: responses are parsed defensively, and outputs that look like a fallback/placeholder (`category: "Unknown"`, `amount: 0`) are explicitly rejected rather than saved.

## What I'd add next

- Authentication (API keys or JWT) — right now, anyone with the URL can read/write data
- Dockerize and deploy so the API is reachable outside localhost
- Retry logic for malformed LLM responses instead of a single hard failure
