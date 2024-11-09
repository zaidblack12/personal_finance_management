Here's a comprehensive README file for your FastAPI-based project:

```markdown
# Expense Tracker API

An API for managing user accounts and tracking expenses, built using **FastAPI** and **PostgreSQL**. The API supports user registration, login with JWT authentication, and CRUD operations on transactions.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [API Endpoints](#api-endpoints)
  - [User Authentication](#user-authentication)
  - [Expense Tracking](#expense-tracking)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Registration** and **Login** with password hashing.
- **JWT Authentication** for secure user access.
- **CRUD Operations** for expense tracking:
  - Add, update, view, and delete expenses.
  - Category and labels to organize expenses.
- **Transaction Management** per user, ensuring data privacy.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/expense-tracker-api.git
   cd expense-tracker-api
   ```

2. **Install dependencies**:
   Make sure you have Python 3.8+ installed, then install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL**:
   Ensure you have a PostgreSQL instance running. Update the database connection details in `create_connection()` in `main.py`.

## Environment Variables

This API requires several environment variables to configure JWT and database connectivity:

| Variable      | Description                  |
|---------------|------------------------------|
| `SECRET_KEY`  | Secret key for JWT encoding  |
| `ALGORITHM`   | Algorithm for JWT (e.g., `HS256`) |
| `DB_HOST`     | Database host                |
| `DB_USER`     | Database user                |
| `DB_PASSWORD` | Database password            |
| `DB_NAME`     | Database name                |

Create a `.env` file or use environment variables in your deployment configuration to store sensitive information.

## Database Setup

1. **Create the PostgreSQL Database and Tables**:

   Run the following SQL commands to set up the necessary tables:

   ```sql
   CREATE DATABASE bank;

   CREATE TABLE user_register (
       id SERIAL PRIMARY KEY,
       username VARCHAR(255) UNIQUE NOT NULL,
       email VARCHAR(255) UNIQUE NOT NULL,
       password VARCHAR(255) NOT NULL
   );

   CREATE TABLE expense_tracker (
       rrn SERIAL PRIMARY KEY,
       expense_date TIMESTAMP NOT NULL,
       category VARCHAR(255) NOT NULL,
       labels VARCHAR(255),
       amount DECIMAL(10, 2) NOT NULL,
       payee VARCHAR(255),
       note TEXT,
       payment_type VARCHAR(50),
       location VARCHAR(255),
       user_id INT REFERENCES user_register(id)
   );
   ```

2. **Apply the schema changes** in your PostgreSQL instance.

## API Endpoints

### User Authentication

- **Register a New User**
  - **Endpoint**: `POST /user/register/`
  - **Body**: `{ "username": "string", "email": "string", "password": "string" }`
  - **Response**: `{"message": "user registered successfully"}`

- **Login**
  - **Endpoint**: `POST /user/login/`
  - **Body**: `{ "username": "string", "password": "string" }`
  - **Response**: `{ "access_token": "string", "token_type": "bearer" }`

- **Get Current User**
  - **Endpoint**: `GET /user/me`
  - **Headers**: `Authorization: Bearer <token>`
  - **Response**: `{ "user_id": "integer" }`

### Expense Tracking

- **Add a New Transaction**
  - **Endpoint**: `POST /transaction/`
  - **Headers**: `Authorization: Bearer <token>`
  - **Body**: `{ "category": "string", "labels": "string", "amount": float, "payee": "string", "note": "string", "payment_type": "string", "location": "string" }`
  - **Response**: `{ "message": "Transaction added successfully" }`

- **Update a Transaction**
  - **Endpoint**: `PUT /transactions/{transaction_id}`
  - **Headers**: `Authorization: Bearer <token>`
  - **Body**: Same as Add Transaction
  - **Response**: `{ "message": "Transaction updated successfully" }`

- **Delete a Transaction**
  - **Endpoint**: `DELETE /transactions/{transaction_id}`
  - **Headers**: `Authorization: Bearer <token>`
  - **Response**: `{ "message": "Transaction deleted successfully" }`

- **Retrieve All Transactions (up to limit)**
  - **Endpoint**: `GET /`
  - **Query Parameters**: `limit (default=100)`
  - **Response**: List of transactions

- **Truncate Transactions Table**
  - **Endpoint**: `DELETE /truncate/`
  - **Response**: `{ "message": "Table truncated successfully" }`

## Usage

1. **Run the API**:
   Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

2. **Access API documentation**:
   - Interactive Swagger UI: `http://127.0.0.1:8000/docs`
   - Alternative ReDoc: `http://127.0.0.1:8000/redoc`

## Contributing

Feel free to contribute by creating pull requests or reporting issues. When contributing:
- Fork the repository.
- Create a feature branch.
- Commit your changes.
- Submit a pull request with a detailed description.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
```

This README provides details for configuring, deploying, and using your FastAPI project and follows best practices for clarity and structure. Let me know if you'd like adjustments or additional details.
