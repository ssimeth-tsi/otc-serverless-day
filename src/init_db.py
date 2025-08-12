#!/usr/bin/env python3
"""
Initialisierungsskript für die SQLite-Datenbank mit Beispieldaten
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from index import Base, UserDB

# Datenbank-Setup
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tabellen erstellen
Base.metadata.create_all(bind=engine)

# Beispieldaten einfügen
db = SessionLocal()

try:
    # Prüfen ob bereits Daten vorhanden sind
    existing = db.query(UserDB).first()
    if not existing:
        # Beispiel-Benutzer erstellen
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
        print(f"✅ {len(users)} Beispiel-Benutzer wurden erfolgreich erstellt")
    else:
        print("ℹ️  Datenbank enthält bereits Daten")
        
except Exception as e:
    print(f"❌ Fehler beim Initialisieren der Datenbank: {e}")
    db.rollback()
finally:
    db.close()