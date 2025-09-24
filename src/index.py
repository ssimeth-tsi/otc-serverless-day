import json
import os
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import pymysql
from fastapi import FastAPI, HTTPException
from pymysql.cursors import DictCursor

# FastAPI App
app = FastAPI(title="User API", version="1.0.0")

# Database configuration derived from environment variables provided via user_data
DB_CONFIG: Dict[str, Any] = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "users"),
}

_REQUIRED_CONFIG_KEYS = ("host", "password")
for key in _REQUIRED_CONFIG_KEYS:
    if not DB_CONFIG[key]:
        raise RuntimeError(f"Missing required database configuration value: {key.upper()}")

SAMPLE_USERS: List[tuple[str, str, int]] = [
    ("Max Mustermann", "max@example.com", 30),
    ("Anna Schmidt", "anna@example.com", 25),
    ("Peter Müller", "peter@example.com", 35),
]

_db_initialized = False


def _base_connection_kwargs(include_database: bool) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {
        "host": DB_CONFIG["host"],
        "port": DB_CONFIG["port"],
        "user": DB_CONFIG["user"],
        "password": DB_CONFIG["password"],
        "autocommit": True,
        "cursorclass": DictCursor,
        "charset": "utf8mb4",
    }
    if include_database:
        kwargs["database"] = DB_CONFIG["database"]
    return kwargs


@contextmanager
def get_connection():
    """Yield a new MySQL connection using environment configuration."""
    conn = pymysql.connect(**_base_connection_kwargs(include_database=True))
    try:
        yield conn
    finally:
        conn.close()


def ensure_database_exists() -> None:
    """Create the target database if it does not exist."""
    with pymysql.connect(**_base_connection_kwargs(include_database=False)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )


def init_db() -> None:
    """Create the users table and populate sample data if empty."""
    global _db_initialized
    if _db_initialized:
        return

    ensure_database_exists()
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    age INT
                )
                """
            )
            cursor.execute("SELECT COUNT(*) AS count FROM users")
            count = cursor.fetchone()["count"]
            if count == 0:
                cursor.executemany(
                    "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)",
                    SAMPLE_USERS,
                )
    _db_initialized = True


def fetch_users() -> List[Dict[str, Any]]:
    """Retrieve all users using intentionally inefficient access patterns."""
    # First gather ids in one query
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users ORDER BY id")
            id_rows = cursor.fetchall()

    users: List[Dict[str, Any]] = []
    # For each id, open a brand new connection and query again
    for id_row in id_rows:
        user_id = id_row["id"]
        with get_connection() as per_user_conn:
            with per_user_conn.cursor() as cursor:
                # Redundant query to simulate extra load
                cursor.execute("SELECT COUNT(*) AS c FROM users")
                cursor.fetchone()
                cursor.execute(
                    "SELECT id, name, email, age FROM users WHERE id = %s",
                    (user_id,),
                )
                row = cursor.fetchone()
                if row:
                    users.append(
                        {
                            "id": row["id"],
                            "name": row["name"],
                            "email": row["email"],
                            "age": row["age"],
                        }
                    )
    return users


def fetch_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single user inefficiently by scanning all rows client-side."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, email, age FROM users ORDER BY RAND()")
            rows = cursor.fetchall()

    for row in rows:
        if row["id"] == user_id:
            return {
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "age": row["age"],
            }
    return None


def _health_payload() -> Dict[str, Any]:
    return {"status": "healthy", "service": "User API", "version": "1.0.1-pr-test"}


@app.get("/")
async def root():
    """Health Check"""
    return _health_payload()


@app.get("/users")
async def get_users():
    """Get all users"""
    init_db()
    try:
        return fetch_users()
    except Exception as exc:  # pragma: no cover - defensive for runtime exceptions
        raise HTTPException(status_code=500, detail="Failed to fetch users") from exc


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get single user"""
    init_db()
    user = fetch_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Handler for FunctionGraph
def handler(event, context):
    """FunctionGraph handler"""
    path = event.get("path", "/")
    method = event.get("httpMethod", "GET")

    try:
        init_db()
    except Exception as exc:  # pragma: no cover - defensive for runtime exceptions
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Database initialization failed"}),
        }

    if path == "/" and method == "GET":
        result = _health_payload()
    elif path == "/users" and method == "GET":
        try:
            result = fetch_users()
        except Exception:  # pragma: no cover - defensive for runtime exceptions
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Failed to fetch users"}),
            }
    elif path.startswith("/users/") and method == "GET":
        user_id_part = path.split("/")[-1]
        try:
            user_id = int(user_id_part)
        except ValueError:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid user ID"}),
            }

        user = fetch_user(user_id)
        if not user:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "User not found"}),
            }
        result = user
    else:
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Not found"}),
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result),
    }

