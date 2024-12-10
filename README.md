<h3 align="center">Kalendarz App Backend</h3>

---

<p align="center"> Few lines describing your project.
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Built Using](#built_using)
- [Authors](#authors)

## 🧐 About <a name = "about"></a>

This is a backend project developed as part of a university course to explore and gain hands-on experience with modern backend technologies and practices. The application is built using Python and Django, with PostgreSQL as the database, SQLAlchemy for ORM-like query flexibility, and JWT tokens for secure user authentication and authorization.

The main objectives of this project are:

To deepen understanding of Python and the Django framework for building robust web applications.
To utilize PostgreSQL for efficient and scalable database management.
To implement secure user authentication and authorization using JWT tokens.
To design and build a modular, maintainable backend architecture suitable for real-world applications.
This project serves as both a learning experience and a practical demonstration of combining these technologies to deliver a secure and high-performance backend system.
## 🏁 Getting Started <a name = "getting_started"></a>

These instructions will guide you to set up and run the project locally for development and testing purposes. Refer to the deployment section for instructions on deploying the application to a live system.

### Prerequisites

Ensure you have the following software installed on your system:

Python (>= 3.8)
Install Python from the official Python website.
sudo apt update
sudo apt install python3 python3-pip

PostgreSQL
Download and install PostgreSQL from PostgreSQL Official Website.


Virtual Environment (Optional but Recommended)
Use venv or any virtual environment manager to isolate the project's dependencies.
python3 -m pip install virtualenv


```

### Installing

A step by step series of examples that tell you how to get a development env running.

1. Clone the Repository
Clone the repository to your local machine.
git clone https://github.com/KajetanJedrych/DjangoWSB.git
cd project-name

2. Create and Activate a Virtual Environment
Set up a virtual environment for the project.
python3 -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows

3. Install Dependencies
Install the required Python packages from requirements.txt.
pip install -r requirements.txt

4. Configure Environment Variables
Create a .env file in the project's root directory and add the following:
Copy code
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=127.0.0.1
DB_PORT=5432
Replace your-* placeholders with your specific configurations.

5. Set Up the Database
Apply database migrations to initialize the database schema.
python manage.py makemigrations
python manage.py migrate

6. Run the Development Server
Start the Django development server.
python manage.py runserver

```

## 🎈 Usage <a name="usage"></a>

Use an API client like Postman or cURL to register a user by sending a POST request to /api/auth/register/ with appropriate payload.

Example:

POST http://127.0.0.1:8000/api/auth/register/
{
    "username": "testuser",
    "password": "securepassword"
}
Log In to Receive JWT Token:
Authenticate and retrieve a JWT token to access secure endpoints.

Example:

POST http://127.0.0.1:8000/api/auth/login/
{
    "username": "testuser",
    "password": "securepassword"
}
Response:
{
    "access": "your-access-token",
    "refresh": "your-refresh-token"
}

http://127.0.0.1:8000/api/calendar/appointments/
{
  "service": 1,
  "employee": 1,
  "date": "2024-11-20",
  "time": "10:00"
}

## ⛏️ Built Using <a name = "built_using"></a>

- PostgreSQL - Database
- Django - Web Framework
- Django REST Framework - REST API Framework
- Simple JWT - JWT Authentication

## ✍️ Authors <a name = "authors"></a>

- [@KajetanJedrych](https://github.com/KajetanJedrych) - Idea & Initial work



