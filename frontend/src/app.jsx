import React, { useState } from 'react'
import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import Predict from './pages/Predict'
import History from './pages/History'
import Stats from './pages/Stats'
import About from './pages/About'

const NAV = [
  { to: '/',        label: 'Predict',  icon: '🌱' },
  { to: '/history', label: 'History',  icon: '📋' },
  { to: '/stats',   label: 'Stats',    icon: '📊' },
  { to: '/about',   label: 'About',    icon: '🌿' },
]

export default function App() {
  const location = useLocation()

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <aside style={{
        width: 220,
        background: 'var(--soil)',
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        top: 0, left: 0, bottom: 0,
        zIndex: 100,
        boxShadow: '4px 0 20px rgba(0,0,0,0.2)',
      }}>
        {/* Logo */}
        <div style={{ padding: '32px 24px 28px' }}>
          <div style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: 22,
            fontWeight: 700,
            color: 'var(--sprout)',
            letterSpacing: '-0.3px',
          }}>
            🌾 CropSense
          </div>
          <div style={{
            fontSize: 11,
            color: 'var(--text-light)',
            marginTop: 4,
            letterSpacing: '1.5px',
            textTransform: 'uppercase',
          }}>
            Precision Agriculture
          </div>
        </div>

        {/* Divider */}
        <div style={{ height: 1, background: 'rgba(255,255,255,0.08)', margin: '0 20px 16px' }} />

        {/* Nav links */}
        <nav style={{ flex: 1, padding: '0 12px' }}>
          {NAV.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '11px 14px',
                borderRadius: 10,
                marginBottom: 4,
                fontSize: 14,
                fontWeight: isActive ? 500 : 400,
                color: isActive ? 'var(--sprout)' : 'rgba(240,237,230,0.65)',
                background: isActive ? 'rgba(93,138,60,0.18)' : 'transparent',
                transition: 'all var(--transition)',
                borderLeft: isActive ? '3px solid var(--sprout)' : '3px solid transparent',
              })}
            >
              <span style={{ fontSize: 16 }}>{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div style={{
          padding: '20px 24px',
          fontSize: 11,
          color: 'rgba(240,237,230,0.3)',
          borderTop: '1px solid rgba(255,255,255,0.06)',
        }}>
          v1.0.0 · ML + FastAPI + React
        </div>
      </aside>

      {/* Main content */}
      <main style={{ marginLeft: 220, flex: 1, minHeight: '100vh' }}>
        <Routes>
          <Route path="/"        element={<Predict />} />
          <Route path="/history" element={<History />} />
          <Route path="/stats"   element={<Stats />} />
          <Route path="/about"   element={<About />} />
        </Routes>
      </main>
    </div>
  )
}