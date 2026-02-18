import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import RagChat from './pages/RagChat'
import MmmDashboard from './pages/MmmDashboard'
import DataManagement from './pages/DataManagement'

const NAV_ITEMS = [
  {
    to: '/rag',
    label: 'RAG Chat',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    ),
  },
  {
    to: '/mmm',
    label: 'MMM Dashboard',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
        <line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/>
      </svg>
    ),
  },
  {
    to: '/data',
    label: 'Data Management',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
        <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
      </svg>
    ),
  },
]

function SunIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="4"/>
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>
    </svg>
  )
}

function MoonIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
  )
}

const THEME_KEY = 'platform-theme'

function Sidebar({ theme, onToggleTheme }) {
  return (
    <aside style={{
      width: 240,
      minHeight: '100vh',
      background: 'var(--bg-sidebar)',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
    }}>
      {/* Brand */}
      <div style={{
        padding: '20px 20px 16px',
        borderBottom: '1px solid rgba(255,255,255,0.08)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'var(--accent)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 15, fontWeight: 700, color: '#fff',
          }}>R</div>
          <div>
            <div style={{ color: '#fff', fontWeight: 600, fontSize: 13, lineHeight: 1.2 }}>RAG + MMM</div>
            <div style={{ color: 'var(--text-sidebar)', fontSize: 11, opacity: 0.7 }}>Platform</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '12px 8px' }}>
        <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: '0.08em', color: 'var(--text-sidebar)', opacity: 0.5, padding: '0 12px', marginBottom: 6, textTransform: 'uppercase' }}>
          Navigation
        </div>
        {NAV_ITEMS.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '9px 12px',
              borderRadius: 7,
              margin: '2px 0',
              textDecoration: 'none',
              fontSize: 14,
              fontWeight: isActive ? 600 : 400,
              color: isActive ? 'var(--text-sidebar-active)' : 'var(--text-sidebar)',
              background: isActive ? 'var(--bg-sidebar-active)' : 'transparent',
              transition: 'background 0.15s, color 0.15s',
            })}
            onMouseEnter={e => {
              if (!e.currentTarget.dataset.active) {
                e.currentTarget.style.background = 'var(--bg-sidebar-hover)'
              }
            }}
            onMouseLeave={e => {
              if (!e.currentTarget.classList.contains('active')) {
                e.currentTarget.style.background = e.currentTarget.getAttribute('data-active') === 'true' ? 'var(--bg-sidebar-active)' : 'transparent'
              }
            }}
          >
            <span style={{ opacity: 0.85 }}>{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Theme toggle */}
      <div style={{ padding: '12px 16px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
        <button
          onClick={onToggleTheme}
          style={{
            display: 'flex', alignItems: 'center', gap: 8,
            width: '100%', padding: '8px 12px', borderRadius: 7,
            background: 'rgba(255,255,255,0.06)', border: 'none',
            color: 'var(--text-sidebar)', cursor: 'pointer', fontSize: 13,
            transition: 'background 0.15s',
          }}
          title="Toggle theme"
        >
          {theme === 'dark' ? <SunIcon /> : <MoonIcon />}
          {theme === 'dark' ? 'Light mode' : 'Dark mode'}
        </button>
      </div>
    </aside>
  )
}

export default function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem(THEME_KEY) || 'light')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem(THEME_KEY, theme)
  }, [theme])

  const toggleTheme = () => setTheme(t => t === 'light' ? 'dark' : 'light')

  return (
    <BrowserRouter>
      <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
        <Sidebar theme={theme} onToggleTheme={toggleTheme} />
        <main style={{
          flex: 1, overflow: 'auto',
          background: 'var(--bg)',
          padding: '28px 32px',
        }}>
          <Routes>
            <Route path="/" element={<Navigate to="/rag" replace />} />
            <Route path="/rag" element={<RagChat />} />
            <Route path="/mmm" element={<MmmDashboard />} />
            <Route path="/data" element={<DataManagement />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
