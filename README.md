# Acme Corp – Corporate Event Management System

A full-stack Corporate Event Management System developed as a backend development project. It allows employees to view corporate events and register for them, while administrators can create, manage, and delete events.

The application uses **FastAPI** for the backend, **PostgreSQL (Neon)** for data storage, and **React** for the frontend.

## 1. Project Overview

Organizations arrange different types of corporate activities, including:

- Product launches
- Technical workshops and training sessions
- Team-building activities
- Corporate events and conferences

Managing these events manually can lead to duplicate registrations, capacity problems, and difficulty tracking participants.

This project provides a centralized system to manage events and employee registrations, with role-based access control.

## 2. Main Objectives

- Build a RESTful API using FastAPI.
- Store application data in a PostgreSQL database.
- Implement asynchronous database operations using SQLAlchemy.
- Validate incoming data using Pydantic.
- Implement JWT-based authentication.
- Provide separate permissions for administrators and employees.
- Prevent duplicate registrations and registrations beyond event capacity.
- Build a React frontend to interact with the API.

## 3. Features

### Authentication and Authorization

- User registration.
- User login.
- Password hashing.
- JWT access-token authentication.
- Protected user profile endpoint.
- Role-based permissions for admin and employee accounts.

### Event Management

Administrators can:

- Create events.
- View all events.
- View individual event details.
- Update events.
- Delete events.

Employees and other visitors can view available events.

### Event Registration

Authenticated employees can:

- Register for an event.
- View event registrations.

The system checks:

- Whether the requested event exists.
- Whether the employee has already registered.
- Whether the event has reached its maximum capacity.

Duplicate registrations and full-capacity registrations are rejected.

### Frontend

The React application provides:

- Login interface.
- Dashboard.
- Event listing.
- Event search.
- Event creation for administrators.
- Event deletion for administrators.
- Event registration for employees.

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| PostgreSQL | Relational database |
| Neon | Hosted PostgreSQL database |
| SQLAlchemy 2.0 | Database ORM and async operations |
| Pydantic | Request and response validation |
| PyJWT | JWT authentication |
| Argon2 | Password hashing |
| React | Frontend interface |
| Vite | Frontend development server |
| JavaScript | Frontend functionality |
| CSS | Frontend styling |
| Git and GitHub | Version control and source-code hosting |
| Pytest | Backend testing framework |

## 5. Project Structure

```text
corporate-event-management/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── services.py
│   │   ├── security.py
│   │   ├── create_tables.py
│   │   ├── test_db.py
│   │   ├── test_schemas.py
│   │   └── test_services.py
│   │
│   ├── requirements.txt
│   └── .env                 # Local only; not committed
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
├── README.md
└── GPT.md
```

## 6. Database Design

The application uses three main entities:

### User

Stores user account information, including:

- ID
- Name
- Email
- Hashed password
- Role (`admin` or `employee`)

### Event

Stores corporate event information, including:

- ID
- Title
- Description
- Location
- Event date
- Maximum capacity

### Registration

Connects users with events and records their registrations.

The database uses a unique constraint on the user and event combination to prevent the same user from registering for the same event more than once.

## 7. API Endpoints

The backend exposes the following main endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Root endpoint |
| GET | `/health` | Application health check |
| GET | `/health/db` | Database health check |
| POST | `/users` | Register a new user |
| POST | `/login` | Authenticate a user |
| GET | `/users/me` | Get current authenticated user |
| POST | `/events` | Create an event (admin) |
| GET | `/events` | List events |
| GET | `/events/{event_id}` | Get event details |
| PUT | `/events/{event_id}` | Update an event (admin) |
| DELETE | `/events/{event_id}` | Delete an event (admin) |
| POST | `/events/{event_id}/registrations` | Register for an event |
| GET | `/events/{event_id}/registrations` | View event registrations |
| DELETE | `/registrations/{registration_id}` | Delete a registration |

### Important HTTP Status Codes

| Status | Meaning |
|---|---|
| 200 | Request successful |
| 201 | Resource created |
| 204 | Resource deleted successfully |
| 401 | Authentication required or invalid |
| 403 | User does not have permission |
| 404 | Requested resource not found |
| 409 | Conflict, such as duplicate registration or full event |
| 422 | Input validation error |

## 8. Installation and Setup

### Prerequisites

Install the following:

- Python
- Node.js and npm
- Git
- A PostgreSQL database (Neon can be used)

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd corporate-event-management
```

Replace the placeholder with the actual GitHub repository URL.

### Step 2: Set Up the Backend

```bash
cd backend
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file inside the `backend` folder.

Add the database connection string and secret-key settings required by `app/config.py`.

Example values (use the exact variable names expected by your configuration):

```env
DATABASE_URL=your_postgresql_connection_string
SECRET_KEY=your_long_random_secret
```

Do not publish real database credentials or secret keys to GitHub.

### Step 4: Prepare the Database

Configure your Neon PostgreSQL connection and create the required database tables using the project's table-creation script.

From the `backend` folder, run:

```bash
python -m app.create_tables
```

### Step 5: Start the Backend

From the `backend` folder:

```bash
python -m uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Step 6: Start the Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local frontend URL shown by Vite, normally:

```text
http://localhost:5173
```

The backend must be running for frontend API requests to work.

## 9. Authentication and Roles

### Employee

- Can log in.
- Can view events.
- Can register for events.
- Cannot create, update, or delete events.

### Administrator

- Can log in.
- Can view events.
- Can create events.
- Can update events.
- Can delete events.

New public sign-ups receive the employee role by default. Administrator access should be assigned securely by an authorized database administrator.

## 10. Testing

The project includes test modules for database, schema, and service-level testing.

To run the test suite from the backend directory:

```bash
pytest
```

The tests should be executed in an environment with the required dependencies and database configuration.

Manual API checks can also be performed through Swagger at `/docs`.

Examples of important scenarios to verify:

- Successful user registration and login.
- Access to protected endpoints with and without a valid token.
- Administrator-only event operations.
- Successful event registration.
- Duplicate registration rejection.
- Event capacity enforcement.
- Missing event handling.
- Invalid request validation.

**Testing note:** Only report tests as passed after running them and checking their actual results.

## 11. Security and Configuration

- Passwords are stored as hashes rather than plain text.
- JWT tokens are used for authenticated requests.
- Administrator operations require the appropriate role.
- Database credentials and secret keys are kept in environment variables.
- `.gitignore` excludes sensitive and generated files.

## 12. Current Scope and Future Improvements

Possible improvements include:

- Stronger registration ownership checks.
- Administrator management through a dedicated interface.
- Registration cancellation and history.
- Automated integration tests.
- Database migrations using Alembic.
- Improved deployment and production configuration.
- Email notifications for event registration.
- Better reporting and event analytics.

## 13. Learning Outcomes

This project provides practical experience with:

- REST API architecture.
- Backend development using FastAPI.
- Relational database design.
- SQLAlchemy and asynchronous database operations.
- Authentication and authorization.
- Data validation and error handling.
- React frontend integration.
- Git and GitHub workflows.
- Debugging and testing a full-stack application.

## 14. Project Transparency

This project was developed as a learning assignment. AI tools were used as learning and development assistance. The development process included understanding the code, implementing features, debugging issues, and manually checking API and frontend behavior.

More details about AI assistance and the development process are documented in `GPT.md`.

---

**Project:** Acme Corp – Corporate Event Management System  
**Project Type:** Full-Stack Web Application / REST API  
**Backend:** FastAPI  
**Frontend:** React  
**Database:** PostgreSQL (Neon)
