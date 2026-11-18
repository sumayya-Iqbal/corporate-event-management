
# ============================================================
# IMPORTS
# ============================================================

# FastAPI is the framework used to build our REST API.
# Depends is used for dependency injection, such as getting a database session.
# HTTPException allows us to return HTTP errors.
# status provides readable HTTP status-code constants.
# Response allows us to customize the HTTP response.
# Query is used to validate query parameters such as skip and limit.
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Response,
    Query
)

# CORS middleware allows our frontend (React) to communicate
# with our backend even when they run on different origins.
from fastapi.middleware.cors import CORSMiddleware

# AsyncSession represents an asynchronous SQLAlchemy database session.
from sqlalchemy.ext.asyncio import AsyncSession

# SQLAlchemy text() allows us to execute raw SQL statements.
from sqlalchemy import text

# Import the function that provides a database session.
from app.db import get_db

# Import the service layer.
# Services contain the actual business logic and database operations.
from app import services

# Import the User database model.
# We use it for type hints and authenticated-user information.
from app.models import User

# Import Pydantic schemas.
# Schemas validate incoming data and control the structure of API responses.
from app.schemas import (
    EventCreate,
    EventUpdate,
    EventResponse,
    UserCreate,
    UserResponse,
    RegistrationResponse,
    LoginRequest,
    TokenResponse
)

# Import authentication and authorization functions.
from app.security import (
    create_access_token,
    get_current_user,
    require_admin
)


# ============================================================
# 1. CREATE FASTAPI APPLICATION
# ============================================================

# FastAPI() creates the main application instance.
# All API endpoints will be registered using this app object.
app = FastAPI(
    title="Corporate Event Management API",
    description="Backend API for managing corporate events",
    version="1.0.0"
)

# These settings appear in the automatically generated API documentation.
# Open http://127.0.0.1:8000/docs to explore and test the endpoints.


# ============================================================
# 2. CORS CONFIGURATION
# ============================================================

# CORS stands for Cross-Origin Resource Sharing.
#
# Browsers restrict requests between different origins by default.
# For example:
# React frontend: http://localhost:5173
# FastAPI backend: http://127.0.0.1:8000
#
# They have different origins, so we allow the frontend to communicate
# with our backend through this middleware.
app.add_middleware(
    CORSMiddleware,

    # Only the frontend origin listed here is allowed to access the API
    # through a browser.
    allow_origins=["http://localhost:5173"],

    # Allow cookies and authentication-related credentials if needed.
    allow_credentials=True,

    # Allow all HTTP methods: GET, POST, PUT, DELETE, etc.
    allow_methods=["*"],

    # Allow all request headers, including Authorization.
    allow_headers=["*"]
)

# DEPLOYMENT NOTE:
# When the frontend is deployed on Vercel, add its actual HTTPS domain
# to allow_origins. Otherwise, the browser may block frontend requests.


# ============================================================
# 3. HOME AND HEALTH ROUTES
# ============================================================

# GET /
# This is the root endpoint.
# It returns a welcome message when someone opens the backend URL.
@app.get("/")
async def home():
    return {
        "message": "Welcome to Corporate Event Management API"
    }


# GET /health
# This endpoint checks whether the FastAPI application is running.
# It does not check the database connection.
@app.get("/health")
async def health():
    return {
        "status": "Backend is running"
    }


# GET /health/db
# This endpoint checks whether the backend can communicate with PostgreSQL.
@app.get("/health/db")
async def database_health(
    # Depends(get_db) asks FastAPI to provide a database session.
    # The session is automatically managed by the get_db dependency.
    db: AsyncSession = Depends(get_db)
):
    # Execute a simple SQL query.
    # SELECT 1 is commonly used to test whether a database connection works.
    #
    # await is used because database execution is asynchronous.
    result = await db.execute(text("SELECT 1"))

    # scalar() extracts the first value from the query result.
    # For SELECT 1, the returned value is 1.
    return {
        "status": "Database connection successful",
        "result": result.scalar()
    }


# ============================================================
# 4. USER ROUTES
# ============================================================

# ------------------------------------------------------------
# 4.1 CREATE USER / SIGN UP
# ------------------------------------------------------------

# POST /users
# Creates a new user account.
#
# response_model:
# Defines the structure of the successful response.
#
# status_code=201:
# HTTP 201 means that a new resource was created successfully.
@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    # FastAPI receives the request body and validates it using UserCreate.
    # For example, it checks required fields and valid email format.
    user_data: UserCreate,

    # Provides the database session for this request.
    db: AsyncSession = Depends(get_db)
):
    # Send the validated user data to the service layer.
    #
    # The service handles business logic such as checking duplicate emails,
    # hashing the password, and saving the user.
    return await services.create_user(db, user_data)


# ------------------------------------------------------------
# 4.2 USER LOGIN
# ------------------------------------------------------------

# POST /login
# Authenticates a user using their email and password.
# If credentials are correct, the API returns a JWT access token.
@app.post(
    "/login",
    response_model=TokenResponse
)
async def login(
    # LoginRequest validates the incoming email and password.
    login_data: LoginRequest,

    # Database session used to find and authenticate the user.
    db: AsyncSession = Depends(get_db)
):
    # Ask the service layer to verify the user's credentials.
    #
    # It checks whether the user exists and whether the password is correct.
    user = await services.authenticate_user(
        db,
        login_data.email,
        login_data.password
    )

    # If authentication fails, the service returns None.
    if user is None:

        # HTTP 401 means the user is not authenticated.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,

            # Do not reveal whether the email or password was incorrect.
            detail="Incorrect email or password",

            # Tells the client that Bearer token authentication is expected.
            headers={"WWW-Authenticate": "Bearer"}
        )

    # If credentials are correct, generate a JWT access token.
    #
    # The token contains the user's ID and role.
    # The security module handles token creation and signing.
    access_token = create_access_token(
        user_id=user.id,
        role=user.role
    )

    # Return the token to the frontend.
    # The frontend can send it in future requests using:
    # Authorization: Bearer <access_token>
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ------------------------------------------------------------
# 4.3 GET CURRENT LOGGED-IN USER
# ------------------------------------------------------------

# GET /users/me
# Returns the profile of the currently authenticated user.
@app.get(
    "/users/me",
    response_model=UserResponse
)
async def get_my_profile(
    # get_current_user verifies the JWT token and retrieves the user.
    #
    # If the token is missing, invalid, or expired,
    # the authentication dependency rejects the request.
    current_user: User = Depends(get_current_user)
):
    # Return the authenticated user's information.
    return current_user


# ============================================================
# 5. EVENT ROUTES
# ============================================================

# ------------------------------------------------------------
# 5.1 CREATE EVENT (ADMIN ONLY)
# ------------------------------------------------------------

# POST /events
# Allows administrators to create a new corporate event.
@app.post(
    "/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_event(
    # Incoming event information is validated using EventCreate.
    event_data: EventCreate,

    # Database session used to save the event.
    db: AsyncSession = Depends(get_db),

    # require_admin verifies that the requester is authenticated
    # and has the administrator role.
    #
    # If the requester is not an admin, the request is rejected.
    current_user: User = Depends(require_admin)
):
    # Send the event data to the service layer.
    # The service performs the database operation.
    return await services.create_event(db, event_data)


# ------------------------------------------------------------
# 5.2 GET ALL EVENTS (PUBLIC)
# ------------------------------------------------------------

# GET /events
# Returns a list of events.
# Authentication is not required for this endpoint.
@app.get(
    "/events",
    response_model=list[EventResponse]
)
async def get_events(
    # skip controls how many records are skipped.
    # Example: skip=10 means start after the first 10 records.
    #
    # ge=0 means the value cannot be negative.
    skip: int = Query(default=0, ge=0),

    # limit controls the maximum number of records returned.
    # Default is 10 and the maximum allowed value is 100.
    limit: int = Query(default=10, ge=1, le=100),

    # Optional title filter.
    # str | None means the value can be a string or None.
    # If no title is provided, all matching events are returned.
    title: str | None = None,

    # Database session used to retrieve event records.
    db: AsyncSession = Depends(get_db)
):
    # Call the service layer and pass the filtering and pagination values.
    return await services.get_events(
        db=db,
        skip=skip,
        limit=limit,
        title=title
    )


# ------------------------------------------------------------
# 5.3 GET ONE EVENT (PUBLIC)
# ------------------------------------------------------------

# GET /events/{event_id}
# Returns details about one event.
#
# Example:
# GET /events/5
# This requests the event whose ID is 5.
@app.get(
    "/events/{event_id}",
    response_model=EventResponse
)
async def get_event(
    # FastAPI extracts event_id from the URL path.
    event_id: int,

    # Database session used to retrieve the event.
    db: AsyncSession = Depends(get_db)
):
    # Ask the service layer to find the event.
    # If it does not exist, the service handles the error.
    return await services.get_event(db, event_id)


# ------------------------------------------------------------
# 5.4 UPDATE EVENT (ADMIN ONLY)
# ------------------------------------------------------------

# PUT /events/{event_id}
# Allows administrators to update an existing event.
@app.put(
    "/events/{event_id}",
    response_model=EventResponse
)
async def update_event(
    # ID of the event that needs to be updated.
    event_id: int,

    # Contains the new event information.
    # EventUpdate validates the incoming data.
    event_data: EventUpdate,

    # Database session for the update operation.
    db: AsyncSession = Depends(get_db),

    # Only an authenticated administrator can update events.
    current_user: User = Depends(require_admin)
):
    # Pass the event ID and updated information to the service layer.
    return await services.update_event(
        db,
        event_id,
        event_data
    )


# ------------------------------------------------------------
# 5.5 DELETE EVENT (ADMIN ONLY)
# ------------------------------------------------------------

# DELETE /events/{event_id}
# Allows administrators to delete an event.
@app.delete(
    "/events/{event_id}",

    # HTTP 204 means the deletion was successful.
    # It does not return a response body.
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_event(
    # ID of the event to delete.
    event_id: int,

    # Database session used for the deletion.
    db: AsyncSession = Depends(get_db),

    # Verify that the requester has administrator permissions.
    current_user: User = Depends(require_admin)
):
    # Ask the service layer to delete the event.
    # Database-related deletion logic is handled there.
    await services.delete_event(
        db,
        event_id
    )

    # Return an empty HTTP 204 response.
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


# ============================================================
# 6. REGISTRATION ROUTES
# ============================================================

# ------------------------------------------------------------
# 6.1 REGISTER EMPLOYEE FOR AN EVENT
# ------------------------------------------------------------

# POST /events/{event_id}/registrations
# Allows an authenticated employee to register for an event.
@app.post(
    "/events/{event_id}/registrations",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_employee(
    # ID of the event the employee wants to join.
    event_id: int,

    # Database session used for the registration operation.
    db: AsyncSession = Depends(get_db),

    # get_current_user verifies the JWT and retrieves the logged-in user.
    # An unauthenticated user cannot register.
    current_user: User = Depends(get_current_user)
):
    # Create a registration using:
    # 1. The database session.
    # 2. The requested event ID.
    # 3. The authenticated user's ID.
    #
    # We use current_user.id instead of accepting a user ID from the client.
    # This prevents a user from simply submitting another person's ID.
    return await services.create_registration(
        db,
        event_id,
        current_user.id
    )


# ------------------------------------------------------------
# 6.2 GET ALL REGISTRATIONS FOR AN EVENT
# ------------------------------------------------------------

# GET /events/{event_id}/registrations
# Returns the registrations associated with an event.
@app.get(
    "/events/{event_id}/registrations",
    response_model=list[RegistrationResponse]
)
async def get_registrations(
    # ID of the event whose registrations we want to retrieve.
    event_id: int,

    # Database session used to query registrations.
    db: AsyncSession = Depends(get_db)
):
    # Retrieve the event's registrations through the service layer.
    return await services.get_event_registrations(
        db,
        event_id
    )


# ------------------------------------------------------------
# 6.3 CANCEL REGISTRATION
# ------------------------------------------------------------

# DELETE /registrations/{registration_id}
# Deletes a registration record.
@app.delete(
    "/registrations/{registration_id}",

    # HTTP 204 indicates successful deletion with no response body.
    status_code=status.HTTP_204_NO_CONTENT
)
async def cancel_registration(
    # ID of the registration that should be deleted.
    registration_id: int,

    # Database session used for deletion.
    db: AsyncSession = Depends(get_db)
):
    # Ask the service layer to delete the registration.
    await services.delete_registration(
        db,
        registration_id
    )

    # Return an empty 204 response.
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
