
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models import Event, User, Registration
from app.schemas import EventCreate, EventUpdate, UserCreate
from app.security import hash_password, verify_password

from sqlalchemy import delete
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models import Event, User, Registration
# ==================================
# 1. CREATE EVENT
# ==================================

async def create_event(db: AsyncSession, event_data: EventCreate):
    new_event = Event(**event_data.model_dump())

    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)

    return new_event


# ==================================
# 2. GET ALL EVENTS
# ==================================

async def get_events(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    title: str | None = None
):
    query = select(Event)

    if title:
        query = query.where(Event.title.ilike(f"%{title}%"))

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)

    return result.scalars().all()


# ==================================
# 3. GET EVENT BY ID
# ==================================

async def get_event(db: AsyncSession, event_id: int):
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )

    event = result.scalar_one_or_none()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return event


# ==================================
# 4. UPDATE EVENT
# ==================================

async def update_event(
    db: AsyncSession,
    event_id: int,
    event_data: EventUpdate
):
    event = await get_event(db, event_id)

    update_data = event_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if value is None and field != "description":
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null"
            )

    for field, value in update_data.items():
        setattr(event, field, value)

    await db.commit()
    await db.refresh(event)

    return event


# ==================================
# 5. DELETE EVENT
# ==================================



async def delete_event(db: AsyncSession, event_id: int):
    event = await get_event(db, event_id)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    try:
        # First delete registrations linked to this event.
        await db.execute(
            delete(Registration).where(
                Registration.event_id == event_id
            )
        )

        # Then delete the event itself.
        await db.delete(event)

        await db.commit()

    except Exception:
        await db.rollback()
        raise



# ==================================
# 6. CREATE USER
# ==================================

async def create_user(db: AsyncSession, user_data: UserCreate):
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered"
        )

    hashed_password = hash_password(user_data.password)

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        role="employee"
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


# ==================================
# 7. USER LOGIN
# ==================================

async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str
):
    result = await db.execute(
        select(User).where(User.email == email)
    )

    user = result.scalar_one_or_none()

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


# ==================================
# 8. REGISTER EMPLOYEE FOR EVENT
# ==================================

async def create_registration(
    db: AsyncSession,
    event_id: int,
    user_id: int
):
    event = await get_event(db, event_id)

    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    duplicate_result = await db.execute(
        select(Registration).where(
            Registration.event_id == event_id,
            Registration.user_id == user_id
        )
    )

    existing_registration = duplicate_result.scalar_one_or_none()

    if existing_registration:
        raise HTTPException(
            status_code=409,
            detail="Employee is already registered for this event"
        )

    count_result = await db.execute(
        select(func.count(Registration.id)).where(
            Registration.event_id == event_id
        )
    )

    total_registrations = count_result.scalar_one()

    if total_registrations >= event.capacity:
        raise HTTPException(
            status_code=409,
            detail="Event capacity is full"
        )

    new_registration = Registration(
        user_id=user_id,
        event_id=event_id
    )

    db.add(new_registration)
    await db.commit()
    await db.refresh(new_registration)

    return new_registration


# ==================================
# 9. GET EVENT REGISTRATIONS
# ==================================

async def get_event_registrations(
    db: AsyncSession,
    event_id: int
):
    await get_event(db, event_id)

    result = await db.execute(
        select(Registration).where(
            Registration.event_id == event_id
        )
    )

    return result.scalars().all()


# ==================================
# 10. DELETE REGISTRATION
# ==================================

async def delete_registration(
    db: AsyncSession,
    registration_id: int
):
    result = await db.execute(
        select(Registration).where(
            Registration.id == registration_id
        )
    )

    registration = result.scalar_one_or_none()

    if registration is None:
        raise HTTPException(
            status_code=404,
            detail="Registration not found"
        )

    await db.delete(registration)
    await db.commit()

    return None
