import { Link, Navigate, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Paths from "./pages/Paths";
import Assessment from "./pages/Assessment";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return <>
    <header className="border-b border-gray-200 bg-white sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-5 h-16 flex items-center justify-between">
        <Link to="/" className="font-black text-xl tracking-tight">PySchool<span className="text-gray-400">.</span></Link>
        <nav className="flex items-center gap-5 text-sm font-semibold text-gray-600">
          <Link to="/paths" className="hover:text-black">Career paths</Link>
        </nav>
      </div>
    </header>
    <main className="max-w-6xl mx-auto px-5 py-8"><Routes>
      <Route path="/" element={<Home />} />
      <Route path="/paths" element={<Paths />} />
      <Route path="/paths/:slug/assessment" element={<Assessment />} />
      <Route path="/dashboard/:id" element={<Dashboard />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes></main>
  </>;
}
