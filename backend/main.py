import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
import sqlalchemy

# Loads environment variables from the .env file in the root directory.
load_dotenv()

# Initializes the FastAPI application.
app = FastAPI()

# Initializes the Groq client using the API key from the environment variables.
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Defines the system prompt for the LLM.
# This version is specifically for the simple, single-table schema.
SYSTEM_PROMPT = """You are a specialized SQL Code Bot. Your single purpose is to convert a user's question into a single, clean, valid PostgreSQL query for the table provided below.

### PRIMARY DIRECTIVE
You will output ONLY the SQL query required. Nothing else. No comments, no explanations.

### DATABASE SCHEMA
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(50),
    location VARCHAR(255)
);

### RULES
1.  For all text comparisons (gender, location, name), you MUST use the `ILIKE` operator for case-insensitivity.
2.  For names, use wildcards for partial matches. Example: `name ILIKE '%arjun%'`.
3.  Do NOT use JOINs. All data is in the `customers` table.

### EXAMPLES
* **User:** "Show me all female customers from Mumbai"
* **Your SQL:** SELECT * FROM customers WHERE gender ILIKE 'female' AND location ILIKE 'mumbai';

* **User:** "who is arjun"
* **Your SQL:** SELECT * FROM customers WHERE name ILIKE '%arjun%';

### FINAL OUTPUT
Your entire response must be only the raw SQL query.
"""

# Establishes the connection to the PostgreSQL database.
# The connection URL is retrieved from the environment variables.
try:
    db_url = os.getenv("DB_URL")
    engine = sqlalchemy.create_engine(db_url)
except Exception as e:
    print(f"Error connecting to database: {e}")
    engine = None

# Defines the data model for the incoming request body using Pydantic.
# This ensures the request has a 'query' field of type string.
class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def process_query(request: QueryRequest):
    """
    This endpoint receives a natural language query, converts it to SQL using the LLM,
    executes the SQL against the database, and returns the result.
    """
    # Checks if the database connection was successfully established.
    if not engine:
        raise HTTPException(status_code=500, detail="Database connection not available")

    try:
        # Step 1: Sends the user's query and the system prompt to the Groq API.
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.query},
            ],
            model="llama3-8b-8192",
        )
        # Extracts the raw text response from the LLM.
        raw_response = chat_completion.choices[0].message.content.strip()
        
        # Uses regex to find and extract only the SQL query from the response,
        # making the system resilient to extra conversational text from the LLM.
        sql_match = re.search(r"SELECT.*?;", raw_response, re.DOTALL | re.IGNORECASE)
        
        if not sql_match:
            raise ValueError(f"The LLM did not return a valid SQL query. Response was: {raw_response}")

        sql_query = sql_match.group(0)

    except Exception as e:
        # Handles potential failures in the LLM API call or response parsing.
        raise HTTPException(status_code=500, detail=f"Error calling LLM API or parsing response: {e}")

    try:
        # Step 2: Executes the generated SQL query against the database.
        with engine.connect() as connection:
            result = connection.execute(sqlalchemy.text(sql_query))
            # Converts the database rows to a list of dictionaries for JSON compatibility.
            # This line has been corrected.
            results_as_dict = [dict(row) for row in result.mappings()]
            return {"sql_query": sql_query, "results": results_as_dict}

    except Exception as e:
        # Handles errors during SQL execution, such as syntax errors in the generated query.
        raise HTTPException(status_code=400, detail=f"Error executing SQL query: {e}. Generated SQL was: {sql_query}")

@app.get("/")
def read_root():
    """
    Defines the root endpoint to confirm the server is running.
    """
    return {"message": "LLM SQL Chatbot is running"}
