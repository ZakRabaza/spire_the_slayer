import psycopg2

DB_CONFIG = {
    "dbname":   "spire_the_slayer",
    "user":     "postgres",
    "password": "root",
    "host":     "localhost",
    "port":     5432,
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)