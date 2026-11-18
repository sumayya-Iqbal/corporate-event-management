
import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [user, setUser] = useState(null);
  const [events, setEvents] = useState([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [activePage, setActivePage] = useState("dashboard");

  const [newEvent, setNewEvent] = useState({
    title: "",
    description: "",
    event_date: "",
    location: "",
    capacity: 20,
  });

  function getHeaders(authToken = token) {
    return {
      Authorization: `Bearer ${authToken}`,
      "Content-Type": "application/json",
    };
  }

  async function loadProfile(authToken = token) {
    const response = await fetch(`${API_URL}/users/me`, {
      headers: getHeaders(authToken),
    });

    if (!response.ok) {
      throw new Error("Session expired. Please log in again.");
    }

    const data = await response.json();
    setUser(data);
  }

  async function loadEvents() {
    const response = await fetch(`${API_URL}/events`);

    if (!response.ok) {
      throw new Error("Could not load events.");
    }

    const data = await response.json();
    setEvents(data);
  }

  useEffect(() => {
    if (!token) return;

    async function restoreSession() {
      try {
        await loadProfile(token);
        await loadEvents();
      } catch (err) {
        localStorage.removeItem("token");
        setToken("");
        setUser(null);
        setError(err.message);
      }
    }

    restoreSession();
  }, []);

  async function handleLogin(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Login failed.");
      }

      localStorage.setItem("token", data.access_token);
      setToken(data.access_token);

      await loadProfile(data.access_token);
      await loadEvents();

      setMessage("Welcome back!");
    } catch (err) {
      localStorage.removeItem("token");
      setToken("");
      setUser(null);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("token");
    setToken("");
    setUser(null);
    setEvents([]);
    setMessage("");
    setError("");
    setPassword("");
  }

  async function handleCreateEvent(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/events`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({
          ...newEvent,
          event_date: new Date(newEvent.event_date).toISOString(),
          capacity: Number(newEvent.capacity),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not create event.");
      }

      setNewEvent({
        title: "",
        description: "",
        event_date: "",
        location: "",
        capacity: 20,
      });

      await loadEvents();
      setMessage("Your event has been created successfully!");
      setActivePage("events");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleRegister(eventId) {
    setError("");
    setMessage("");

    try {
      const response = await fetch(
        `${API_URL}/events/${eventId}/registrations`,
        {
          method: "POST",
          headers: getHeaders(),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Registration failed.");
      }

      setMessage("You have successfully registered for this event!");
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDeleteEvent(eventId) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this event? Its registrations will also be deleted."
    );

    if (!confirmed) return;

    setError("");
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/events/${eventId}`, {
        method: "DELETE",
        headers: getHeaders(),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Could not delete event.");
      }

      await loadEvents();
      setMessage("Event deleted successfully!");
    } catch (err) {
      setError(err.message);
    }
  }

  const filteredEvents = events.filter((event) =>
    `${event.title} ${event.location}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  const upcomingEvents = events.filter(
    (event) => new Date(event.event_date) >= new Date()
  );

  function formatDate(date) {
    return new Date(date).toLocaleDateString("en-US", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  }

  function formatTime(date) {
    return new Date(date).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  if (!user) {
    return (
      <div className="login-page">
        <div className="login-decoration">
          <div className="login-brand">
            <div className="brand-logo">A</div>
            <span>ACME EVENTS</span>
          </div>

          <div className="login-hero">
            <span className="hero-label">CORPORATE EVENT MANAGEMENT</span>
            <h1>Bring your team together.</h1>
            <p>
              Discover, organize and manage company events from one
              professional workspace.
            </p>
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

        <div className="login-panel">
          <div className="login-card">
            <div className="mobile-brand">
              <div className="brand-logo">A</div>
              <span>ACME EVENTS</span>
            </div>

            <span className="form-eyebrow">WELCOME BACK</span>
            <h2>Sign in to your account</h2>
            <p className="login-description">
              Enter your credentials to access your workspace.
            </p>

            {error && <div className="alert error">{error}</div>}
            {message && <div className="alert success">{message}</div>}

            <form onSubmit={handleLogin}>
              <label>Email address</label>
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

  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-logo">A</div>
          <div>
            <strong>ACME</strong>
            <span>EVENTS PORTAL</span>
          </div>
        </div>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="sidebar-nav">
          <button
            className={activePage === "dashboard" ? "nav-item active" : "nav-item"}
            onClick={() => setActivePage("dashboard")}
          >
            <span>▦</span> Overview
          </button>

          <button
            className={activePage === "events" ? "nav-item active" : "nav-item"}
            onClick={() => setActivePage("events")}
          >
            <span>▣</span> All Events
            <span className="nav-count">{events.length}</span>
          </button>

          {user.role === "admin" && (
            <button
              className={activePage === "create" ? "nav-item active" : "nav-item"}
              onClick={() => setActivePage("create")}
            >
              <span>＋</span> Create Event
            </button>
          )}
        </nav>

        <div className="sidebar-bottom">
          <div className="profile-card">
            <div className="avatar">
              {user.name?.charAt(0).toUpperCase()}
            </div>
            <div className="profile-info">
              <strong>{user.name}</strong>
              <span>{user.role}</span>
            </div>
          </div>

          <button className="logout-button" onClick={handleLogout}>
            ↪ <span>Sign Out</span>
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="topbar-label">ACME / WORKSPACE</span>
            <h2>
              {activePage === "create"
                ? "Create Event"
                : activePage === "events"
                ? "All Events"
                : "Overview"}
            </h2>
          </div>

          <div className="topbar-right">
            <div className="online-indicator">
              <span></span> System Online
            </div>
            <div className="topbar-avatar">
              {user.name?.charAt(0).toUpperCase()}
            </div>
          </div>
        </header>

        <div className="page-content">
          {error && <div className="alert error">{error}</div>}
          {message && <div className="alert success">{message}</div>}

          {activePage === "dashboard" && (
            <>
              <section className="welcome-banner">
                <div>
                  <span className="banner-label">YOUR EVENT WORKSPACE</span>
                  <h1>Hello, {user.name.split(" ")[0]} 👋</h1>
                  <p>
                    {user.role === "admin"
                      ? "Manage company events and bring your team together."
                      : "Explore upcoming events and find your next experience."}
                  </p>
                  {user.role === "admin" && (
                    <button
                      className="banner-button"
                      onClick={() => setActivePage("create")}
                    >
                      + Create an Event
                    </button>
                  )}
                </div>
                <div className="banner-art">
                  <span>✦</span>
                  <span>✧</span>
                  <span>✦</span>
                  <div>EVENTS</div>
                </div>
              </section>

              <section className="stats-grid">
                <div className="stat-card">
                  <div className="stat-icon blue">▣</div>
                  <span>Total Events</span>
                  <strong>{events.length}</strong>
                  <small>All company events</small>
                </div>

                <div className="stat-card">
                  <div className="stat-icon purple">◷</div>
                  <span>Upcoming Events</span>
                  <strong>{upcomingEvents.length}</strong>
                  <small>Scheduled for the future</small>
                </div>

                <div className="stat-card">
                  <div className="stat-icon green">✓</div>
                  <span>Your Role</span>
                  <strong className="role-stat">
                    {user.role === "admin" ? "Admin" : "Employee"}
                  </strong>
                  <small>Account access level</small>
                </div>
              </section>

              <section className="content-section">
                <div className="section-title">
                  <div>
                    <span className="section-eyebrow">DISCOVER</span>
                    <h2>Featured Events</h2>
                    <p>Explore what's happening at your company.</p>
                  </div>
                  <button
                    className="text-button"
                    onClick={() => setActivePage("events")}
                  >
                    View all events →
                  </button>
                </div>

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

                {events.length === 0 && (
                  <EmptyState
                    text="No events have been created yet."
                    detail="Your company events will appear here."
                  />
                )}
              </section>
            </>
          )}

          {activePage === "events" && (
            <section className="content-section events-page">
              <div className="section-title">
                <div>
                  <span className="section-eyebrow">EVENT DIRECTORY</span>
                  <h2>All Corporate Events</h2>
                  <p>Browse and manage company activities.</p>
                </div>
                <button className="refresh-button" onClick={loadEvents}>
                  ↻ Refresh
                </button>
              </div>

              <div className="search-box">
                <span>⌕</span>
                <input
                  type="text"
                  placeholder="Search by event title or location..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>

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

              {filteredEvents.length === 0 && (
                <EmptyState
                  text="No matching events found."
                  detail="Try another search or create a new event."
                />
              )}
            </section>
          )}

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
                <form className="create-card" onSubmit={handleCreateEvent}>
                  <div className="form-card-heading">
                    <div className="form-icon">＋</div>
                    <div>
                      <h3>Event Information</h3>
                      <p>Enter the basic event details below.</p>
                    </div>
                  </div>

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

                  <div className="form-actions">
                    <button
                      type="button"
                      className="cancel-button"
                      onClick={() => setActivePage("dashboard")}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="primary-button"
                      disabled={saving}
                    >
                      {saving ? "Creating..." : "Publish Event →"}
                    </button>
                  </div>
                </form>

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

          <footer className="dashboard-footer">
            <span>© 2026 ACME Corporate Events</span>
            <span>Powered by React · FastAPI · PostgreSQL</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

function EventCard({
  event,
  index,
  user,
  onRegister,
  onDelete,
  formatDate,
  formatTime,
}) {
  const colors = ["blue", "purple", "orange"];
  const color = colors[index % colors.length];

  return (
    <article className="event-card">
      <div className={`event-card-cover ${color}`}>
        <span className="cover-label">CORPORATE EVENT</span>
        <span className="cover-symbol">✦</span>
        <span className="cover-id">EVENT #{event.id}</span>
      </div>

      <div className="event-card-body">
        <h3>{event.title}</h3>
        <p className="event-description">
          {event.description || "No event description provided."}
        </p>

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

        <div className="event-card-action">
          {user.role === "admin" ? (
            <button
              className="delete-button"
              onClick={() => onDelete(event.id)}
            >
              Delete Event
            </button>
          ) : (
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

function EmptyState({ text, detail }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">▣</div>
      <h3>{text}</h3>
      <p>{detail}</p>
    </div>
  );
}

export default App;
