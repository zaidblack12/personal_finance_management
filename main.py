from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer
import psycopg2
import time
import bcrypt   
import jwt

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"



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


app = FastAPI()

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class  UserLogin(BaseModel):
    username: str
    password: str

@app.post("/user/login/")
def login(user: UserLogin):
    conn = create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cur = conn.cursor()
        sql = "SELECT * FROM user_register WHERE username = %s"
        val = (user.username,)
        cur.execute(sql, val)
        db_user = cur.fetchone()  # Fetch the user data
        
        if db_user is None or not bcrypt.checkpw(user.password.encode('utf-8'), db_user[2].encode('utf-8')):  # Assuming hashed_password is in the 3rd column
            raise HTTPException(status_code=400, detail="Invalid credentials")

        # Create JWT token
        expiration = datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode({"sub": db_user[1], "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)  # Assuming username is in the 2nd column

        return {"access_token": token, "token_type": "bearer"}
    finally:
        cur.close()
        conn.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

@app.get("/user/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        conn = create_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        try:
            cur = conn.cursor()
            sql = "SELECT * FROM user_register WHERE username = %s"
            val = (username,)
            cur.execute(sql, val)
            db_user = cur.fetchone()
            if db_user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return {"username": db_user[1], "email": db_user[3]}
        finally:
            cur.close()
            conn.close()
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")



@app.post("/user/register/")
def  register_user(user:  UserCreate):
    conn = create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cur = conn.cursor()
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        sql = """INSERT INTO user_register (username, email, password)
                VALUES (%s, %s, %s)"""
        val = (user.username, user.email, hashed_password.decode('utf-8'))
        cur.execute(sql, val)
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        conn.close()
    
    return {"message": "user registered successfully"}

            # End of register_user function





@app.get("/")
def read_root(limit: int=100):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM expense_tracker LIMIT %s", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows
# End of root endpoint

@app.post("/transaction/")
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


