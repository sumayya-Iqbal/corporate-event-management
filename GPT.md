# AI Assistance and Development Transparency

## 1. Purpose of This Document

This document explains how AI assistance was used during the development of the Acme Corp Corporate Event Management System.

The purpose is to maintain transparency about AI involvement, distinguish AI-assisted work from personal learning and implementation, and help instructors and reviewers understand the development process.

AI was used as a learning and development assistant, not as a replacement for understanding, reviewing, or testing the application.

## 2. AI Tool Used

**Tool:** ChatGPT

ChatGPT was used to support the development process through explanations, examples, coding guidance, debugging assistance, and documentation preparation.

## 3. Why AI Assistance Was Used

Before starting this assignment, my backend development experience was limited. I understood basic programming concepts but had not completed a full backend project involving authentication, a relational database, API development, and frontend integration.

I used AI assistance to understand unfamiliar technologies and follow a structured development process.

My main learning objectives were:

- Understand how a backend application works.
- Learn how frontend and backend communicate.
- Understand REST API design.
- Learn database integration.
- Understand authentication and authorization.
- Learn how to identify and fix errors.
- Complete a working project while improving my development skills.

## 4. Areas Where AI Assistance Was Used

### A. Project Planning and Architecture

AI assistance was used to:

- Break the assignment into smaller development tasks.
- Understand the purpose of the backend, frontend, and database.
- Plan the application folder structure.
- Understand how FastAPI, React, PostgreSQL, and SQLAlchemy work together.
- Identify the responsibilities of different application files.

### B. Backend Development

AI assistance supported the development and explanation of:

- FastAPI application structure.
- API routes and HTTP methods.
- SQLAlchemy database models.
- Pydantic request and response schemas.
- Database connection configuration.
- Service-layer logic.
- Asynchronous database operations.
- Error handling and HTTP status codes.

### C. Authentication and Authorization

AI assistance was used to understand and implement concepts related to:

- Password hashing.
- User registration and login.
- JWT access tokens.
- Protected API endpoints.
- Current-user authentication.
- Administrator and employee roles.
- Permission checks.

### D. Database Integration

AI assistance helped explain:

- PostgreSQL database connections.
- Neon hosted PostgreSQL.
- SQLAlchemy ORM.
- Relationships between users, events, and registrations.
- Unique constraints.
- Database table creation.
- Database connection errors.

### E. Frontend Development

AI assistance supported:

- React component structure.
- Connecting the frontend to the FastAPI backend.
- Sending HTTP requests.
- Login and authentication-token handling.
- Displaying event data.
- Creating and deleting events.
- Employee event registration.
- UI layout and CSS improvements.

### F. Debugging and Error Resolution

AI assistance was used to investigate and resolve development issues, including:

- API request failures.
- Authentication errors.
- Authorization errors.
- Database-related errors.
- Duplicate registration conflicts.
- Event capacity validation.
- Frontend-to-backend communication issues.
- Event deletion problems.

### G. Documentation

AI assistance helped prepare:

- Project README documentation.
- Installation instructions.
- API endpoint descriptions.
- Technology-stack explanations.
- This AI assistance disclosure document.

## 5. How AI Assistance Was Used

The development process followed an iterative learning approach:

1. Understand the assignment requirements.
2. Break the work into smaller tasks.
3. Learn the purpose of the technology or code being used.
4. Implement the suggested solution in the project.
5. Run the application.
6. Check the result through Swagger or the frontend.
7. Share errors when something did not work.
8. Review explanations and apply corrections.
9. Continue to the next development task.

The goal was to understand the implementation rather than simply copy code without explanation.

## 6. What I Personally Worked On

As the learner and developer, I:

- Followed the assignment requirements.
- Set up the local project environment.
- Created and organized the project structure.
- Configured the database connection.
- Worked through backend and frontend implementation steps.
- Ran the application locally.
- Used Swagger to check API behavior.
- Checked authentication and authorization behavior.
- Tested important registration and event-management scenarios manually.
- Investigated errors and applied fixes with guidance.
- Prepared the project for Git and GitHub.
- Reviewed the application and its functionality.

These activities reflect my practical involvement in the development process. AI assistance was used throughout, so this project should be described as AI-assisted development rather than entirely independent coding.

## 7. Manual Verification

During development, the following behaviors were manually checked:

| Area | Verification |
|---|---|
| Database | Database connection tested |
| API | Swagger documentation accessed |
| User registration | Registration endpoint checked |
| Login | Login and token generation checked |
| Authentication | Protected endpoint checked with and without a token |
| Authorization | Employee restriction on admin event operations checked |
| Event management | Event creation and deletion checked |
| Registration | Successful event registration checked |
| Duplicate registration | Conflict response checked |
| Capacity | Full-event registration rejection checked |
| Validation | Invalid input response checked |
| Missing event | Not-found response checked |
| Frontend | Login, event listing, and event actions checked |

These are manual development checks, not a claim that every possible scenario has been covered by automated tests.

The automated Pytest suite should be run separately, and its actual result should be reported honestly.

## 8. Limitations and Areas Requiring Further Improvement

The project is a learning-stage application and is not yet a fully production-hardened enterprise system.

Areas that require further review and improvement include:

- Stronger ownership and authorization checks for registration deletion.
- More comprehensive automated tests.
- Production-grade error handling and logging.
- Secure production deployment configuration.
- Database migration management.
- Additional security review.
- More complete frontend validation and user feedback.
- Improved handling of concurrent registration requests.

These limitations are acknowledged as opportunities for further learning and development.

## 9. Responsible Use of AI

I understand that AI-generated code can contain errors, security weaknesses, or incorrect assumptions.

For this reason:

- AI suggestions should be reviewed before use.
- Sensitive credentials must not be included in public repositories.
- Important functionality should be tested.
- Security-related code requires additional attention.
- AI assistance should not be presented as independent work.
- Technical concepts should be understood well enough to explain and maintain the application.

## 10. Learning Reflection

This assignment helped me understand how different parts of a full-stack application work together.

I gained practical exposure to FastAPI, PostgreSQL, SQLAlchemy, Pydantic, JWT authentication, React, and GitHub.

One of the most valuable parts of this project was learning how to troubleshoot errors and understand the relationship between API routes, database operations, authentication, and frontend requests.

I still have more to learn, particularly about advanced backend architecture, automated testing, application security, and production deployment.

**Final Disclosure:** ChatGPT was used as a development and learning assistant for planning, code guidance, explanations, debugging, UI assistance, and documentation. The project was implemented and manually checked through an iterative process with AI assistance. This document is intended to provide an honest account of that assistance.
