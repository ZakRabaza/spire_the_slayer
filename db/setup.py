import psycopg2
from psycopg2 import sql
from database import DB_CONFIG

def create_database():
    """
        Connect to the default 'postgres' database and create the game database if it does not already exist.
    """
    conn = psycopg2.connect(**{**DB_CONFIG, "dbname": "postgres"})
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s",
                (DB_CONFIG["dbname"],))

    if not cur.fetchone():
        cur.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(DB_CONFIG["dbname"])
        ))
        print(f"Database '{DB_CONFIG['dbname']}' created.")
    else:
        print(f"Database '{DB_CONFIG['dbname']}' already exists.")

    cur.close()
    conn.close()

def run_sql_file(conn, filepath: str):
    """
        Read a SQL file and execute its contents against the provided connection.
    """
    with open(filepath, "r") as f:
        sql_content = f.read()
    with conn.cursor() as cur:
        cur.execute(sql_content)
    conn.commit()
    print(f"Ran {filepath}")

def setup():
    """
        Full setup sequence:
        1. Create the database if missing
        2. Run schema.sql to create tables
        3. Run seed.sql to insert static data
    """
    create_database()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        run_sql_file(conn, "schema.sql")
        run_sql_file(conn, "seed.sql")
        print("Setup complete.")
    finally:
        conn.close()

if __name__ == "__main__":
    setup()