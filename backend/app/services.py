
# Import select to retrieve records from the database.
# Import func to use SQL functions such as COUNT().
from sqlalchemy import select, func

# AsyncSession allows us to communicate with the database asynchronously.
from sqlalchemy.ext.asyncio import AsyncSession

# HTTPException is used to return API errors.
# status provides standard HTTP status code constants.
from fastapi import HTTPException, status

# Import database models (tables).
# Event represents events, User represents employees/admins,
# and Registration connects users with events.
from app.models import Event, User, Registration

# Import Pydantic schemas used to validate incoming data.
from app.schemas import EventCreate, EventUpdate, UserCreate

# Import password functions.
# We hash passwords before saving them and verify them during login.
from app.security import hash_password, verify_password

# Import delete to delete database records using SQLAlchemy.
from sqlalchemy import delete
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models import Event, User, Registration


# ==================================
# 1. CREATE EVENT
# ==================================

async def create_event(db: AsyncSession, event_data: EventCreate):
    # Convert the validated Pydantic data into a Python dictionary.
    # model_dump() gives us the field names and their values.
    #
    # The ** operator unpacks that dictionary into Event's constructor.
    # This creates a new Event object with the supplied information.
    new_event = Event(**event_data.model_dump())

    # Add the new event to the current database session.
    db.add(new_event)

    # Save the new event permanently in the database.
    await db.commit()

    # Refresh the object to load database-generated values,
    # such as its automatically generated ID.
    await db.refresh(new_event)

    # Return the newly created event to the API route.
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
    # Start building a query that selects all Event records.
    query = select(Event)

    # If the user provides a title, filter events by that title.
    if title:
        # ilike() performs a case-insensitive search.
        # The % symbols allow matching text before or after the search term.
        # Example: searching "tech" can match "Technology Workshop".
        query = query.where(Event.title.ilike(f"%{title}%"))

    # Pagination:
    # offset(skip) skips a number of records.
    # limit(limit) restricts how many records are returned.
    #
    # Example: skip=10 and limit=10 returns the next 10 records.
    query = query.offset(skip).limit(limit)

    # Execute the query asynchronously.
    result = await db.execute(query)

    # scalars() extracts Event objects from the result.
    # all() returns all matching events as a list.
    return result.scalars().all()


# ==================================
# 3. GET EVENT BY ID
# ==================================

async def get_event(db: AsyncSession, event_id: int):
    # Build a query to find an event with the requested ID.
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )

    # Return the matching Event object.
    # If no matching event exists, return None.
    event = result.scalar_one_or_none()

    # Check whether the event exists.
    if event is None:
        # 404 means the requested resource was not found.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    # Return the event if it exists.
    return event


# ==================================
# 4. UPDATE EVENT
# ==================================

async def update_event(
    db: AsyncSession,
    event_id: int,
    event_data: EventUpdate
):
    # First, find the event that needs to be updated.
    # get_event() also raises a 404 error if it does not exist.
    event = await get_event(db, event_id)

    # Convert the supplied update data into a dictionary.
    #
    # exclude_unset=True means only fields actually provided
    # by the client will be included.
    #
    # For example, if the client only sends a new title,
    # the other event fields will not be included.
    update_data = event_data.model_dump(exclude_unset=True)

    # Check every field provided in the update request.
    for field, value in update_data.items():

        # Do not allow a field to be set to None,
        # except description, which is allowed to be None.
        if value is None and field != "description":
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null"
            )

    # Apply the new values to the existing Event object.
    for field, value in update_data.items():

        # setattr() changes an object's attribute dynamically.
        # Example: setattr(event, "title", "New Workshop")
        # is equivalent to event.title = "New Workshop".
        setattr(event, field, value)

    # Save the changes in the database.
    await db.commit()

    # Refresh the object to get its latest database values.
    await db.refresh(event)

    # Return the updated event.
    return event


# ==================================
# 5. DELETE EVENT
# ==================================

async def delete_event(db: AsyncSession, event_id: int):

    # Find the event first.
    # If it does not exist, get_event() raises a 404 error.
    event = await get_event(db, event_id)

    # This check is kept from your original code.
    # In practice, it is redundant because get_event()
    # already raises an exception when the event is missing.
    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    try:
        # First delete all registrations connected to this event.
        #
        # Why?
        # A registration contains an event_id that refers to an event.
        # Removing the event while registrations still exist can cause
        # a foreign-key constraint error, depending on database settings.
        await db.execute(
            delete(Registration).where(
                Registration.event_id == event_id
            )
        )

        # Now delete the event itself.
        await db.delete(event)

        # Save both deletion operations in one database transaction.
        await db.commit()

    except Exception:
        # If something goes wrong, undo uncommitted changes.
        # This prevents a partially completed deletion.
        await db.rollback()

        # Raise the original error again so the API can handle it.
        raise


# ==================================
# 6. CREATE USER
# ==================================

async def create_user(db: AsyncSession, user_data: UserCreate):

    # Search the database to check whether this email is already registered.
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )

    # Get the matching user, or None if no user exists.
    existing_user = result.scalar_one_or_none()

    # Prevent two accounts from using the same email address.
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered"
        )

    # Never save a plain-text password in the database.
    # hash_password() converts it into a secure password hash.
    hashed_password = hash_password(user_data.password)

    # Create a new User database object.
    new_user = User(
        name=user_data.name,
        email=user_data.email,

        # Save the hashed password, not the original password.
        password_hash=hashed_password,

        # Every newly registered user gets the employee role.
        role="employee"
    )

    # Add the new user to the database session.
    db.add(new_user)

    # Save the new user permanently.
    await db.commit()

    # Refresh the object to load its generated database values.
    await db.refresh(new_user)

    # Return the created user.
    return new_user


# ==================================
# 7. USER LOGIN
# ==================================

async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str
):
    # Search for an account with the provided email address.
    result = await db.execute(
        select(User).where(User.email == email)
    )

    # Get the matching user, or None if the email does not exist.
    user = result.scalar_one_or_none()

    # If no account exists, authentication fails.
    if user is None:
        return None

    # Compare the entered password with the stored password hash.
    # verify_password() returns True if the password matches.
    if not verify_password(password, user.password_hash):
        return None

    # Return the user if both email and password are correct.
    # The API route can then create an access token.
    return user


# ==================================
# 8. REGISTER EMPLOYEE FOR EVENT
# ==================================

async def create_registration(
    db: AsyncSession,
    event_id: int,
    user_id: int
):
    # First check whether the requested event exists.
    # A missing event results in a 404 error.
    event = await get_event(db, event_id)

    # Find the employee who wants to register.
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = user_result.scalar_one_or_none()

    # The registration cannot be created for a user who does not exist.
    if user is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Check whether this employee has already registered for this event.
    duplicate_result = await db.execute(
        select(Registration).where(
            Registration.event_id == event_id,
            Registration.user_id == user_id
        )
    )

    # Get the existing registration, or None if there is no match.
    existing_registration = duplicate_result.scalar_one_or_none()

    # Prevent the same employee from registering for the same event twice.
    if existing_registration:
        raise HTTPException(
            status_code=409,
            detail="Employee is already registered for this event"
        )

    # Count how many registrations currently exist for this event.
    count_result = await db.execute(
        select(func.count(Registration.id)).where(
            Registration.event_id == event_id
        )
    )

    # Extract the number from the database result.
    total_registrations = count_result.scalar_one()

    # Compare the current registration count with the event capacity.
    if total_registrations >= event.capacity:
        # 409 means the request conflicts with the current resource state.
        raise HTTPException(
            status_code=409,
            detail="Event capacity is full"
        )

    # Create a new registration connecting this user and event.
    new_registration = Registration(
        user_id=user_id,
        event_id=event_id
    )

    # Add the registration to the database session.
    db.add(new_registration)

    # Save the registration.
    await db.commit()

    # Refresh the object to load its generated ID and other database values.
    await db.refresh(new_registration)

    # Return the newly created registration.
    return new_registration


# ==================================
# 9. GET EVENT REGISTRATIONS
# ==================================

async def get_event_registrations(
    db: AsyncSession,
    event_id: int
):
    # Check that the event exists before retrieving registrations.
    await get_event(db, event_id)

    # Find all registrations belonging to this event.
    result = await db.execute(
        select(Registration).where(
            Registration.event_id == event_id
        )
    )

    # Return all matching registration records as a list.
    return result.scalars().all()


# ==================================
# 10. DELETE REGISTRATION
# ==================================

async def delete_registration(
    db: AsyncSession,
    registration_id: int
):
    # Search for the registration using its ID.
    result = await db.execute(
        select(Registration).where(
            Registration.id == registration_id
        )
    )

    # Get the matching registration, or None if it does not exist.
    registration = result.scalar_one_or_none()

    # Return a 404 error if the registration cannot be found.
    if registration is None:
        raise HTTPException(
            status_code=404,
            detail="Registration not found"
        )

    # Mark the registration for deletion.
    await db.delete(registration)

    # Save the deletion in the database.
    await db.commit()

    # Return None because this operation does not need to return a response body.
    return None
