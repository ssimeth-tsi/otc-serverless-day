from fastapi import FastAPI
from mangum import Mangum
import sqlite3
import json

# FastAPI App
app = FastAPI(title="User API", version="1.0.0")

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('/tmp/users.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  age INTEGER)''')
    
    # Add sample data if empty
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        sample_users = [
            ('Max Mustermann', 'max@example.com', 30),
            ('Anna Schmidt', 'anna@example.com', 25),
            ('Peter Müller', 'peter@example.com', 35)
        ]
        c.executemany('INSERT INTO users (name, email, age) VALUES (?, ?, ?)', sample_users)
    
    conn.commit()
    conn.close()

@app.get("/")
async def root():
    """Health Check"""
    return {"status": "healthy", "service": "User API", "version": "1.0.1-pr-test"}

@app.get("/users")
async def get_users():
    """Get all users"""
    init_db()
    conn = sqlite3.connect('/tmp/users.db')
    c = conn.cursor()
    c.execute('SELECT id, name, email, age FROM users')
    users = []
    for row in c.fetchall():
        users.append({
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'age': row[3]
        })
    conn.close()
    return users

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get single user"""
    init_db()
    conn = sqlite3.connect('/tmp/users.db')
    c = conn.cursor()
    c.execute('SELECT id, name, email, age FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'age': row[3]
        }
    return {"error": "User not found"}

# Handler für FunctionGraph
def handler(event, context):
    """FunctionGraph handler"""
    import json
    
    # Parse the event
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    path_parameters = event.get('pathParameters', {})
    
    # Initialize database on each request
    init_db()
    
    # Route handling
    if path == '/' and method == 'GET':
        result = {"status": "healthy", "service": "User API", "version": "1.0.1-pr-test"}
        
    elif path == '/users' and method == 'GET':
        conn = sqlite3.connect('/tmp/users.db')
        c = conn.cursor()
        c.execute('SELECT id, name, email, age FROM users')
        users = []
        for row in c.fetchall():
            users.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'age': row[3]
            })
        conn.close()
        result = users
        
    elif path.startswith('/users/') and method == 'GET':
        user_id = path.split('/')[-1]
        try:
            user_id = int(user_id)
            conn = sqlite3.connect('/tmp/users.db')
            c = conn.cursor()
            c.execute('SELECT id, name, email, age FROM users WHERE id = ?', (user_id,))
            row = c.fetchone()
            conn.close()
            if row:
                result = {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'age': row[3]
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'User not found'})
                }
        except ValueError:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Invalid user ID'})
            }
    else:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Not found'})
        }
    
    # Return successful response
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(result)
    }