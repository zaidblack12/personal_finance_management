from fastapi import FastAPI
import psycopg2
import json


app = FastAPI()

#Database connection function

def create_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="bank",
            user="test_user",
            password="test@123"
            )
        return conn
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return None
    # End of database connection function

@app.get("/")
def read_root(limit: int=100):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transaction_data LIMIT %s", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows
# End of root endpoint
