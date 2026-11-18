
# Import datetime because event dates and registration timestamps
# need to contain both date and time information.
from datetime import datetime

# Import Pydantic tools.
from pydantic import BaseModel, ConfigDict, Field, EmailStr


# ==================================
# USER SCHEMAS
# ==================================

# UserCreate defines the data required when someone creates an account.
#
# This schema validates incoming signup data before it reaches
# the database service function.
class UserCreate(BaseModel):

    # User's name must contain at least 2 characters
    # and cannot contain more than 100 characters.
    name: str = Field(min_length=2, max_length=100)

    # EmailStr checks whether the supplied value has a valid email format.
    # Example: user@example.com
    email: EmailStr

    # Password must contain at least 8 characters.
    # The password will later be hashed in services.py before database storage.
    password: str = Field(min_length=8)


# UserResponse defines the information returned to the client
# after retrieving or creating a user.
#
# Notice that password and password_hash are not included.
# This prevents sensitive password information from being returned.
class UserResponse(BaseModel):

    # Unique ID of the user.
    id: int

    # User's name.
    name: str

    # User's email address.
    email: EmailStr

    # User's role, such as employee or admin.
    role: str

    # Allow Pydantic to read values directly from SQLAlchemy objects.
    #
    # Without this configuration, Pydantic normally expects dictionary-like
    # input. With from_attributes=True, it can read object attributes
    # such as user.id, user.name, and user.email.
    model_config = ConfigDict(from_attributes=True)


# ==================================
# AUTHENTICATION SCHEMAS
# ==================================

# LoginRequest defines the data required when a user logs in.
class LoginRequest(BaseModel):

    # The user must provide a valid email format.
    email: EmailStr

    # Password entered by the user.
    # It is checked against the stored password hash during authentication.
    password: str


# TokenResponse defines the structure of the successful login response.
class TokenResponse(BaseModel):

    # JWT access token generated after successful authentication.
    # The client sends this token when accessing protected endpoints.
    access_token: str

    # The token type tells the client how to send the token.
    # "bearer" means the client sends it in the Authorization header.
    # Example: Authorization: Bearer <access_token>
    token_type: str = "bearer"


# ==================================
# EVENT SCHEMAS
# ==================================

# EventCreate defines the information required to create a new event.
class EventCreate(BaseModel):

    # Event title must contain at least 3 characters
    # and cannot exceed 150 characters.
    title: str = Field(min_length=3, max_length=150)

    # Event description is optional.
    # str | None means it can contain text or None.
    # The default value is None when the client does not provide it.
    description: str | None = None

    # Date and time of the event.
    # Pydantic validates and converts compatible date-time input.
    event_date: datetime

    # Event location must contain at least 2 characters
    # and cannot exceed 200 characters.
    location: str = Field(min_length=2, max_length=200)

    # Maximum number of people allowed to register.
    # gt=0 means the capacity must be greater than zero.
    # Therefore, zero and negative values are rejected.
    capacity: int = Field(gt=0)


# EventUpdate defines the fields that can be changed
# when an existing event is updated.
#
# Unlike EventCreate, these fields are optional because
# the client may want to update only one or two fields.
class EventUpdate(BaseModel):

    # Optional updated title.
    # If provided, it must still follow the title validation rules.
    title: str | None = Field(default=None, min_length=3, max_length=150)

    # Optional updated description.
    description: str | None = None

    # Optional new event date and time.
    event_date: datetime | None = None

    # Optional updated location.
    location: str | None = Field(default=None, min_length=2, max_length=200)

    # Optional updated capacity.
    # If provided, it must be greater than zero.
    capacity: int | None = Field(default=None, gt=0)


# EventResponse defines the information returned to the client
# when an event is retrieved, created, or updated.
class EventResponse(BaseModel):

    # Unique ID of the event.
    id: int

    # Event title.
    title: str

    # Event description, which may be None.
    description: str | None

    # Event date and time.
    event_date: datetime

    # Event location.
    location: str

    # Maximum number of registrations allowed.
    capacity: int

    # Date and time when the event record was created.
    created_at: datetime

    # Allow Pydantic to read values from SQLAlchemy Event objects.
    model_config = ConfigDict(from_attributes=True)


# ==================================
# REGISTRATION SCHEMAS
# ==================================

# RegistrationCreate defines the data required to create a registration.
class RegistrationCreate(BaseModel):

    # User ID must be a positive integer.
    # gt=0 rejects zero and negative IDs.
    user_id: int = Field(gt=0)


# RegistrationResponse defines the information returned
# when a registration is retrieved or created.
class RegistrationResponse(BaseModel):

    # Unique ID of the registration record.
    id: int

    # ID of the user who registered.
    user_id: int

    # ID of the event for which the user registered.
    event_id: int

    # Date and time when the registration was created.
    registered_at: datetime

    # Allow Pydantic to read values from SQLAlchemy Registration objects.
    model_config = ConfigDict(from_attributes=True)
