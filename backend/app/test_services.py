
# Import the services module from the app package.
# This module contains the business logic for managing events,
# users, registrations, and other application operations.
from app import services


# --------------------------------------------------
# TEST 1: CHECK SERVICES IMPORT
# --------------------------------------------------

# If Python successfully imports services.py,
# this message confirms that the import worked.
print("Services imported successfully!")


# --------------------------------------------------
# TEST 2: CHECK AVAILABLE EVENT FUNCTIONS
# --------------------------------------------------

# Display a heading before listing the functions.
print("\nAvailable functions:")


# Print the create_event function.
# This function handles creating a new event in the database.
print(services.create_event)


# Print the get_events function.
# This function retrieves multiple events from the database.
print(services.get_events)


# Print the get_event function.
# This function retrieves one event using its ID.
print(services.get_event)


# Print the update_event function.
# This function updates an existing event.
print(services.update_event)


# Print the delete_event function.
# This function deletes an existing event.
print(services.delete_event)
