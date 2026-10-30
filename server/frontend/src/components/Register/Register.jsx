import React, { useState } from "react";
import "./Register.css";
import Header from "../Header/Header";

const Register = () => {
  const [userName, setUserName] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const register = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      const response = await fetch(
        window.location.origin + "/djangoapp/register",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            userName,
            firstName,
            lastName,
            password,
          }),
        }
      );

      const data = await response.json();

      if (response.ok && data.status === "Account created") {
        alert("Account created successfully. Please log in.");
        window.location.href = "/login";
      } else {
        setMessage(data.message || data.error || "Registration failed.");
      }
    } catch (error) {
      setMessage("Unable to connect to the registration service.");
    }
  };

  return (
    <div>
      <Header />
      <div className="register_container">
        <h2 className="header">Register</h2>

        <form onSubmit={register} className="inputs">
          <div className="input">
            <input
              className="input_field"
              type="text"
              placeholder="Username"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              required
            />
          </div>

          <div className="input">
            <input
              className="input_field"
              type="text"
              placeholder="First Name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
            />
          </div>

          <div className="input">
            <input
              className="input_field"
              type="text"
              placeholder="Last Name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
            />
          </div>

          <div className="input">
            <input
              className="input_field"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {message && <p role="alert">{message}</p>}

          <div className="submit_panel">
            <button className="submit" type="submit">
              Create Account
            </button>
          </div>

          <p>
            Already have an account? <a href="/login">Login</a>
          </p>
        </form>
      </div>
    </div>
  );
};

export default Register;
