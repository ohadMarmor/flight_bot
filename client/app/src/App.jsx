import React from "react";
import LoginPage from "./LoginPage";
import Chat from "./Chat"
import {BrowserRouter as Router, Route, Routes} from "react-router-dom";
import { Home } from "./Home";
import RegisterPage from "./RegisterPage";


function App() {
  return (
    <div className="App">
        <Router>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/register" element={<RegisterPage />} /> 
          </Routes>
        </Router>
      </div>
  );
}

export default App;
