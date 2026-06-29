import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Load environment variables from .env file
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./caterhub.db")

# Normalise postgres:// scheme to postgresql:// if needed for SQLAlchemy compatibility
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure connection parameters optimized for either SQLite or remote PostgreSQL databases
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        poolclass=NullPool,
        connect_args={"connect_timeout": 30},  # allow Neon cold-start warmup time
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that provides a DB session with retry on Neon cold-start."""
    max_retries = 3
    for attempt in range(max_retries):
        db = SessionLocal()
        try:
            yield db
            return
        except Exception as e:
            db.close()
            err = str(e).lower()
            is_connection_err = any(k in err for k in [
                "connection", "operational", "timeout", "ssl", "could not connect",
                "server closed", "EOF", "connection reset"
            ])
            if is_connection_err and attempt < max_retries - 1:
                print(f"[DB] Connection failed (attempt {attempt + 1}), retrying in 2s...")
                time.sleep(2)
                continue
            raise
        finally:
            try:
                db.close()
            except Exception:
                pass


def warmup_db():
    """Ping the DB once to wake up Neon. Call on startup."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("[DB] Neon database connection warmed up successfully.")
    except Exception as e:
        print(f"[DB] Warmup ping failed (Neon may still be waking up): {e}")
