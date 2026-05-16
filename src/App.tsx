import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "@/pages/Login";
import UserManual from "@/pages/UserManual";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/help/user-manual" element={<UserManual />} />
      </Routes>
    </Router>
  );
}
