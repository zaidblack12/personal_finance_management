from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from fastapi import Depends, Security, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.utils import get_openapi
from jose import jwt
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

class TransactionCreate(BaseModel):
    category:str
    labels:str
    amount: float
    payee: str
    note: str 
    payment_type:str 
    location:str 
    # End of Transaction class

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="users/login",
    scopes={
        "read": "Read access to resources",
        "write": "Write access to resources",
        "admin": "Full admin access"
    }
)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Expense Tracker API",
        version="1.0.0",
        description="API for managing users and tracking expenses",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/user/login/",
                    "scopes": {
                        "read": "Read access to resources",
                        "write": "Write access to resources",
                        "admin": "Full admin access",
                    },
                }
            },
        }
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        scopes = payload.get("scopes", [])
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"user_id": user_id, "scopes": scopes}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
def check_scopes(required_scopes: list, user_scopes: list):
    for scope in required_scopes:
        if scope not in user_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient scope",
                headers={"WWW-Authenticate": f'Bearer scope="{scope}"'},
            )
@app.get("/secure-data/")
def read_secure_data(
    token_data: dict = Security(get_current_user, scopes=["read"])
):
    return {"message": "You have read access", "user_id": token_data["user_id"]}

@app.post("/secure-write/")
def write_secure_data(
    token_data: dict = Security(get_current_user, scopes=["write"])
):
    return {"message": "You have write access", "user_id": token_data["user_id"]}

@app.delete("/admin-only/")
def admin_access(
    token_data: dict = Security(get_current_user, scopes=["admin"])
):
    return {"message": "Admin access granted", "user_id": token_data["user_id"]}

@app.post("/user/register/")
def register_user(user:  UserCreate):
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


from fastapi.security import OAuth2PasswordRequestForm

@app.post("/user/login/")
def login(user: OAuth2PasswordRequestForm = Depends()):
    conn = create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cur = conn.cursor()
        sql = "SELECT * FROM user_register WHERE username = %s"
        val = (user.username,)
        cur.execute(sql, val)
        db_user = cur.fetchone()

        if db_user is None or not bcrypt.checkpw(user.password.encode('utf-8'), db_user[2].encode('utf-8')):
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        # Example: Assign default scopes (could be dynamic based on user role)
        scopes = ["read", "write"]

        # Create JWT token
        expiration = datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode(
            {
                "sub": db_user[1],
                "user_id": db_user[0],
                "scopes": scopes,  # Include scopes in the token
                "exp": expiration,
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

        return {"access_token": token, "token_type": "bearer"}
    finally:
        cur.close()
        conn.close()



@app.get("/user/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")  # Assuming you store user_id in the token
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")

@app.get("/")
def read_root( user_id: int = Depends(get_current_user)):
    conn = create_connection()
    cur = conn.cursor()
    
    sql = "SELECT * FROM expense_tracker WHERE user_id = %s"
    val = (user_id,)
    cur.execute(sql, val)
    rows = cur.fetchall()
    conn.close()
    return rows
# End of root endpoint

def get_current_user_id(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")



@app.post("/transaction/")
def add_transaction(transaction : TransactionCreate, user_id: int = Depends(get_current_user)):
    current_datetime = time.strftime('%Y-%m-%d %H:%M:%S')
    conn = create_connection()
    if conn is None:
        raise  HTTPException(status_code=500, detail="Database connection failed")
    try:
        cur = conn.cursor()
        sql = """INSERT INTO expense_tracker (expense_date, category, labels, amount, payee, note, payment_type, location, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        val = (
            current_datetime, transaction.category, 
            transaction.labels, 
            transaction.amount, 
            transaction.payee, 
            transaction.note, 
            transaction.payment_type, 
            transaction.location, 
            user_id  # Automatically injected from the token
        )
        cur.execute(sql, val)
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        conn.close()
    
    return {"message": "Transaction added successfully"}

@app.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: int, transaction: TransactionCreate, user_id: int = Depends(get_current_user)):
    conn = create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        check_sql = "SELECT * FROM expense_tracker WHERE rrn = %s AND user_id = %s"
        cur.execute(check_sql, (transaction_id, user_id))
        existing_transaction = cur.fetchone()

        if existing_transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found or not owned by user")

        sql = """UPDATE expense_tracker SET category = %s, labels = %s, amount = %s,  
        payee = %s, note = %s, payment_type = %s, location = %s
        WHERE rrn = %s AND user_id = %s"""
        val = (
            transaction.category,
            transaction.labels,
            transaction.amount,
            transaction.payee,
            transaction.note,
            transaction.payment_type,
            transaction.location,
            transaction_id,
            user_id
        )
        cur.execute(sql, val)

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="No update made, possibly due to incorrect transaction ID or user ID.")

        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()
    
    return {"message": "Transaction updated successfully"}

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

@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, user_id: int = Depends(get_current_user)):
    conn = create_connection()
    cur = conn.cursor()
    sql = """DELETE FROM expense_tracker WHERE rrn = %s AND user_id = %s"""
    val = (transaction_id, user_id)
    
    cur.execute(sql, val)
    
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found or not owned by user")
    
    conn.commit()
    conn.close()
    
    return {"message": "Transaction deleted successfully"}




