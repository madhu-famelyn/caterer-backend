# CaterHub Backend API

Welcome to the backend API of **CaterHub** — a premium marketplace platform connecting clients with elite caterers. The backend is built using **FastAPI**, **SQLAlchemy ORM**, and supports **Neon PostgreSQL** or local **SQLite** databases.

---

## 🚀 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: PostgreSQL (Neon Cloud) / SQLite (Local development)
- **ORM**: SQLAlchemy
- **Authentication**: JWT tokens (via `python-jose`) and passwords hashed with Bcrypt (`passlib`)
- **Web Server**: Uvicorn

---

## 📂 Project Structure

```bash
caterer-backend/
├── routers/
│   ├── auth.py          # JWT login & auth routes
│   └── caterers.py      # Caterer profiles CRUD & filtering
├── database.py          # Database session & engine configurations
├── main.py              # Application entry point & mock data seeding
├── models.py            # SQLAlchemy models (Caterer schema)
├── schemas.py           # Pydantic validation schemas
├── security.py          # Password hashing & JWT generation helpers
├── requirements.txt     # Python package dependencies
└── .env                 # Environment variables (created locally)
```

---

## 🛠️ Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** installed.

### 2. Set Up a Virtual Environment
In the `caterer-backend` root folder, run:
```powershell
# Create venv
python -m venv venv

# Activate venv (Windows)
.\venv\Scripts\activate

# Activate venv (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a file named `.env` in the root of the backend folder:
```ini
DATABASE_URL=postgresql://neondb_owner:<password>@ep-little-sun-ahpo0btj-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```
*(If `DATABASE_URL` is omitted, the application will automatically fall back to a local SQLite database `caterhub.db`).*

### 5. Run the Server
Start the development server with hot-reload enabled. Choose the command corresponding to your operating system and terminal:

#### Windows (PowerShell)
```powershell
# 1. Activate the virtual environment
.\venv\Scripts\Activate.ps1

# 2. Start the Uvicorn server
python -m uvicorn main:app --reload
```

#### Windows (Command Prompt / CMD)
```cmd
# 1. Activate the virtual environment
call venv\Scripts\activate.bat

# 2. Start the Uvicorn server
python -m uvicorn main:app --reload
```

#### macOS / Linux
```bash
# 1. Activate the virtual environment
source venv/bin/activate

# 2. Start the Uvicorn server
uvicorn main:app --reload
```

Once started, the backend server will run at **`http://127.0.0.1:8000`**.

- **Interactive API Docs (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative Docs (ReDoc)**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔑 Key Features & Design Details

- **Automatic Seeding**: On startup, the backend automatically checks if the database is empty and populates it with a set of default premium caterers (e.g. *Noir & Flame Catering*, *Blue Plate Co.*, *Saffron Table*).
- **Flexible Schema Management**: Normalizes Postgres schemes and securely manages standard connection parameters across SQLite and PostgreSQL automatically.
- **Search & Filters**: Supports filtering caterers by city, cuisine type, and general search queries (`q`) along with pagination limit/skip filters.

---

## 📁 API Endpoints Summary

### Authentication
- `POST /api/v1/auth/login` - Obtain a JWT access token using email and password.

### Caterers
- `POST /api/v1/caterers/` - Register a new caterer profile.
- `GET /api/v1/caterers/` - List caterers with optional filtering (city, cuisine, query, limit/skip).
- `GET /api/v1/caterers/{caterer_id}` - Retrieve a single caterer profile details.
- `PUT /api/v1/caterers/{caterer_id}` - Update details of a caterer.
- `DELETE /api/v1/caterers/{caterer_id}` - Delete a caterer profile.
