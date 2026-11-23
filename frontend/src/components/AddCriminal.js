import React, { useState } from 'react';
import { addCriminal } from '../services/api';

const INITIAL = {
  name: '', alias: '', crime: '', danger_level: 'medium',
  nationality: '', age: '', description: '',
};

function AddCriminal({ onAdded, onClose }) {
  const [form, setForm] = useState(INITIAL);
  const [photo, setPhoto] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handlePhoto = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setPhoto(file);
    setPreview(URL.createObjectURL(file));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!form.name || !form.crime) {
      setError('Name and Crime are required.');
      return;
    }
    setLoading(true);
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => { if (v) fd.append(k, v); });
      if (photo) fd.append('photo', photo);
      const res = await addCriminal(fd);
      onAdded(res.data);
      setForm(INITIAL);
      setPhoto(null);
      setPreview(null);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error adding criminal.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <div className="modal-header">
          <div className="modal-title">Add Criminal to Database</div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 18 }}
          >✕</button>
        </div>

        {error && (
          <div style={{ background: 'rgba(220,38,38,0.1)', border: '1px solid #dc2626', borderRadius: 6, padding: '8px 12px', marginBottom: 14, fontSize: 13, color: '#ef4444' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Full Name *</label>
              <input className="form-input" name="name" value={form.name} onChange={handleChange} placeholder="John Doe" />
            </div>
            <div className="form-group">
              <label className="form-label">Alias / Nickname</label>
              <input className="form-input" name="alias" value={form.alias} onChange={handleChange} placeholder="Scarface" />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Crime(s) *</label>
            <input className="form-input" name="crime" value={form.crime} onChange={handleChange} placeholder="Armed robbery, murder..." />
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Danger Level</label>
              <select className="form-select" name="danger_level" value={form.danger_level} onChange={handleChange}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Age</label>
              <input className="form-input" type="number" name="age" value={form.age} onChange={handleChange} placeholder="35" min="1" max="120" />
            </div>
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Nationality</label>
              <input className="form-input" name="nationality" value={form.nationality} onChange={handleChange} placeholder="American" />
            </div>
            <div className="form-group">
              <label className="form-label">Photo</label>
              <input type="file" accept="image/*" onChange={handlePhoto} style={{ color: 'var(--text-secondary)', fontSize: 12 }} />
            </div>
          </div>

          {preview && (
            <div style={{ marginBottom: 14 }}>
              <img src={preview} alt="Preview" style={{ width: 80, height: 80, objectFit: 'cover', borderRadius: 6, border: '1px solid var(--border)' }} />
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea className="form-textarea" name="description" value={form.description} onChange={handleChange} placeholder="Additional notes..." />
          </div>

          <div className="flex-row" style={{ justifyContent: 'flex-end', gap: 8 }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Adding...' : '+ Add Criminal'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddCriminal;
