
// Import React hooks.
// useState stores information that can change while the application runs.
// useEffect runs code when the component is loaded or when dependencies change.
import { useEffect, useState } from "react";

// Import the CSS file that contains the styling of this application.
import "./App.css";

// Backend API address.
// React sends HTTP requests to this FastAPI backend.
const API_URL = "http://127.0.0.1:8000";


// =====================================================
// MAIN APP COMPONENT
// =====================================================

function App() {

  // ---------------------------------------------------
  // 1. REACT STATE (APPLICATION DATA)
  // ---------------------------------------------------

  // Get the saved JWT token from browser localStorage.
  // If no token exists, use an empty string.
  // useState keeps the token available while the app is running.
  const [token, setToken] = useState(localStorage.getItem("token") || "");

  // Stores the currently logged-in user's information.
  // Initially null because no user profile has been loaded yet.
  const [user, setUser] = useState(null);

  // Stores all events received from the backend API.
  const [events, setEvents] = useState([]);

  // Stores email and password entered in the login form.
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // loading controls the login button while login is processing.
  const [loading, setLoading] = useState(false);

  // saving controls the create-event button while an event is being saved.
  const [saving, setSaving] = useState(false);

  // Stores successful messages shown to the user.
  const [message, setMessage] = useState("");

  // Stores error messages returned by the backend or frontend.
  const [error, setError] = useState("");

  // Stores the text entered in the event search field.
  const [search, setSearch] = useState("");

  // Controls which dashboard page is currently visible.
  // Possible values: dashboard, events, create.
  const [activePage, setActivePage] = useState("dashboard");


  // Stores the values entered in the Create Event form.
  // These are the default values shown when the form is opened.
  const [newEvent, setNewEvent] = useState({
    title: "",
    description: "",
    event_date: "",
    location: "",
    capacity: 20,
  });


  // ---------------------------------------------------
  // 2. COMMON API HEADERS
  // ---------------------------------------------------

  // Creates HTTP headers for API requests.
  // The Authorization header sends the JWT token to the backend.
  // The backend uses this token to identify the logged-in user.
  //
  // authToken has a default value of the current token.
  // We can also pass a different token, for example after login.
  function getHeaders(authToken = token) {
    return {
      Authorization: `Bearer ${authToken}`,
      "Content-Type": "application/json",
    };
  }


  // ---------------------------------------------------
  // 3. LOAD LOGGED-IN USER PROFILE
  // ---------------------------------------------------

  // Requests the current user's profile from the backend.
  // This endpoint is protected and requires a valid JWT token.
  async function loadProfile(authToken = token) {

    const response = await fetch(`${API_URL}/users/me`, {
      headers: getHeaders(authToken),
    });

    // If the backend rejects the request, the token may be invalid
    // or the user's session may have expired.
    if (!response.ok) {
      throw new Error("Session expired. Please log in again.");
    }

    // Convert the JSON response into a JavaScript object.
    const data = await response.json();

    // Save the user information in React state.
    setUser(data);
  }


  // ---------------------------------------------------
  // 4. LOAD ALL EVENTS
  // ---------------------------------------------------

  // Gets all events from the backend.
  // The GET /events endpoint returns the available events.
  async function loadEvents() {

    const response = await fetch(`${API_URL}/events`);

    // Stop and show an error if the request fails.
    if (!response.ok) {
      throw new Error("Could not load events.");
    }

    // Convert the backend JSON response into JavaScript data.
    const data = await response.json();

    // Save the events in React state.
    // React automatically updates the UI when this state changes.
    setEvents(data);
  }


  // ---------------------------------------------------
  // 5. RESTORE USER SESSION WHEN APP OPENS
  // ---------------------------------------------------

  // useEffect runs after the component is first rendered.
  // The empty dependency array [] means this effect runs once
  // when the component is mounted.
  useEffect(() => {

    // If there is no saved token, there is no session to restore.
    if (!token) return;

    // This async function checks whether the saved token is still valid.
    async function restoreSession() {
      try {

        // First, verify the token by loading the user's profile.
        await loadProfile(token);

        // Then load events for the dashboard.
        await loadEvents();

      } catch (err) {

        // If session restoration fails, remove the invalid token.
        localStorage.removeItem("token");

        // Clear authentication and profile information.
        setToken("");
        setUser(null);

        // Display the reason for failure.
        setError(err.message);
      }
    }

    // Start restoring the saved session.
    restoreSession();

  }, []);


  // ---------------------------------------------------
  // 6. USER LOGIN
  // ---------------------------------------------------

  // Called when the user submits the login form.
  async function handleLogin(e) {

    // Prevent the browser from refreshing the page
    // when the form is submitted.
    e.preventDefault();

    // Show loading state and clear old messages.
    setLoading(true);
    setError("");
    setMessage("");

    try {

      // Send login credentials to the FastAPI backend.
      const response = await fetch(`${API_URL}/login`, {
        method: "POST",

        // Login does not require a token.
        headers: { "Content-Type": "application/json" },

        // Convert email and password into JSON.
        body: JSON.stringify({ email, password }),
      });

      // Read the backend response.
      const data = await response.json();

      // If login fails, display the error returned by the backend.
      if (!response.ok) {
        throw new Error(data.detail || "Login failed.");
      }

      // Save the JWT token in browser localStorage.
      // This allows the session to survive a page refresh.
      localStorage.setItem("token", data.access_token);

      // Update React state with the new token.
      setToken(data.access_token);

      // Load the logged-in user's profile using the new token.
      await loadProfile(data.access_token);

      // Load events after successful authentication.
      await loadEvents();

      // Show a success message.
      setMessage("Welcome back!");

    } catch (err) {

      // If login or profile loading fails, clear the saved session.
      localStorage.removeItem("token");
      setToken("");
      setUser(null);

      // Display the error message.
      setError(err.message);

    } finally {

      // Stop the loading state whether login succeeds or fails.
      setLoading(false);
    }
  }


  // ---------------------------------------------------
  // 7. USER LOGOUT
  // ---------------------------------------------------

  // Clears the current session and returns the user to login.
  function handleLogout() {

    // Remove the JWT token from browser storage.
    localStorage.removeItem("token");

    // Clear user authentication and application data.
    setToken("");
    setUser(null);
    setEvents([]);

    // Clear messages and password.
    setMessage("");
    setError("");
    setPassword("");
  }


  // ---------------------------------------------------
  // 8. CREATE A NEW EVENT
  // ---------------------------------------------------

  // Called when an admin submits the Create Event form.
  async function handleCreateEvent(e) {

    // Prevent the default browser form submission.
    e.preventDefault();

    // Show saving state and clear previous messages.
    setSaving(true);
    setError("");
    setMessage("");

    try {

      // Send a POST request to the backend to create an event.
      const response = await fetch(`${API_URL}/events`, {
        method: "POST",

        // Send the JWT token because creating an event
        // requires admin authentication.
        headers: getHeaders(),

        // Convert form data into JSON.
        body: JSON.stringify({

          // Copy all current event form values.
          ...newEvent,

          // Convert the date input into ISO date-time format.
          // The backend expects a valid date-time value.
          event_date: new Date(newEvent.event_date).toISOString(),

          // HTML number inputs can return strings.
          // Convert capacity into a JavaScript number.
          capacity: Number(newEvent.capacity),
        }),
      });

      // Read the response returned by FastAPI.
      const data = await response.json();

      // If the backend rejects the request, show its error.
      if (!response.ok) {
        throw new Error(data.detail || "Could not create event.");
      }

      // Clear the form after successful event creation.
      setNewEvent({
        title: "",
        description: "",
        event_date: "",
        location: "",
        capacity: 20,
      });

      // Refresh events so the newly created event appears.
      await loadEvents();

      // Show success message.
      setMessage("Your event has been created successfully!");

      // Navigate to the events page.
      setActivePage("events");

    } catch (err) {

      // Display any error that occurred during creation.
      setError(err.message);

    } finally {

      // Stop the saving indicator.
      setSaving(false);
    }
  }


  // ---------------------------------------------------
  // 9. REGISTER FOR AN EVENT
  // ---------------------------------------------------

  // Called when an employee clicks the Register Now button.
  // eventId identifies the event selected by the employee.
  async function handleRegister(eventId) {

    // Clear previous messages.
    setError("");
    setMessage("");

    try {

      // Send a POST request to register the logged-in user.
      const response = await fetch(
        `${API_URL}/events/${eventId}/registrations`,
        {
          method: "POST",

          // Send JWT authentication token.
          headers: getHeaders(),
        }
      );

      // Read the backend response.
      const data = await response.json();

      // If registration fails, display the backend error.
      // Examples: already registered or event capacity is full.
      if (!response.ok) {
        throw new Error(data.detail || "Registration failed.");
      }

      // Display successful registration message.
      setMessage("You have successfully registered for this event!");

    } catch (err) {

      // Display the error returned by the backend.
      setError(err.message);
    }
  }


  // ---------------------------------------------------
  // 10. DELETE AN EVENT
  // ---------------------------------------------------

  // Called when an admin clicks the Delete Event button.
  async function handleDeleteEvent(eventId) {

    // Ask the admin to confirm before deleting.
    // This prevents accidental deletion.
    const confirmed = window.confirm(
      "Are you sure you want to delete this event? Its registrations will also be deleted."
    );

    // If the admin selects Cancel, stop the function.
    if (!confirmed) return;

    // Clear previous messages.
    setError("");
    setMessage("");

    try {

      // Send a DELETE request for the selected event.
      const response = await fetch(`${API_URL}/events/${eventId}`, {
        method: "DELETE",

        // Include the admin's JWT token.
        headers: getHeaders(),
      });

      // If deletion fails, read the error returned by the backend.
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Could not delete event.");
      }

      // Refresh the event list after successful deletion.
      await loadEvents();

      // Show success message.
      setMessage("Event deleted successfully!");

    } catch (err) {

      // Display any deletion error.
      setError(err.message);
    }
  }


  // ---------------------------------------------------
  // 11. FILTER EVENTS USING SEARCH
  // ---------------------------------------------------

  // filter() creates a new array containing only matching events.
  // Search checks both event title and location.
  //
  // toLowerCase() makes the search case-insensitive.
  // includes() checks whether the search text exists in the event details.
  const filteredEvents = events.filter((event) =>
    `${event.title} ${event.location}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );


  // ---------------------------------------------------
  // 12. FIND UPCOMING EVENTS
  // ---------------------------------------------------

  // Keep only events whose date is today or in the future.
  // This value is used in the Upcoming Events dashboard statistic.
  const upcomingEvents = events.filter(
    (event) => new Date(event.event_date) >= new Date()
  );


  // ---------------------------------------------------
  // 13. FORMAT EVENT DATE
  // ---------------------------------------------------

  // Converts an event date into a readable format.
  // Example: 2026-12-20 becomes Dec 20, 2026.
  function formatDate(date) {
    return new Date(date).toLocaleDateString("en-US", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  }


  // ---------------------------------------------------
  // 14. FORMAT EVENT TIME
  // ---------------------------------------------------

  // Converts a date-time value into a readable time.
  // Example: 10:00 becomes 10:00 AM.
  function formatTime(date) {
    return new Date(date).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }


  // =====================================================
  // 15. LOGIN PAGE
  // =====================================================

  // If the user profile is not loaded,
  // display the login page instead of the dashboard.
  if (!user) {
    return (
      <div className="login-page">

        {/* Decorative left section of the login screen. */}
        <div className="login-decoration">

          {/* ACME brand logo and name. */}
          <div className="login-brand">
            <div className="brand-logo">A</div>
            <span>ACME EVENTS</span>
          </div>

          {/* Main introduction shown on the login page. */}
          <div className="login-hero">
            <span className="hero-label">CORPORATE EVENT MANAGEMENT</span>
            <h1>Bring your team together.</h1>
            <p>
              Discover, organize and manage company events from one
              professional workspace.
            </p>

            {/* Decorative symbols. */}
            <div className="hero-decoration">
              <span>✦</span>
              <span>✦</span>
              <span>✦</span>
            </div>
          </div>

          <p className="login-footer-text">
            Making every corporate moment count.
          </p>
        </div>


        {/* Right section containing the login form. */}
        <div className="login-panel">
          <div className="login-card">

            {/* Brand shown on smaller/mobile screens. */}
            <div className="mobile-brand">
              <div className="brand-logo">A</div>
              <span>ACME EVENTS</span>
            </div>

            <span className="form-eyebrow">WELCOME BACK</span>
            <h2>Sign in to your account</h2>
            <p className="login-description">
              Enter your credentials to access your workspace.
            </p>

            {/* Display error and success messages when available. */}
            {error && <div className="alert error">{error}</div>}
            {message && <div className="alert success">{message}</div>}

            {/* Login form.
                onSubmit calls handleLogin when the user submits it. */}
            <form onSubmit={handleLogin}>

              <label>Email address</label>

              {/* Controlled input:
                  value comes from React state.
                  onChange updates React state when the user types. */}
              <input
                type="email"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              <label>Password</label>

              <input
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />

              {/* Disable the button while login is processing. */}
              <button className="primary-button login-submit" disabled={loading}>
                {loading ? "Signing in..." : "Sign In to Dashboard →"}
              </button>
            </form>

            <p className="secure-note">
              🔒 Secure access powered by JWT authentication
            </p>
          </div>
        </div>
      </div>
    );
  }


  // =====================================================
  // 16. MAIN DASHBOARD
  // =====================================================

  // Once the user profile is available, show the dashboard.
  return (
    <div className="dashboard-layout">

      {/* -------------------------------------------------
          SIDEBAR
          Contains navigation, profile and logout button.
      -------------------------------------------------- */}

      <aside className="sidebar">

        {/* Sidebar brand. */}
        <div className="sidebar-brand">
          <div className="brand-logo">A</div>
          <div>
            <strong>ACME</strong>
            <span>EVENTS PORTAL</span>
          </div>
        </div>

        <div className="sidebar-label">WORKSPACE</div>

        {/* Navigation buttons change the active dashboard page. */}
        <nav className="sidebar-nav">

          {/* Overview navigation button. */}
          <button
            className={activePage === "dashboard" ? "nav-item active" : "nav-item"}
            onClick={() => setActivePage("dashboard")}
          >
            <span>▦</span> Overview
          </button>

          {/* All Events navigation button.
              Displays the total number of events. */}
          <button
            className={activePage === "events" ? "nav-item active" : "nav-item"}
            onClick={() => setActivePage("events")}
          >
            <span>▣</span> All Events
            <span className="nav-count">{events.length}</span>
          </button>

          {/* Only administrators can see Create Event navigation. */}
          {user.role === "admin" && (
            <button
              className={activePage === "create" ? "nav-item active" : "nav-item"}
              onClick={() => setActivePage("create")}
            >
              <span>＋</span> Create Event
            </button>
          )}
        </nav>


        {/* Bottom sidebar section containing profile and logout. */}
        <div className="sidebar-bottom">

          {/* Display the current user's information. */}
          <div className="profile-card">
            <div className="avatar">
              {/* Show the first letter of the user's name. */}
              {user.name?.charAt(0).toUpperCase()}
            </div>

            <div className="profile-info">
              <strong>{user.name}</strong>
              <span>{user.role}</span>
            </div>
          </div>

          {/* Logout button clears the current session. */}
          <button className="logout-button" onClick={handleLogout}>
            ↪ <span>Sign Out</span>
          </button>
        </div>
      </aside>


      {/* -------------------------------------------------
          MAIN CONTENT AREA
          Displays the selected dashboard page.
      -------------------------------------------------- */}

      <main className="main-content">

        {/* Top navigation bar. */}
        <header className="topbar">
          <div>
            <span className="topbar-label">ACME / WORKSPACE</span>

            {/* Page title changes according to activePage. */}
            <h2>
              {activePage === "create"
                ? "Create Event"
                : activePage === "events"
                ? "All Events"
                : "Overview"}
            </h2>
          </div>

          <div className="topbar-right">

            {/* Decorative system status indicator. */}
            <div className="online-indicator">
              <span></span> System Online
            </div>

            {/* Display the user's first initial. */}
            <div className="topbar-avatar">
              {user.name?.charAt(0).toUpperCase()}
            </div>
          </div>
        </header>


        {/* Main page content changes based on activePage. */}
        <div className="page-content">

          {/* Display application messages if they exist. */}
          {error && <div className="alert error">{error}</div>}
          {message && <div className="alert success">{message}</div>}


          {/* =================================================
              PAGE 1: DASHBOARD OVERVIEW
          ================================================== */}

          {activePage === "dashboard" && (
            <>

              {/* Welcome banner with a personalized greeting. */}
              <section className="welcome-banner">
                <div>
                  <span className="banner-label">YOUR EVENT WORKSPACE</span>
                  <h1>Hello, {user.name.split(" ")[0]} 👋</h1>

                  {/* Different introduction for admins and employees. */}
                  <p>
                    {user.role === "admin"
                      ? "Manage company events and bring your team together."
                      : "Explore upcoming events and find your next experience."}
                  </p>

                  {/* Admins get a shortcut to the event creation page. */}
                  {user.role === "admin" && (
                    <button
                      className="banner-button"
                      onClick={() => setActivePage("create")}
                    >
                      + Create an Event
                    </button>
                  )}
                </div>

                {/* Decorative banner artwork. */}
                <div className="banner-art">
                  <span>✦</span>
                  <span>✧</span>
                  <span>✦</span>
                  <div>EVENTS</div>
                </div>
              </section>


              {/* Dashboard statistics. */}
              <section className="stats-grid">

                {/* Total number of events. */}
                <div className="stat-card">
                  <div className="stat-icon blue">▣</div>
                  <span>Total Events</span>
                  <strong>{events.length}</strong>
                  <small>All company events</small>
                </div>

                {/* Number of events scheduled for today or later. */}
                <div className="stat-card">
                  <div className="stat-icon purple">◷</div>
                  <span>Upcoming Events</span>
                  <strong>{upcomingEvents.length}</strong>
                  <small>Scheduled for the future</small>
                </div>

                {/* Current user's role. */}
                <div className="stat-card">
                  <div className="stat-icon green">✓</div>
                  <span>Your Role</span>
                  <strong className="role-stat">
                    {user.role === "admin" ? "Admin" : "Employee"}
                  </strong>
                  <small>Account access level</small>
                </div>
              </section>


              {/* Featured events section. */}
              <section className="content-section">
                <div className="section-title">
                  <div>
                    <span className="section-eyebrow">DISCOVER</span>
                    <h2>Featured Events</h2>
                    <p>Explore what's happening at your company.</p>
                  </div>

                  {/* Navigate to the complete event list. */}
                  <button
                    className="text-button"
                    onClick={() => setActivePage("events")}
                  >
                    View all events →
                  </button>
                </div>


                {/* Show up to three events on the dashboard.
                    map() creates an EventCard component for each event. */}
                <div className="event-grid">
                  {events.slice(0, 3).map((event, index) => (
                    <EventCard
                      key={event.id}
                      event={event}
                      index={index}
                      user={user}
                      onRegister={handleRegister}
                      onDelete={handleDeleteEvent}
                      formatDate={formatDate}
                      formatTime={formatTime}
                    />
                  ))}
                </div>


                {/* Show this message if there are no events. */}
                {events.length === 0 && (
                  <EmptyState
                    text="No events have been created yet."
                    detail="Your company events will appear here."
                  />
                )}
              </section>
            </>
          )}


          {/* =================================================
              PAGE 2: ALL EVENTS
          ================================================== */}

          {activePage === "events" && (
            <section className="content-section events-page">
              <div className="section-title">
                <div>
                  <span className="section-eyebrow">EVENT DIRECTORY</span>
                  <h2>All Corporate Events</h2>
                  <p>Browse and manage company activities.</p>
                </div>

                {/* Reload the events from the backend. */}
                <button className="refresh-button" onClick={loadEvents}>
                  ↻ Refresh
                </button>
              </div>


              {/* Search input filters events by title or location. */}
              <div className="search-box">
                <span>⌕</span>
                <input
                  type="text"
                  placeholder="Search by event title or location..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>


              {/* Display every event that matches the search. */}
              <div className="event-grid">
                {filteredEvents.map((event, index) => (
                  <EventCard
                    key={event.id}
                    event={event}
                    index={index}
                    user={user}
                    onRegister={handleRegister}
                    onDelete={handleDeleteEvent}
                    formatDate={formatDate}
                    formatTime={formatTime}
                  />
                ))}
              </div>


              {/* Display an empty state if no events match. */}
              {filteredEvents.length === 0 && (
                <EmptyState
                  text="No matching events found."
                  detail="Try another search or create a new event."
                />
              )}
            </section>
          )}


          {/* =================================================
              PAGE 3: CREATE EVENT
              Only admins can access this page.
          ================================================== */}

          {activePage === "create" && user.role === "admin" && (
            <section className="create-page">
              <div className="section-title">
                <div>
                  <span className="section-eyebrow">EVENT MANAGEMENT</span>
                  <h2>Create a New Event</h2>
                  <p>Fill in the details to publish a company event.</p>
                </div>
              </div>


              <div className="create-layout">

                {/* Form for entering a new event. */}
                <form className="create-card" onSubmit={handleCreateEvent}>

                  <div className="form-card-heading">
                    <div className="form-icon">＋</div>
                    <div>
                      <h3>Event Information</h3>
                      <p>Enter the basic event details below.</p>
                    </div>
                  </div>


                  {/* Event title input. */}
                  <label>Event Title</label>
                  <input
                    type="text"
                    placeholder="e.g. Annual Technology Conference"
                    value={newEvent.title}
                    minLength={3}
                    onChange={(e) =>
                      setNewEvent({ ...newEvent, title: e.target.value })
                    }
                    required
                  />


                  {/* Optional event description. */}
                  <label>Event Description</label>
                  <textarea
                    placeholder="Tell employees what this event is about..."
                    value={newEvent.description}
                    onChange={(e) =>
                      setNewEvent({
                        ...newEvent,
                        description: e.target.value,
                      })
                    }
                  />


                  {/* Location and capacity fields share one row. */}
                  <div className="form-row">

                    <div>
                      <label>Location</label>
                      <input
                        type="text"
                        placeholder="City or venue"
                        value={newEvent.location}
                        onChange={(e) =>
                          setNewEvent({
                            ...newEvent,
                            location: e.target.value,
                          })
                        }
                        required
                      />
                    </div>

                    <div>
                      <label>Maximum Capacity</label>
                      <input
                        type="number"
                        min="1"
                        value={newEvent.capacity}
                        onChange={(e) =>
                          setNewEvent({
                            ...newEvent,
                            capacity: e.target.value,
                          })
                        }
                        required
                      />
                    </div>
                  </div>


                  {/* Date and time input for the event. */}
                  <label>Event Date & Time</label>
                  <input
                    type="datetime-local"
                    value={newEvent.event_date}
                    onChange={(e) =>
                      setNewEvent({
                        ...newEvent,
                        event_date: e.target.value,
                      })
                    }
                    required
                  />


                  {/* Form action buttons. */}
                  <div className="form-actions">

                    {/* Cancel returns the user to the dashboard. */}
                    <button
                      type="button"
                      className="cancel-button"
                      onClick={() => setActivePage("dashboard")}
                    >
                      Cancel
                    </button>

                    {/* Submit creates the event.
                        Disable the button while saving is in progress. */}
                    <button
                      type="submit"
                      className="primary-button"
                      disabled={saving}
                    >
                      {saving ? "Creating..." : "Publish Event →"}
                    </button>
                  </div>
                </form>


                {/* Helpful tips displayed beside the form. */}
                <aside className="create-tip">
                  <div className="tip-icon">✦</div>
                  <h3>Make it memorable.</h3>
                  <p>
                    Great events bring people together. Add clear details so
                    employees know exactly what to expect.
                  </p>

                  <div className="tip-divider"></div>

                  <strong>Before publishing</strong>
                  <ul>
                    <li>Choose a clear event title.</li>
                    <li>Confirm the date and time.</li>
                    <li>Set the participant capacity.</li>
                    <li>Provide the event location.</li>
                  </ul>
                </aside>
              </div>
            </section>
          )}


          {/* Footer displayed at the bottom of the dashboard. */}
          <footer className="dashboard-footer">
            <span>© 2026 ACME Corporate Events</span>
            <span>Powered by React · FastAPI · PostgreSQL</span>
          </footer>
        </div>
      </main>
    </div>
  );
}


// =====================================================
// 17. EVENT CARD COMPONENT
// =====================================================

// This is a reusable component.
// Instead of writing the same event-card HTML multiple times,
// we create one component and pass event information through props.
//
// Props are data/functions received from the parent component.
function EventCard({
  event,
  index,
  user,
  onRegister,
  onDelete,
  formatDate,
  formatTime,
}) {

  // Define three visual colors for event cards.
  const colors = ["blue", "purple", "orange"];

  // Choose a color based on the event's position.
  // The modulo operator (%) cycles through the colors.
  const color = colors[index % colors.length];

  return (
    <article className="event-card">

      {/* Decorative event-card header. */}
      <div className={`event-card-cover ${color}`}>
        <span className="cover-label">CORPORATE EVENT</span>
        <span className="cover-symbol">✦</span>
        <span className="cover-id">EVENT #{event.id}</span>
      </div>


      {/* Main event information. */}
      <div className="event-card-body">
        <h3>{event.title}</h3>

        {/* Display a fallback message if no description exists. */}
        <p className="event-description">
          {event.description || "No event description provided."}
        </p>


        {/* Display event details. */}
        <div className="event-meta">

          <div>
            <span className="meta-icon">▦</span>
            <span>{formatDate(event.event_date)}</span>
          </div>

          <div>
            <span className="meta-icon">◷</span>
            <span>{formatTime(event.event_date)}</span>
          </div>

          <div>
            <span className="meta-icon">⌖</span>
            <span>{event.location}</span>
          </div>

          <div>
            <span className="meta-icon">♙</span>
            <span>{event.capacity} participant capacity</span>
          </div>
        </div>


        {/* Show different actions according to the user's role. */}
        <div className="event-card-action">

          {user.role === "admin" ? (

            // Admins can delete events.
            <button
              className="delete-button"
              onClick={() => onDelete(event.id)}
            >
              Delete Event
            </button>

          ) : (

            // Employees can register for events.
            <button
              className="register-button"
              onClick={() => onRegister(event.id)}
            >
              Register Now →
            </button>

          )}
        </div>
      </div>
    </article>
  );
}


// =====================================================
// 18. EMPTY STATE COMPONENT
// =====================================================

// A reusable component for displaying a message
// when there are no events or no search results.
function EmptyState({ text, detail }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">▣</div>

      {/* Main empty-state message. */}
      <h3>{text}</h3>

      {/* Additional explanation. */}
      <p>{detail}</p>
    </div>
  );
}


// =====================================================
// 19. EXPORT MAIN COMPONENT
// =====================================================

// Export App so main.jsx can import it
// and display the application in the browser.
export default App;
