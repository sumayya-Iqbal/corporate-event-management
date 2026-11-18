
from app.schemas import EventCreate

# Valid event data
event = EventCreate(
    title="AI Technology Conference",
    description="A conference about Artificial Intelligence",
    event_date="2026-12-20T10:00:00",
    location="Karachi",
    capacity=100
)

print("Event validation successful!")
print(event.model_dump())


# Try invalid capacity
try:
    EventCreate(
        title="AI Conference",
        event_date="2026-12-20T10:00:00",
        location="Karachi",
        capacity=-5
    )
except Exception as error:
    print("\nValidation error detected:")
    print(error)
