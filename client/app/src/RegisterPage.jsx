import React, { useState } from "react";
import "./LoginPage.css";
import axios from "axios";


function RegisterPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [conPassword, setConPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const handleUsernameChange = (event) => {
    setUsername(event.target.value);
  };

  const handlePasswordChange = (event) => {
    setPassword(event.target.value);
  };

  const handleConPasswordChange = (event) => {
    setConPassword(event.target.value);
  };

  const handleNameChange = (event) => {
    setName(event.target.value);
  };

  const handleSubmit = async (event) => {
        event.preventDefault();
    if (password != conPassword) {
        setError("Password and confirm password fields do not match")
        return
    }
    try {
      const response = await axios.post("http://127.0.0.1:5000/api/users", {
        email: username,
        password: password,
        name: name
      });
      if (response.status == 400) {
        setError("user already exists")
        return
      }
  
      // Redirect to the chat page
      window.location.href = "/";
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
          Your Nickname:
          <input
            type="text"
            name="name" // Add the name attribute
            value={name}
            onChange={handleNameChange}
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
        <label>
          Confirm Password:
          <input
            type="password"
            name="conPassword" // Add the name attribute
            value={conPassword}
            onChange={handleConPasswordChange}
            required
          />
        </label>
        {error && <div className="error">{error}</div>}
        <button type="submit" className="login-button">
          Sign Up
        </button>
      </form>
    </div>
  );
}

export default RegisterPage;
