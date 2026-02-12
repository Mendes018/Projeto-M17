import sqlite3
import os

db_path = 'z:\\OneDrive\\M17\\projetaoo\\database\\eventos_bilhetes.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    # try relative path if running from root
    db_path = 'database/eventos_bilhetes.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table info
    print("--- Schema for seats ---")
    cursor.execute("PRAGMA table_info(seats)")
    for col in cursor.fetchall():
        print(col)
        
    # Get some sample data
    print("\n--- Sample Data ---")
    cursor.execute("SELECT * FROM seats LIMIT 5")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
