import psycopg2
from database import DB_CONFIG

def reset():
    """
        Drop all tables in reverse dependency order, then re-run setup to rebuild from scratch.
        Development only — destroys all data.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("""
        DROP TABLE IF EXISTS run_cards CASCADE;
        DROP TABLE IF EXISTS runs     CASCADE;
        DROP TABLE IF EXISTS enemies  CASCADE;
        DROP TABLE IF EXISTS cards    CASCADE;
    """)
    print("All tables dropped.")

    cur.close()
    conn.close()

if __name__ == "__main__":
    confirm = input("Reset the database? This deletes all data. [y/N] ")
    if confirm.lower() == "y":
        reset()
        from setup import setup
        setup()
    else:
        print("Reset cancelled.")