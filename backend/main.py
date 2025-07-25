import os
import re
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
import sqlalchemy

# Loads environment variables from the .env file in the root directory.
load_dotenv()

# Initializes the FastAPI application.
app = FastAPI()

# ====================================================================
# CORS MIDDLEWARE CONFIGURATION
# ====================================================================
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ====================================================================


# ====================================================================
# API KEY SECURITY
# ====================================================================
# Retrieves the master API key from the environment variables.
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-Key" # The name of the header to check for the key

# Defines the security scheme for API Key authentication.
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    """
    Dependency function to validate the API key from the request header.
    """
    if not api_key or api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or Missing API Key")
    return api_key
# ====================================================================


# Initializes the Groq client using the API key from the environment variables.
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Defines the system prompt for the LLM.
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
try:
    db_url = os.getenv("DB_URL")
    engine = sqlalchemy.create_engine(db_url)
except Exception as e:
    print(f"Error connecting to database: {e}")
    engine = None

# Defines the data model for the incoming request body using Pydantic.
class QueryRequest(BaseModel):
    query: str

# Applies the API key dependency to the /query endpoint.
@app.post("/query", dependencies=[Depends(get_api_key)])
def process_query(request: QueryRequest):
    """
    This endpoint is now protected. It will only execute if a valid API key
    is provided in the 'X-API-Key' header.
    """
    if not engine:
        raise HTTPException(status_code=500, detail="Database connection not available")

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.query},
            ],
            model="llama3-8b-8192",
        )
        raw_response = chat_completion.choices[0].message.content.strip()
        
        sql_match = re.search(r"SELECT.*?;", raw_response, re.DOTALL | re.IGNORECASE)
        
        if not sql_match:
            raise ValueError(f"The LLM did not return a valid SQL query. Response was: {raw_response}")

        sql_query = sql_match.group(0)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling LLM API or parsing response: {e}")

    try:
        with engine.connect() as connection:
            result = connection.execute(sqlalchemy.text(sql_query))
            results_as_dict = [dict(row) for row in result.mappings()]
            return {"sql_query": sql_query, "results": results_as_dict}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing SQL query: {e}. Generated SQL was: {sql_query}")

@app.get("/")
def read_root():
    return {"message": "LLM SQL Chatbot is running"}
