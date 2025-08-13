#!/usr/bin/env python3
"""
Initialization script for SQLite database with sample data
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from index import Base, UserDB

# Datenbank-Setup
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Insert sample data
db = SessionLocal()

try:
    # Check if data already exists
    existing = db.query(UserDB).first()
    if not existing:
        # Create sample users
        users = [
            UserDB(name="Max Mustermann", email="max@example.com", age=30),
            UserDB(name="Anna Schmidt", email="anna@example.com", age=25),
            UserDB(name="Peter Müller", email="peter@example.com", age=35),
            UserDB(name="Lisa Weber", email="lisa@example.com", age=28),
            UserDB(name="Tom Wagner", email="tom@example.com", age=42)
        ]
        
        for user in users:
            db.add(user)
        
        db.commit()
        print(f"✅ {len(users)} sample users created successfully")
    else:
        print("ℹ️  Database already contains data")
        
except Exception as e:
    print(f"❌ Error initializing database: {e}")
    db.rollback()
finally:
    db.close()