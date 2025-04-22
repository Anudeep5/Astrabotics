# sql_engine.py

from owlmind.simple import SimpleEngine
from owlmind.bot import BotMessage
from datetime import datetime
import re

MAX_DISCORD_MESSAGE_LENGTH = 4000
MONTHS = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05",
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
}


class SQLEngine(SimpleEngine):
    def __init__(self, id, db, schema=None):
        super().__init__(id)
        self.db = db
        self.db_schema = self.generate_schema()
        self.load("rules/bot-rules-common.csv")
        self.load("rules/bot-rules-fun.csv")
        self.load("rules/bot-rules-errors.csv")

    def generate_schema(self) -> str:
        schema = ""
        for table in self.db.tables():
            columns = self.db.columns(table)
            col_defs = ", ".join(
                [f"{col['name']} {col['type'].upper()}" for col in columns]
            )
            schema += f"Table {table}({col_defs})\n"
        return schema.strip()

    def is_data_query(self, message: str):
        return True

    def format_result(self, result):
        if not result:
            return "No results found."
        elif len(result[0]) == 1:
            return "\n".join(f"- {row[0]}" for row in result)
        else:
            return "\n".join(", ".join(str(col) for col in row) for row in result)

    def clip(self, text: str) -> str:
        if len(text) > MAX_DISCORD_MESSAGE_LENGTH:
            return text[: MAX_DISCORD_MESSAGE_LENGTH - 10] + "\n[...]"
        return text

    def match_error_response(self, error_text: str):
        from owlmind.context import Context

        error_context = Context({"message": error_text.lower()})
        if error_context in self.plans:
            return error_context.compile(error_context.result)
        return None

    def get_dynamic_context(self):
        now = datetime.now()
        current_month = now.strftime("%Y-%m")
        current_year = now.strftime("%Y")
        q1 = ("01", "02", "03")
        q2 = ("04", "05", "06")
        q3 = ("07", "08", "09")
        q4 = ("10", "11", "12")
        return {
            "date_format": "YYYY-MM-DD",
            "current_month": current_month,
            "year": current_year,
            "quarter_1": tuple(f"{current_year}-{m}" for m in q1),
            "quarter_2": tuple(f"{current_year}-{m}" for m in q2),
            "quarter_3": tuple(f"{current_year}-{m}" for m in q3),
            "quarter_4": tuple(f"{current_year}-{m}" for m in q4),
        }

    def correct_sql(self, sql: str, override: str = None) -> str:
        sql = re.sub(
            r"WHERE\s+month\s*=\s*['\"](\d{4}-\d{2})['\"]",
            r"WHERE strftime('%Y-%m', month) = '\1'",
            sql,
            flags=re.IGNORECASE,
        )
        sql = re.sub(
            r"strftime\('%Y-%m',\s*month\)\s*=\s*['\"](\d{4})-\d{2}['\"]",
            r"strftime('%Y', month) = '\1'",
            sql,
            flags=re.IGNORECASE,
        )
        if override:
            sql = re.sub(
                r"strftime\('%Y', month\)\s*=\s*['\"]\d{4}['\"]", override, sql
            )
        return sql

    def process(self, context: BotMessage):
        message = context["message"]

        if message.lower().strip() in [
            "what is the database schema",
            "show me the schema",
            "what tables are there",
            "show schema",
        ]:
            context.response = self.clip(
                f"### Current Database Schema:\n```\n{self.db_schema}\n```"
            )
            return

        month_hint = None
        for month_text, month_num in MONTHS.items():
            match = re.search(rf"{month_text} (\d{{4}})", message.lower())
            if match:
                year = match.group(1)
                month_hint = f"strftime('%Y-%m', month) = '{year}-{month_num}'"
                break

        if context in self.plans:
            if self.debug:
                print("SQLEngine: matched plan rule")
            context.response = self.clip(context.compile(context.result))
            return

        if self.is_data_query(message):
            dynamic = self.get_dynamic_context()

            hint_instruction = (
                f"\n- Treat month-specific filters like this: {month_hint}"
                if month_hint
                else ""
            )

            prompt = f"""You are an AI assistant that generates correct and simple SQL queries.

Rules:
- Only use tables and columns that exist in the schema.
- DO NOT use JOINs unless the user explicitly asks to compare or combine data from multiple tables.
- DO NOT use aliases like T1 or T2 unless necessary.
- DO NOT guess columns — if unsure, say 'column not found'.
- Use simple SELECT statements when possible.
- All date fields are in format 'YYYY-MM-DD'.
- To filter by month, use: strftime('%Y-%m', column_name) = 'YYYY-MM'
  Example: strftime('%Y-%m', month) = '2024-05'
- To filter by year, use: strftime('%Y', column_name) = 'YYYY'
  Example: strftime('%Y', month) = '2024'{hint_instruction}

Database schema:
{self.db_schema}

Context:
- The current month is: {dynamic['current_month']}.
- Current year: {dynamic['year']}
- Q1: months starting with {dynamic['quarter_1']}
- Q2: months starting with {dynamic['quarter_2']}
- Q3: months starting with {dynamic['quarter_3']}
- Q4: months starting with {dynamic['quarter_4']}

User question: {message}

Return only the SQL query."""

            sql_query = self.model_provider.request(prompt)
            corrected_sql = self.correct_sql(sql_query, override=month_hint)

            try:
                result = self.db.query(corrected_sql)
                formatted = self.format_result(result)
                response = f"Query:\n```sql\n{corrected_sql}```\n\nResult:\n{formatted}"
                context.response = self.clip(response)
            except Exception as e:
                fallback = self.match_error_response(str(e))
                context.response = self.clip(
                    fallback if fallback else f"❌ SQL Error: {str(e)}"
                )
        else:
            context.response = self.clip(
                "#### DEFAULT: There are no rules setup for this request!"
            )
