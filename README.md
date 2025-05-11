# Astrabotics

**Astrabotics** is a GenAI-powered Discord bot that lets users ask natural language questions about company data and instantly get answers by executing SQL queries on a connected database.

It is built with the OwlMind framework and enhanced with LLM-driven SQL generation, schema-aware prompting, and post-processing for accurate and secure database access.

---

## Features

- Ask plain-English questions like `“What is the revenue in May 2023?”`
- Automatically generates and runs SQL queries on your database
- Dynamically adapts to any schema using live introspection
- LLM-powered with prompt engineering + correction logic
- Handles time-based queries smartly with SQLite `strftime()`
- Returns results directly inside Discord
- Fallback rules and error handling

---

## Quickstart

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/astrabotics.git
cd astrabotics
```

---

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment

Create a `.env` file with your Discord bot token and LLM provider details:

```env
DISCORD_TOKEN=your_discord_bot_token
SERVER_URL=http://localhost:11434
SERVER_MODEL=llama3
SERVER_TYPE=ollama
SERVER_API_KEY=  # Optional, if needed
```

---

### 5. Launch the Bot

```bash
python bot-1.py
```

---

## Project Structure

```plaintext
astrabotics/
├── bot-1.py               # Bot startup script
├── sql_engine.py          # Core LLM+SQL processing logic
├── db_client.py           # Schema-aware DB interface
├── context.py             # Message context handler
├── rules/                 # Rule-based fallback responses
│   ├── bot-rules-common.csv
│   ├── bot-rules-fun.csv
│   └── bot-rules-errors.csv
├── .env                   # Your Discord and model credentials
└── company_data.db        # Your database (SQLite)
```

---

## Example Queries

- `@Astrabotics what is the revenue in May 2023?`
- `@Astrabotics show all departments`
- `@Astrabotics top 5 products by sales`
- `@Astrabotics what was the expense in Q1 2024?`

---

## Advanced Configurations

- You can switch LLMs using `SERVER_MODEL` and `SERVER_TYPE` (e.g., `ollama`, `openai`)
- Database schema is dynamically introspected — no hardcoding needed
- SQL is post-processed to fix time-based filters and remove invalid characters

---

## Built With

- [OwlMind](https://github.com/genilab-fau/owlmind)
- Python 3.10+
- SQLite
- Discord.py
- Your choice of LLM (Ollama, OpenAI, etc.)

---

## License

MIT License — free to use, modify, and share.

---

## Questions or Contributions?

Open an issue or drop a pull request. Happy hacking with Astrabotics!
