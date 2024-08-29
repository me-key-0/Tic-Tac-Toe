import { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Navbar from "../src/components/Common/Header";
import LoginSignup from "./components/LoginSignup";
import "./App.css";

function App() {
  const [count, setCount] = useState(0);

  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/login" element={<LoginSignup />} />

          {/* Add more routes here as your app grows */}
          {/* Example: <Route path="/dashboard" element={<Dashboard />} /> */}

          {/* Redirect to /login if the route is not matched */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
