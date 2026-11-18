
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Response,
    Query
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db import get_db
from app import services
from app.models import User
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
from app.security import (
    create_access_token,
    get_current_user,
    require_admin
)


# ==================================
# CREATE FASTAPI APPLICATION
# ==================================

app = FastAPI(
    title="Corporate Event Management API",
    description="Backend API for managing corporate events",
    version="1.0.0"
)


# ==================================
# CORS CONFIGURATION
# ==================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ==================================
# HOME AND HEALTH ROUTES
# ==================================

@app.get("/")
async def home():
    return {
        "message": "Welcome to Corporate Event Management API"
    }


@app.get("/health")
async def health():
    return {
        "status": "Backend is running"
    }


@app.get("/health/db")
async def database_health(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(text("SELECT 1"))

    return {
        "status": "Database connection successful",
        "result": result.scalar()
    }


# ==================================
# USER ROUTES
# ==================================

# 1. CREATE USER
@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await services.create_user(db, user_data)


# 2. USER LOGIN
@app.post(
    "/login",
    response_model=TokenResponse
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await services.authenticate_user(
        db,
        login_data.email,
        login_data.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        user_id=user.id,
        role=user.role
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# 3. GET CURRENT LOGGED-IN USER
@app.get(
    "/users/me",
    response_model=UserResponse
)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


# ==================================
# EVENT ROUTES
# ==================================

# 1. CREATE EVENT (ADMIN ONLY)
@app.post(
    "/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_event(
    event_data: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return await services.create_event(db, event_data)


# 2. GET ALL EVENTS (PUBLIC)
@app.get(
    "/events",
    response_model=list[EventResponse]
)
async def get_events(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    title: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    return await services.get_events(
        db=db,
        skip=skip,
        limit=limit,
        title=title
    )


# 3. GET ONE EVENT (PUBLIC)
@app.get(
    "/events/{event_id}",
    response_model=EventResponse
)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await services.get_event(db, event_id)


# 4. UPDATE EVENT (ADMIN ONLY)
@app.put(
    "/events/{event_id}",
    response_model=EventResponse
)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return await services.update_event(
        db,
        event_id,
        event_data
    )


# 5. DELETE EVENT (ADMIN ONLY)
@app.delete(
    "/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    await services.delete_event(
        db,
        event_id
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


# ==================================
# REGISTRATION ROUTES
# ==================================

# 1. REGISTER EMPLOYEE FOR AN EVENT
@app.post(
    "/events/{event_id}/registrations",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_employee(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await services.create_registration(
        db,
        event_id,
        current_user.id
    )


# 2. GET ALL REGISTRATIONS FOR AN EVENT
@app.get(
    "/events/{event_id}/registrations",
    response_model=list[RegistrationResponse]
)
async def get_registrations(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await services.get_event_registrations(
        db,
        event_id
    )


# 3. CANCEL REGISTRATION
@app.delete(
    "/registrations/{registration_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def cancel_registration(
    registration_id: int,
    db: AsyncSession = Depends(get_db)
):
    await services.delete_registration(
        db,
        registration_id
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
