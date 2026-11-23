import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import CriminalList from './components/CriminalList';
import LogTable from './components/LogTable';

const PAGES = {
  dashboard: { label: '🖥 Dashboard', icon: '🖥' },
  criminals: { label: '🗂 Criminals DB', icon: '🗂' },
  logs: { label: '📋 Match Logs', icon: '📋' },
};

function App() {
  const [page, setPage] = useState('dashboard');
  const [time, setTime] = useState(new Date());

  React.useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h2>⚠ Most-Wanted<br />ID System</h2>
          <span>v1.0.0 · Offline</span>
        </div>

        <nav className="sidebar-nav">
          {Object.entries(PAGES).map(([key, { label }]) => (
            <button
              key={key}
              className={`nav-link ${page === key ? 'active' : ''}`}
              onClick={() => setPage(key)}
            >
              {label}
            </button>
          ))}
        </nav>

        <div className="sidebar-status">
          <div><span className="status-dot online" />System Online</div>
          <div style={{ marginTop: 4, fontFamily: 'var(--font-mono)' }}>
            {time.toLocaleTimeString()}
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="main-content">
        <div className="top-bar">
          <h1>
            {page === 'dashboard' && '🖥 Live Dashboard'}
            {page === 'criminals' && '🗂 Criminals Database'}
            {page === 'logs' && '📋 Match Logs'}
          </h1>
          <div className="top-bar-meta">
            {time.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </div>
        </div>

        <div className="page-body">
          {page === 'dashboard' && <Dashboard />}
          {page === 'criminals' && (
            <div className="card">
              <div className="card-title">🗂 Criminals Database</div>
              <CriminalList />
            </div>
          )}
          {page === 'logs' && (
            <div className="card">
              <div className="card-title">📋 All Match Logs</div>
              <LogTable />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
