# Country Info App

A comprehensive Django application that provides detailed information about countries using PostgreSQL as the database backend.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+
- PostgreSQL
- Git

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Rafin298/shop_management.git
cd shop_management
```

### 2. Set up a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root directory with the following variables:

```
DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
```

> **Note:** Make sure to replace the placeholders with your actual database credentials.

### 5. Set up the PostgreSQL database

Create a PostgreSQL database using the credentials specified in your `.env` file.

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Create a superuser (optional)

```bash
python manage.py createsuperuser
```

## 🚀 Running the Project

Start the development server:

```bash
python manage.py runserver
```

The application will be available at [http://localhost:8000/](http://localhost:8000/).

## 🌐 Live Demo

The application is available online at: [https://shop-management-ten.vercel.app/](https://shop-management-ten.vercel.app/)

You can register for a new account or use these guest credentials to login:
- Username: guest
- Password: Abcd123#

## 📚 API Documentation

The application includes Swagger documentation for the APIs:

- Local Swagger URL: [https://shop-management-ten.vercel.app/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
- Live Site Swagger URL: [https://shop-management-ten.vercel.app/api/schema/swagger-ui/](https://shop-management-ten.vercel.app/api/schema/swagger-ui/)


## 👨‍💻 Author

[Rafin298](https://github.com/Rafin298)