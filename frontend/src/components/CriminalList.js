import React, { useState, useEffect, useCallback } from 'react';
import { fetchCriminals, deleteCriminal } from '../services/api';
import AddCriminal from './AddCriminal';

function CriminalList() {
  const [criminals, setCriminals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [search, setSearch] = useState('');

  const load = useCallback(async () => {
    try {
      const res = await fetchCriminals();
      setCriminals(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete "${name}" from the database?`)) return;
    await deleteCriminal(id);
    setCriminals((prev) => prev.filter((c) => c.id !== id));
  };

  const filtered = criminals.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    (c.alias || '').toLowerCase().includes(search.toLowerCase()) ||
    c.crime.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <div className="empty-state">Loading criminals...</div>;

  return (
    <div>
      <div className="flex-row mb-4" style={{ justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
        <input
          className="form-input"
          style={{ maxWidth: 280 }}
          placeholder="🔍 Search name, alias, crime..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button className="btn btn-primary" onClick={() => setShowAdd(true)}>
          + Add Criminal
        </button>
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">
          {criminals.length === 0
            ? 'No criminals in database. Add one to begin.'
            : 'No results match your search.'}
        </div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Photo</th>
                <th>Name</th>
                <th>Alias</th>
                <th>Crime</th>
                <th>Danger</th>
                <th>Face Data</th>
                <th>Added</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c) => (
                <tr key={c.id}>
                  <td>
                    {c.photo_path ? (
                      <img
                        className="criminal-photo"
                        src={`http://localhost:8000/${c.photo_path.replace(/\\/g, '/')}`}
                        alt={c.name}
                        onError={(e) => { e.target.style.display = 'none'; }}
                      />
                    ) : (
                      <div className="criminal-photo-placeholder">👤</div>
                    )}
                  </td>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{c.name}</td>
                  <td>{c.alias || <span style={{ color: 'var(--text-muted)' }}>—</span>}</td>
                  <td>{c.crime}</td>
                  <td><span className={`badge badge-${c.danger_level}`}>{c.danger_level}</span></td>
                  <td>
                    {c.has_encoding
                      ? <span style={{ color: 'var(--accent-green)', fontSize: 12 }}>✔ Ready</span>
                      : <span style={{ color: 'var(--accent-amber)', fontSize: 12 }}>⚠ No face</span>
                    }
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)' }}>
                    {new Date(c.added_at).toLocaleDateString()}
                  </td>
                  <td>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDelete(c.id, c.name)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showAdd && (
        <AddCriminal
          onAdded={(newC) => setCriminals((prev) => [newC, ...prev])}
          onClose={() => setShowAdd(false)}
        />
      )}
    </div>
  );
}

export default CriminalList;
