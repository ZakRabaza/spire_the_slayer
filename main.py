from db.database import get_conn

try:
    conn = get_conn()
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")