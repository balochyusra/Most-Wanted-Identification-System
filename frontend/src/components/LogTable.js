import React, { useEffect, useState } from 'react';
import { fetchLogs, clearLogs, deleteLog } from '../services/api';

function LogTable() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const res = await fetchLogs(200);
      setLogs(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this log entry?')) return;
    await deleteLog(id);
    setLogs((prev) => prev.filter((l) => l.id !== id));
  };

  const handleClear = async () => {
    if (!window.confirm('Clear ALL match logs? This cannot be undone.')) return;
    await clearLogs();
    setLogs([]);
  };

  if (loading) return <div className="empty-state">Loading logs...</div>;

  return (
    <div>
      <div className="flex-row mb-4" style={{ justifyContent: 'space-between' }}>
        <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          {logs.length} match record(s)
        </div>
        {logs.length > 0 && (
          <button className="btn btn-danger btn-sm" onClick={handleClear}>
            🗑 Clear All
          </button>
        )}
      </div>

      {logs.length === 0 ? (
        <div className="empty-state">No match logs yet. System is watching.</div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Criminal</th>
                <th>Confidence</th>
                <th>Snapshot</th>
                <th>Timestamp</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, i) => (
                <tr key={log.id}>
                  <td style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    {i + 1}
                  </td>
                  <td style={{ color: 'var(--accent-red-light)', fontWeight: 600 }}>
                    {log.criminal_name}
                  </td>
                  <td>
                    <div className="conf-bar-wrap">
                      <div className="conf-bar">
                        <div
                          className="conf-bar-fill"
                          style={{ width: `${Math.min(log.confidence, 100)}%` }}
                        />
                      </div>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                        {log.confidence.toFixed(1)}%
                      </span>
                    </div>
                  </td>
                  <td>
                    {log.snapshot_path ? (
                      <a
                        href={`http://localhost:8000/${log.snapshot_path.replace(/\\/g, '/')}`}
                        target="_blank"
                        rel="noreferrer"
                        style={{ color: 'var(--accent-blue)', fontSize: 12 }}
                      >
                        View
                      </a>
                    ) : (
                      <span style={{ color: 'var(--text-muted)' }}>—</span>
                    )}
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDelete(log.id)}
                    >
                      ✕
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default LogTable;
