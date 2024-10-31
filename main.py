from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from jwt_handler import create_jwt
from dependencies import get_current_user
import psycopg2
import json
import time


app = FastAPI()

# Endpoint to obtain the JWT token
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # For example purposes, use a hardcoded username and password
    if form_data.username == "testuser" and form_data.password == "password":
        token = create_jwt({"sub": form_data.username})
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Endpoint to get the current user

# Protected route that requires a valid JWT token
@app.get("/protected-route")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, {current_user['sub']}!"}
# Endpoint to get the current user


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
    cur.execute("SELECT * FROM expense_tracker LIMIT %s", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows
# End of root endpoint

@app.post("/add_budget/")
def add_budget(category: str, labels: str, amount: float, payee: str, note: str, payment_type: str, location: str):
    current_datetime = time.strftime('%Y-%m-%d %H:%M:%S')
    conn = create_connection()
    
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cur = conn.cursor()
        sql = """INSERT INTO expense_tracker (datetime, category, labels, amount, payee, note, payment_type, location)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        val = (current_datetime, category, labels, amount, payee, note, payment_type, location)
        cur.execute(sql, val)
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        conn.close()
    
    return {"message": "Budget added successfully"}

@app.delete("/truncate/")
def truncate():
    conn = create_connection()
    cur = conn.cursor()
    sql  = """TRUNCATE TABLE expense_tracker"""
    cur.execute(sql)
    conn.commit()
    conn.close()
    return {"message": "Table truncated successfully"}
# End of API endpoints


