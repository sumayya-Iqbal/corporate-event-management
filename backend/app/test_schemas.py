
# Import EventCreate from schemas.py.
# EventCreate defines the rules that event data must follow.
from app.schemas import EventCreate


# --------------------------------------------------
# TEST 1: VALID EVENT DATA
# --------------------------------------------------

# Create an event using valid information.
# Pydantic checks each value against the rules in EventCreate.
event = EventCreate(
    title="AI Technology Conference",
    description="A conference about Artificial Intelligence",

    # Pydantic automatically converts this date-time string
    # into a Python datetime object.
    event_date="2026-12-20T10:00:00",

    location="Karachi",
    capacity=100
)

# If the event is created successfully, validation has passed.
print("Event validation successful!")

# model_dump() converts the Pydantic object into a Python dictionary.
# This is useful when we want to inspect or work with the data.
print(event.model_dump())


# --------------------------------------------------
# TEST 2: INVALID EVENT DATA
# --------------------------------------------------

# Use try/except because we expect Pydantic to raise
# a validation error when capacity is negative.
try:
    EventCreate(
        title="AI Conference",
        event_date="2026-12-20T10:00:00",
        location="Karachi",

        # INVALID VALUE:
        # Our EventCreate schema requires capacity to be greater than 0.
        # Therefore, -5 should fail validation.
        capacity=-5
    )

# Pydantic raises an exception when the supplied data
# does not follow the schema rules.
except Exception as error:

    # Display a message explaining that validation failed.
    print("\nValidation error detected:")

    # Display the actual validation error from Pydantic.
    print(error)
