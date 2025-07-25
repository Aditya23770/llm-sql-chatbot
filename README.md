
# LLM-Powered Chatbot with FastAPI and SQL Integration

## 1. Project Overview

This is a full-stack web application built to fulfill the requirements of the **"LLM-Powered Chatbot with FastAPI and SQL Integration"** assignment. It enables users to query a PostgreSQL database using natural language.

The application uses:
- A **Groq-hosted LLM** (Llama 3) to convert natural language to SQL queries.
- A **FastAPI** backend to handle API calls and query execution.
- A **ReactJS** frontend for user interaction and display.

---

## 2. Application Screenshots

### Main User Interface  
Users enter natural language queries here.  
![Main UI](UI.png)


### Successful Query Response  
Displays the generated SQL and retrieved results.  
![Main UI](example_query.png)


---

## 3. Requirements Checklist

### ✅ Core Requirements
- ✔️ **FastAPI Backend** for handling API requests.
- ✔️ **ReactJS Frontend** for user-friendly input and output.(Although you can skip this part and use postman for checking the backend, instructions are below)
- ✔️ **PostgreSQL Database** with schema: `(customer_id, name, gender, location)`.
- ✔️ **Groq LLM Integration** using Llama 3 to generate SQL queries.
- ✔️ **Sample Data**: Database seeded with 5+ entries.
- ✔️ **End-to-End Functionality**: Full flow from user input → SQL → results.

### ✅ Bonus Points Completed
- ✔️ **Logging** of queries and generated SQL.
- ✔️ **Error Handling** for invalid queries.
- ✔️ **Environment Variables** for secure credentials.
- ✔️ **API Security** via API key in request headers.

---

## 4. System Architecture (Project Flow)

1. **User Input** → Natural language query in frontend.
2. **API Request** → Sent to FastAPI backend with API key.
3. **LLM Processing** → Groq LLM converts query to SQL.
4. **SQL Execution** → Backend runs SQL on PostgreSQL.
5. **Response** → Result sent back to frontend.
6. **Display** → React displays formatted results to user.

---

## 5. Tech Stack

| Component     | Technology / Library                           |
|---------------|-----------------------------------------------|
| Backend       | Python 3, FastAPI, Uvicorn                    |
| Frontend      | ReactJS, JavaScript (ES6+), HTML5, CSS3      |
| Database      | PostgreSQL                                    |
| LLM API       | Groq (Llama 3 Model)                          |
| Python Libs   | SQLAlchemy, Psycopg2, python-dotenv, Groq     |

---

## 6. Project Setup and Execution

### 🔧 Setup Instructions

#### 1. Clone the Repository
```bash
git clone https://github.com/Aditya23770/llm-sql-chatbot
cd llm-sql-chatbot
```

#### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

#### Configure PostgreSQL
- Start PostgreSQL server
- Create a database (e.g., `chatbot_db`)
- Create a user with privileges

#### .env File
Create `.env` in the project root with:
```
GROQ_API_KEY="your_groq_api_key"
DB_URL="postgresql://your_user:your_password@localhost:5432/your_database"
API_KEY="your_chosen_secret_api_key"
```

#### Initialize Database
```bash
psql -d your_database -U your_user -f schema.sql
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
```

---

### ▶️ Running the Application

In **two separate terminals**:


#### Terminal 1 – Start Backend
```bash
uvicorn backend.main:app --reload
```
- URL: `http://127.0.0.1:8000`(but while using postman you for checking backend use `http://127.0.0.1:8000/query` )


##### 🧪 Testing the Backend with Postman

Follow the steps below to test the `/query` endpoint of your FastAPI backend using **Postman**.

---

### ✅ Step 1: Start the Backend Server

Ensure your FastAPI server is running:

```bash
uvicorn backend.main:app --reload
```

Server should be accessible at:  
`http://127.0.0.1:8000`

---

### 🛠️ Step 2: Open Postman and Create a New Request

1. Open **Postman**.
2. Click on **New → HTTP Request**.

---

### 🌐 Step 3: Set Method and URL

- **Method:** `POST`  
- **URL:** `http://127.0.0.1:8000/query`

---

### 🔐 Step 4: Configure Headers

Navigate to the **Headers** tab and add the following key-value pair:

| Key         | Value                     |
|-------------|---------------------------|
| `X-API-Key` | `your_secret_api_key_here` |

> Replace `your_secret_api_key_here` with the value of `API_KEY` from your `.env` file.

---

### 📝 Step 5: Configure Body

1. Go to the **Body** tab.
2. Select **raw**.
3. Set the type to **JSON** from the dropdown.
4. Enter your natural language query as JSON:

```json
{
  "query": "Show me all male customers from Delhi"
}
```

---

### 🚀 Step 6: Send the Request

Click the **Send** button.  
You should receive a JSON response containing:

- The **generated SQL query**
- The **results** returned from the database

---

### ✅ Sample Response (Example)

```json
{
  "sql": "SELECT * FROM customers WHERE gender = 'male' AND location = 'Delhi';",
  "results": [
    {
      "customer_id": 1,
      "name": "Raj Malhotra",
      "gender": "male",
      "location": "Delhi"
    }
  ]
}
```

---

This confirms that your LLM, FastAPI backend, and database integration are working correctly!


#### Terminal 2 – Start Frontend(if want an end-to-end setup)
```bash
cd frontend
npm start
```
- Opens: `http://localhost:3000`

---

## 7. Deliverables

- ✅ FastAPI backend (`/backend`)
- ✅ PostgreSQL schema (`schema.sql`)
- ✅ ReactJS frontend (`/frontend`)
