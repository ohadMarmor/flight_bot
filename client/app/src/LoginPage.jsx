import React, { useState } from "react";
import "./LoginPage.css";
import "./users.json"
import axios from "axios";
import { Link } from 'react-router-dom';


function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleUsernameChange = (event) => {
    setUsername(event.target.value);
  };

  const handlePasswordChange = (event) => {
    setPassword(event.target.value);
  };


  const handleSubmit = async (event) => {
        event.preventDefault();
  
    try {
      const response = await axios.post("http://127.0.0.1:5000/api/login", {
        email: username,
        password: password,
      });
      // Extract the JWT from the server response
      const { access_token } = response.data;
  
      // Store the JWT in localStorage or cookies for future use
      localStorage.setItem("jwt", access_token);
  
      // Redirect to the chat page
      window.location.href = "/chat?token=" + access_token;
    } catch (error) {
      setError("Invalid username or password!");
    }
  };
  

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
      <label>
          Username:
          <input
            type="text"
            name="email" // Add the name attribute
            value={username}
            onChange={handleUsernameChange}
            required
          />
        </label>
        <label>
          Password:
          <input
            type="password"
            name="password" // Add the name attribute
            value={password}
            onChange={handlePasswordChange}
            required
          />
        </label>
        {error && <div className="error">{error}</div>}
        <button type="submit" className="login-button">
          Login
        </button>
        <div className="register-link">
            Don't have an account? <Link to="/register">Register</Link>
        </div>
      </form>
    </div>
  );
}

export default LoginPage;
