# FastAPI AI to SQL Agent

# Standard library imports
# For accessing environment variables and operating system functions
import os
# For accessing Python system-specific parameters and functions
import sys
# For type hints - Optional[T] means a value can be T or None
from typing import Optional

# Third-party library imports
# Loads environment variables from a .env file
from dotenv import load_dotenv
# FastAPI framework for building APIs
from fastapi import FastAPI, HTTPException
# Data validation and settings management using Python type annotations
from pydantic import BaseModel
# Async database support for Python
from databases import Database
# SQL toolkit and Object Relational Mapping (ORM)
from sqlalchemy import create_engine, MetaData
# OpenAI Python library for API interactions
from openai import OpenAI
# ASGI server implementation for running FastAPI applications
import uvicorn

#-----------------------------
# Setup environment variables, database connection, and Config
# Connect to OpenAI and PostgreSQL in render
#-----------------------------

# Load environment variables from .env file
load_dotenv()
# Get database connection string from environment
DATABASE_URL = os.getenv("DATABASE_URL")
# Get OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Check if required environment variables are set
if not DATABASE_URL or not OPENAI_API_KEY:
    print("Missing DATABASE_URL or OPENAI_API_KEY")
    sys.exit(1)

# Create async database connection for handling database operations
db = Database(DATABASE_URL)
# Initialize OpenAI client for making API calls to GPT models
openAI_client = OpenAI()
# Create metadata container to store database schema information
metaData = MetaData()
# Create SQLAlchemy engine for synchronous database operations
engine = create_engine(DATABASE_URL)

    
#-----------------------------
# Data Models
# Pydantic (Schemas for API model) models define what the API expects and returns
# Why Use Pydantic Schemas?
# Validation: Automatically checks that data is the right type
# Documentation: FastAPI uses these to generate API docs
# Type Safety: Helps catch errors before they happen
# Consistency: Ensures your API always returns the same structure
#-----------------------------

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    sql: str
    warning: Optional[str] = ""

class ExecuteResponse(BaseModel):
    sql:str
    rows: list

#-----------------------------
# Now set up FastAPI App Lifecycle
# FastAPI lifecycle events for connecting and disconnecting from the database
# Why Use Lifecycle Events?
# Without lifecycle events:
    # Database connection might not be ready when requests come in
    # Database connection might stay open after the app stops (memory leak)
# With lifecycle events:
    # Database is guaranteed to be connected before any requests are handled
    # Database is properly closed when the app stops
#-----------------------------

app = FastAPI(title="AI-to-SQL Agent")

@app.on_event("startup")
async def on_start():
    await db.connect()

@app.on_event("shutdown")
async def on_stop():
    await db.disconnect()


#-----------------------------
# Helper/Utility Functions for schema detection and prompt generation
#-----------------------------

# Function to detect which table the user is asking about
# Takes a natural language question and finds the matching database table
async def detect_table(question: str) -> str:
    # Query the database to get all table names in the public schema
    rows = await db.fetch_all("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
""")
    # Filter tables whose names appear in the user's question (case-insensitive)
    candidates = [r["table_name"] for r in rows if r["table_name"].lower() in question.lower()]
    # If exactly one table matches, return it
    if len(candidates) == 1:
        return candidates[0]
    # If zero or multiple tables match, raise an error with the candidates found
    raise HTTPException(400, detail=f"Could not detect table. Matches: {candidates}")

# Function to get the complete schema (table + columns) for a question
# This builds on detect_table to provide full database structure information
async def get_schema_for_question(question: str) -> dict:
    # Detect which table the user is asking about
    table = await detect_table(question)
    # Query to get all column names for the detected table, ordered by position
    cols = await db.fetch_all("""
        SELECT column_name from information_schema.columns
        WHERE table_name = :table ORDER by ordinal_position
""", values={"table": table})
    # Return both table name and list of column names
    return {
        "table_name": table,
        "columns": [c["column_name"] for c in cols]
    }

# Function to generate SQL query using OpenAI based on user question and database schema
# Takes a natural language question and database structure, returns executable SQL
def generate_sql(question: str, schema: dict) -> str:
    # Create a wrapper/prompt that tells OpenAI what to do
    prompt = f"""
    You are a helpful assistant that generates SQL queries.
    Given the table `{schema['table_name']}` and its columns:
    {', '.join(schema['columns'])}
    and the user's question:
    {question}
    Produce ONLY the SQL query, no explanation.
    """

    # Call OpenAI API to generate SQL query
    response = openAI_client.chat.completions.create(
        model="gpt-4o",  # Use GPT-4 model for best SQL generation
        messages=[{"role": "user", "content": prompt}],  # Send our prompt as user message
        temperature=0.0,  # Set to 0 for consistent, deterministic output
        max_tokens=300    # Limit response length to 300 tokens
    )
    
    # Clean up the AI response and return clean SQL
    # This chain of operations removes markdown formatting and extra whitespace
    return response.choices[0].message.content.strip().replace("```sql", "").replace("```", "").strip()


#-----------------------------
# API Endpoints
# These endpoints generate and optionally execute SQL from Natural Language
#-----------------------------

#uses given input from api
@app.post("/generate-sql", response_model=QueryResponse)
async def generate_sql_route(payload: QueryRequest):
    try:
        schema = await get_schema_for_question(payload.question)
        sql = generate_sql(payload.question, schema)
        return QueryResponse(sql=sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute-sql", response_model=ExecuteResponse)
async def execute_sql_route(payload: QueryRequest):
    try:
        schema = await get_schema_for_question(payload.question)
        sql = generate_sql(payload.question, schema)
        # this enforces read-only because we don't want to change anything
        if not sql.strip().lower().startswith("select"):
            raise HTTPException(status_code=400, detail="Only SELECT statements are allowed")
        rows = await db.fetch_all(query=sql)
        return ExecuteResponse(sql=sql, rows=[dict(r) for r in rows])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
    
#-----------------------------
# Run the app 
# Use uvicorn to launch the server and Use --reload for the dev mode.
#-----------------------------
if __name__ == "__main__":
    uvicorn.run("sql_agent:app", host="127.0.0.1", port=8000, reload=True)