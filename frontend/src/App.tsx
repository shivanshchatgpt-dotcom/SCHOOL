import { Link, Navigate, Route, Routes } from "react-router-dom";
import { useEffect, useState } from "react";
import Home from "./pages/Home";
import Paths from "./pages/Paths";
import Assessment from "./pages/Assessment";
import Dashboard from "./pages/Dashboard";
import RoadmapView from "./pages/RoadmapView";
import RoadmapsMenu from "./components/RoadmapsMenu";
import { savedLearner } from "./lib/learner";

export default function App() {
  const [learner, setLearner] = useState(savedLearner());
  useEffect(() => {
    const update = () => setLearner(savedLearner());
    window.addEventListener("pyschool:learner-changed", update);
    return () => window.removeEventListener("pyschool:learner-changed", update);
  }, []);
  return <>
    <header className="border-b border-gray-200 bg-white sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-5 h-16 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <RoadmapsMenu />
          <Link to="/" className="font-black text-xl tracking-tight">PySchool<span className="text-gray-400">.</span></Link>
        </div>
        <nav className="flex items-center gap-5 text-sm font-semibold text-gray-600">
          <Link to="/paths" className="hover:text-black">Career paths</Link>
          {learner && <Link to={`/dashboard/${learner.enrollmentId}`} className="text-black">Continue learning</Link>}
        </nav>
      </div>
    </header>
    <main className="max-w-6xl mx-auto px-5 py-8"><Routes>
      <Route path="/" element={<Home />} />
      <Route path="/paths" element={<Paths />} />
      <Route path="/paths/:slug/assessment" element={<Assessment />} />
      <Route path="/roadmaps/:slug" element={<RoadmapView />} />
      <Route path="/dashboard/:id" element={<Dashboard />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes></main>
  </>;
}
