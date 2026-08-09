import React from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'

export default function App() {
  const linkClass = ({ isActive }) =>
    `block px-4 py-2 rounded ${isActive ? 'bg-slate-700 text-white' : 'text-slate-300 hover:bg-slate-800'}`

  return (
    <BrowserRouter>
      <div className="flex h-screen">
        <aside className="w-56 bg-slate-900 p-4 border-r border-slate-800">
          <h1 className="text-lg font-bold mb-6 text-sky-400">VN Research</h1>
          <nav className="space-y-1">
            <NavLink to="/" className={linkClass} end>Dashboard</NavLink>
            <NavLink to="/watchlist" className={linkClass}>Watchlist</NavLink>
            <NavLink to="/stock/VNM" className={linkClass}>Stock: VNM</NavLink>
            <NavLink to="/sector" className={linkClass}>Sectors</NavLink>
          </nav>
          <div className="mt-8 text-xs text-slate-500">
            <p>Backend: localhost:8900</p>
            <p>Data: vnstock-agent</p>
          </div>
        </aside>
        <main className="flex-1 overflow-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/watchlist" element={<Watchlist />} />
            <Route path="/stock/:symbol" element={<StockDetail />} />
            <Route path="/sector" element={<SectorCenter />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
