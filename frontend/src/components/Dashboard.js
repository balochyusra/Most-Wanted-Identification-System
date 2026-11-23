import React, { useState, useEffect } from 'react';
import { fetchCriminals, fetchLogs } from '../services/api';
import CameraFeed from './CameraFeed';
import LogTable from './LogTable';

function StatCard({ label, value, sub, color }) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={{ color: color || 'var(--text-primary)' }}>{value}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}

function Dashboard() {
  const [stats, setStats] = useState({ criminals: 0, logs: 0, withFace: 0 });

  useEffect(() => {
    const load = async () => {
      try {
        const [cRes, lRes] = await Promise.all([fetchCriminals(), fetchLogs(1000)]);
        const criminals = cRes.data;
        const withFace = criminals.filter((c) => c.has_encoding).length;
        setStats({ criminals: criminals.length, logs: lRes.data.length, withFace });
      } catch (e) {
        console.error(e);
      }
    };
    load();
    const interval = setInterval(load, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      {/* Stats row */}
      <div className="grid-3 mb-4">
        <StatCard
          label="Criminals in DB"
          value={stats.criminals}
          sub={`${stats.withFace} with face encodings`}
          color="var(--accent-red-light)"
        />
        <StatCard
          label="Total Matches Logged"
          value={stats.logs}
          sub="All-time detections"
          color="var(--accent-amber)"
        />
        <StatCard
          label="System Status"
          value="ACTIVE"
          sub="Offline — no internet needed"
          color="var(--accent-green)"
        />
      </div>

      {/* Camera + recent logs */}
      <div className="grid-2">
        <div className="card">
          <div className="card-title">📷 Live Camera Feed</div>
          <CameraFeed />
        </div>

        <div className="card">
          <div className="card-title">🔴 Recent Match Logs</div>
          <LogTable />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
