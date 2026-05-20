import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import UserManual from "./pages/UserManual";
import Layout from "./components/Layout";
import DashboardHome from "./pages/DashboardHome";
import Overview from "./pages/Overview";
import DailyTables from "./pages/DailyTables";
import PortfolioManage from "./pages/PortfolioManage";
import PortfolioAnalysis from "./pages/PortfolioAnalysis";
import Strategy from "./pages/Strategy";
import Ranking from "./pages/Ranking";

function AppLayout({ children }: { children: React.ReactNode }) {
  return <Layout>{children}</Layout>;
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/help/user-manual" element={<UserManual />} />
        <Route path="/app" element={<AppLayout><DashboardHome /></AppLayout>} />
        <Route path="/app/overview" element={<AppLayout><Overview /></AppLayout>} />
        <Route path="/app/tables" element={<AppLayout><DailyTables /></AppLayout>} />
        <Route path="/app/portfolio" element={<AppLayout><PortfolioManage /></AppLayout>} />
        <Route path="/app/analysis" element={<AppLayout><PortfolioAnalysis /></AppLayout>} />
        <Route path="/app/strategy" element={<AppLayout><Strategy /></AppLayout>} />
        <Route path="/app/ranking" element={<AppLayout><Ranking /></AppLayout>} />
      </Routes>
    </Router>
  );
}
