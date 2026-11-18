
// Import StrictMode from React.
// StrictMode helps identify potential problems in your React code
// during development. It can show warnings about unsafe practices.
import { StrictMode } from 'react'

// Import createRoot to create the React root where our app will run.
import { createRoot } from 'react-dom/client'

// Import the global CSS file.
// This file contains styles that can apply to the entire application.
import './index.css'

// Import the main App component.
// App.jsx contains the main pages, dashboard, login, and other UI.
import App from './App.jsx'

// Find the HTML element with the id "root".
// React will display the entire application inside this element.
createRoot(document.getElementById('root')).render(

  // StrictMode wraps our application.
  // It helps detect potential issues while developing.
  <StrictMode>

    <App />

  </StrictMode>,
)
