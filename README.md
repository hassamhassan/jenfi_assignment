# Jenfi Long Mail Service - API Documentation

## Table of Contents

- [Introduction](#introduction)
- [Setup Instructions](#setup-instructions)
- [Dependencies](#dependencies)
- [API Endpoints](#api-endpoints)
- [Additional Information](#additional-information)

## Introduction

Welcome to the Jenfi Long Mail Service Documentation. This API powers a parcel delivery system, providing functionalities for parcel creation, train management, and cost optimization. It's implemented using Python and FastAPI.
## Setup Instructions

To set up and run the Jenfi Long Mail Service API on your local machine, follow these steps:

**Create and Activate Virtual Environment**

To create virtual environment, use the following command.
```shell
python -m venv <env>
```
To activate virtual environment, use the following command.
```shell
source <env>/bin/activate
```
**Install Dependencies**:

Ensure you have Python 3.7 or higher installed. Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
   ```

**Database Configuration**:

Create a [.env](.env) file and set DATABASE_URL to connect with your database.
```
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/db
```

**Database Migrations**:

- Initialize the Alembic environment:

```bash
alembic init alembic
```

- Modify the `alembic.ini` file to specify the correct database URL.

- Generate an initial migration:

```bash
alembic revision --autogenerate -m "initial migration"
```
- Apply the migration to create the database tables:

```bash
alembic upgrade head
```

**Run the Application**:

Start the FastAPI application:

   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

Customize the host and port according to your preferences.

7.**Access the API**:

   The API will be available at `http://localhost:8000/docs`.

## Dependencies

The Jenfi Long Mail Service API relies on several libraries and tools, including:

- Python 3.7+
- FastAPI: A fast web framework for building APIs with Python.
- SQLAlchemy: A SQL toolkit and Object-Relational Mapping (ORM) library.
- PostgreSQL: A powerful open-source relational database system for data storage.
- Alembic: A database migration tool for managing schema changes.
- Pydantic: A powerful tool for schema validation

You must install these dependencies as described in the "Setup Instructions" section.
