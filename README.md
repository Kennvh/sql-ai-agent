# AI SQL Agent

A FastAPI-powered AI agent that converts natural language questions into SQL queries and executes them against a PostgreSQL database. Built with OpenAI's GPT-4 for intelligent SQL generation.

## 🚀 Features

- **Natural Language to SQL**: Ask questions in plain English, get SQL queries
- **Smart Table Detection**: Automatically detects which database table you're referring to
- **Schema-Aware**: Understands your database structure and column names
- **Safe Execution**: Only allows SELECT queries for data security
- **Real-time Results**: Execute queries and get live data back
- **API-First**: RESTful API endpoints for easy integration
- **Auto-documentation**: Built-in Swagger UI for API exploration

## 🛠️ Tech Stack

### **Backend Framework**
- **FastAPI** - Modern, fast web framework for building APIs with Python
- **Uvicorn** - Lightning-fast ASGI server implementation
- **Pydantic** - Data validation and settings management

### **Database & ORM**
- **PostgreSQL** - Robust, open-source relational database
- **SQLAlchemy** - SQL toolkit and Object Relational Mapping (ORM)
- **Databases** - Async database support for Python
- **psycopg2** - PostgreSQL adapter for Python

### **AI & Machine Learning**
- **OpenAI GPT-4** - Advanced language model for SQL generation
- **OpenAI Python SDK** - Official Python library for OpenAI API

### **Development & Deployment**
- **Python 3.8+** - Programming language
- **python-dotenv** - Environment variable management
- **Docker** - Containerization (for production deployment)

### **API & Documentation**
- **Swagger UI** - Interactive API documentation (auto-generated)
- **RESTful API** - Standard HTTP endpoints
- **JSON** - Data exchange format

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   FastAPI App   │───▶│  OpenAI GPT-4   │
│  (Natural Lang) │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  PostgreSQL DB  │    │  Generated SQL  │
                       │                 │    │                 │
                       └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- **Python 3.8+** (check with `python3 --version`)
- **PostgreSQL** database (local or cloud-hosted)
- **OpenAI API Key** (get from [OpenAI Platform](https://platform.openai.com))
- **pip** (Python package manager)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ai-sql-agent
```

### 2. Install Dependencies
```bash
pip install -r req_imports.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
DATABASE_URL=postgresql://username:password@host:port/database_name
```

**Example DATABASE_URL:**
- **Local**: `postgresql://postgres:password@localhost:5432/mydb`
- **Cloud**: `postgresql://user:pass@host.com:5432/dbname`

### 4. Initialize Database
Run the database initialization script to create sample data:

```bash
python init_db.py
```

This creates a `customers` table with sample data for testing.

## 🚀 Quick Start

### 1. Start the Server
```bash
python sql_agent.py
```

The server will start at `http://127.0.0.1:8000`

### 2. Explore the API
Open your browser to `http://127.0.0.1:8000/docs` for interactive API documentation.

### 3. Test with cURL
```bash
# Generate SQL only
curl -X POST http://127.0.0.1:8000/generate-sql \
  -H "Content-Type: application/json" \
  -d '{"question":"How many customers with revenue over 1000?"}'

# Execute SQL and get results
curl -X POST http://127.0.0.1:8000/execute-sql \
  -H "Content-Type: application/json" \
  -d '{"question":"Show me all customers with revenue above 1000"}'
```

## 📚 API Endpoints

### POST `/generate-sql`
Converts natural language to SQL without executing it.

**Request:**
```json
{
  "question": "How many customers have revenue over 1000?"
}
```

**Response:**
```json
{
  "sql": "SELECT COUNT(*) FROM customers WHERE revenue > 1000",
  "warning": ""
}
```

### POST `/execute-sql`
Converts natural language to SQL and executes it, returning actual data.

**Request:**
```json
{
  "question": "Show me all customers with revenue above 1000"
}
```

**Response:**
```json
{
  "sql": "SELECT * FROM customers WHERE revenue > 1000",
  "rows": [
    {"id": 1, "name": "Alice", "revenue": 1200.00, "signup_date": "2023-05-01"},
    {"id": 3, "name": "Charlie", "revenue": 1100.25, "signup_date": "2023-07-22"}
  ]
}
```

## 🔧 How It Works

### 1. **Table Detection**
The agent analyzes your question to identify which database table you're referring to:

```python
async def detect_table(question: str) -> str:
    # Queries information_schema.tables to find matching table names
    # Returns the table name that appears in your question
```

### 2. **Schema Discovery**
Once the table is identified, it fetches the column structure:

```python
async def get_schema_for_question(question: str) -> dict:
    # Gets column names and types from information_schema.columns
    # Returns table structure for AI prompt
```

### 3. **AI SQL Generation**
Uses OpenAI GPT-4 to convert natural language to SQL:

```python
def generate_sql(question: str, schema: dict) -> str:
    # Creates a prompt with table structure and user question
    # Calls OpenAI API to generate SQL
    # Cleans up the response and returns executable SQL
```

### 4. **Safe Execution**
Only allows SELECT queries for data security:

```python
if not sql.strip().lower().startswith("select"):
    raise HTTPException(status_code=400, detail="Only SELECT statements are allowed")
```

## 🛡️ Security Features

- **Read-only Operations**: Only SELECT queries are allowed
- **Input Validation**: All requests are validated with Pydantic models
- **Error Handling**: Comprehensive error handling with meaningful messages
- **Environment Variables**: Sensitive data stored in `.env` file

## 📁 Project Structure

```
ai-sql-agent/
├── sql_agent.py          # Main FastAPI application
├── init_db.py            # Database initialization script
├── req_imports.txt       # Python dependencies
├── .env                  # Environment variables (create this)
└── README.md            # This file
```

## 📦 Dependencies

### **Core Dependencies** (`req_imports.txt`)
```
fastapi                    # Web framework
uvicorn[standard]         # ASGI server
openai                    # OpenAI API client
databases[postgresql]     # Async database support
sqlalchemy                # SQL toolkit and ORM
psycopg2-binary          # PostgreSQL adapter
python-dotenv            # Environment variable loader
```

### **Key Features by Technology**
- **FastAPI**: RESTful API endpoints, automatic documentation
- **SQLAlchemy**: Database schema management, query building
- **OpenAI GPT-4**: Natural language to SQL conversion
- **PostgreSQL**: Reliable data storage and retrieval
- **Pydantic**: Request/response validation and serialization

## 🔍 Example Questions

Try these natural language questions:

- **"How many customers do we have?"**
- **"Show me customers with revenue over 1000"**
- **"What's the average revenue per customer?"**
- **"List customers who signed up in 2023"**
- **"Find customers with names starting with 'A'**

## 🚨 Troubleshooting

### Common Issues

**1. "No module named 'dotenv'"**
```bash
pip install python-dotenv
```

**2. "pg_config executable not found"**
```bash
# On macOS
brew install postgresql

# On Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
```

**3. "You exceeded your current quota"**
- Check your OpenAI API billing at https://platform.openai.com/account/billing
- Add payment method if needed

**4. "Could not detect table"**
- Make sure your question mentions a table name that exists in your database
- Check that the table is in the 'public' schema

### Debug Mode
Run with verbose logging:
```bash
python sql_agent.py --log-level debug
```

## 🔄 Development

### Adding New Tables
1. Modify `init_db.py` to create your table
2. Run `python init_db.py` to update the database
3. The agent will automatically detect your new table

### Customizing Prompts
Edit the `generate_sql()` function in `sql_agent.py` to modify how the AI generates SQL.

### Environment Variables
Add new environment variables to `.env`:
```env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
LOG_LEVEL=INFO
```

## 🚀 Deployment

### Local Development
```bash
python sql_agent.py
```

### Production Deployment
1. **Docker** (recommended):
   ```dockerfile
   FROM python:3.11-slim
   COPY . /app
   WORKDIR /app
   RUN pip install -r req_imports.txt
   CMD ["python", "sql_agent.py"]
   ```

2. **Cloud Platforms**:
   - **Render**: Connect your GitHub repo
   - **Heroku**: Use Procfile
   - **Railway**: Direct deployment

### Environment Variables for Production
```env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
```



