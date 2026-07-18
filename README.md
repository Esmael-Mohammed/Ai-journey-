# Expense Tracker API

A production-shaped backend for tracking personal expenses — built with **Python**, **FastAPI**, and **PostgreSQL**, containerized with **Docker**, deployed live on **Render**, and featuring **two AI-powered ways to interact with your data**: natural-language expense entry, and a retrieval-augmented question-answering endpoint.

> Live deployment: `https://ai-journey-75ru.onrender.com`

Instead of manually filling in amount/category/description, you can just say:

> "spent 30 dollars on coffee"

...and the API extracts and saves it. You can also *ask* about your spending in plain English:

> "how much did I spend on taxis?"

...and get a real answer, grounded in your actual data — not a guess.

## Features

- **CRUD expense tracking** backed by a real, persistent PostgreSQL database
- **Typed, validated API** using Pydantic models — every response is clean, labeled JSON
- **API key authentication** — every data endpoint requires a valid `x-api-key` header
- **Containerized with Docker** — runs identically anywhere, with persistent storage via volumes locally and a managed Postgres instance in production
- **Live deployment on Render**, including environment-based secrets management
- **Natural language expense entry** — describe a purchase, let an LLM extract the structured data
- **Guards against bad AI output** — rejects inputs the model can't confidently turn into a real expense, instead of silently saving garbage data
- **Retrieval-Augmented Q&A** — ask questions about your spending; the system retrieves the actually-relevant rows from the database first, then generates an answer grounded in that real data, and explicitly says so when it doesn't have enough information rather than guessing
- **Automated test suite (pytest)** covering health checks, authentication (missing/wrong/correct key), and data creation, with automatic cleanup so tests never leave junk data behind

## Tech stack

- Python 3.12
- FastAPI + Pydantic
- PostgreSQL (via `psycopg2`), hosted on Render
- Docker (containerized app + Dockerfile with layer-caching optimizations)
- Groq API (Llama 3.3 70B) for natural language extraction and RAG
- `pytest` + `httpx` for automated testing
- `python-dotenv` for safe secrets management

## Project structure

```
.
├── api.py                # FastAPI app — all endpoints, auth dependency
├── db_tracker.py          # PostgreSQL data layer (create_table, CRUD, queries)
├── extract_expense.py      # LLM call: natural language -> structured expense
├── rag_query.py             # RAG pipeline: intent extraction -> SQL retrieval -> grounded answer
├── main.py                  # CLI version of the tracker (menu-driven, no API)
├── test_api.py                # pytest suite with cleanup fixture
├── Dockerfile                  # Container build definition
├── .dockerignore                 # Excludes venv, cache, secrets from the image
├── requirements.txt                # Exact dependency versions
└── .env                              # Local secrets (NOT committed — see below)
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

**3. Add your secrets.** Create a `.env` file in the project root:
```
DATABASE_URL=your_postgres_connection_string
GROQ_API_KEY=your_groq_api_key
API_SECRET_KEY=a_long_random_string_you_generate
```
- Get a free Groq key (no credit card required) at [console.groq.com](https://console.groq.com).
- Generate a strong `API_SECRET_KEY` with: `python3 -c "import secrets; print(secrets.token_hex(32))"`
- A free PostgreSQL database can be created directly on [Render](https://render.com).

> `.env` is listed in `.gitignore` and `.dockerignore` and should never be committed or baked into the Docker image.

**4. Run the API locally:**
```bash
uvicorn api:app --reload
```
API runs at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

**5. Or run it in Docker:**
```bash
docker build -t expense-tracker .
docker run -p 8000:8000 --env-file .env expense-tracker
```

## API Endpoints

All endpoints below (except `/`) require an `x-api-key` header matching your `API_SECRET_KEY`.

| Method | Endpoint                            | Description                                          |
|--------|---------------------------------------|-------------------------------------------------------|
| GET    | `/`                                    | Health check (no auth required)                       |
| GET    | `/expenses`                            | List all expenses                                      |
| GET    | `/expenses/total`                      | Total spending across all expenses                     |
| GET    | `/expenses/by-category`                | Spending totals grouped by category                    |
| GET    | `/expenses/category/{category_name}`    | All expenses in a specific category                    |
| POST   | `/expenses`                            | Add an expense manually (amount, category, description) |
| POST   | `/expenses/from-text`                   | Add an expense by describing it in plain English        |

### Example: adding an expense from natural language

```bash
curl -X POST http://127.0.0.1:8000/expenses/from-text \
  -H "x-api-key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"text": "spent 30 dollars on coffee"}'
```

Response:
```json
{
  "message": "Expense added from text",
  "parsed": {"amount": 30, "category": "Food and Beverage", "description": "coffee"}
}
```

If the text doesn't describe a real expense, the API rejects it instead of saving nonsense:
```json
{"error": "Could not extract a valid expense from that text. Try rephrasing."}
```

### Example: asking a question about your spending (RAG)

```bash
python3 rag_query.py
```
Internally, this:
1. Uses an LLM to extract a structured filter (category / keyword) from the question
2. Runs a real SQL query (`WHERE category = ... OR description ILIKE ...`) against the database
3. Feeds only the retrieved, real rows back to the LLM to generate the final answer

If nothing relevant is found, the system says so explicitly rather than guessing:
> "There is no data provided to answer the question."

## Running the CLI version

```bash
python3 main.py
```

## Running the tests

```bash
pytest test_api.py -v
```

Tests cover the health check, all three auth states (missing / wrong / correct key), and expense creation. A cleanup fixture automatically removes any test-created data after each run, so the suite is safe to run as often as you like without polluting real data.

## Design decisions worth knowing

- **PostgreSQL over SQLite in production**: the app is containerized and deployed on infrastructure with ephemeral disk storage — a database that lives inside the container would lose all data on every redeploy. Postgres runs as an independent, persistent service the app connects to over the network.
- **Parameterized queries only** — every SQL query uses `%s`/`?` placeholders, never string formatting, to prevent SQL injection.
- **Separate Pydantic models for input vs. output** (`NewExpense` vs. `Expense`) — a new expense has no `id` yet (the database assigns it); a stored expense does.
- **LLM output is never trusted blindly** — both the natural-language entry feature and the RAG pipeline explicitly check for and reject low-confidence/fallback responses (e.g., `category: "Unknown"`, empty retrieval results) rather than silently acting on them.
- **RAG uses SQL-based retrieval, not embeddings, for now** — the current dataset is small and structured, so exact/fuzzy SQL matching (`=` and `ILIKE`) is a legitimate, simpler retrieval strategy. Embedding-based semantic search is a planned next step for handling less structured or fuzzier queries.

## What I'd add next

- Embedding-based (vector) retrieval for more flexible, semantic RAG queries
- CI (GitHub Actions) to run the test suite automatically on every push
- A dedicated, isolated test database instead of a cleanup-fixture-based compromise
- Retry logic for malformed LLM responses instead of a single hard failure