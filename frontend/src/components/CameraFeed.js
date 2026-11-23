import React, { useState, useEffect, useRef } from 'react';
import { createWebSocket } from '../services/api';

function AlertBanner({ alert, onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 8000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="alert-banner">
      <div className="alert-banner-title">
        <span>⚠️</span> MATCH DETECTED
      </div>
      <div className="alert-banner-name">{alert.criminal_name}</div>
      <div className="alert-banner-detail">
        <div>Crime: {alert.crime}</div>
        <div>Confidence: <strong>{alert.confidence}%</strong></div>
        <div>Danger: <span className={`badge badge-${alert.danger_level}`}>{alert.danger_level}</span></div>
        {alert.alias && <div>Alias: {alert.alias}</div>}
      </div>
      <button className="alert-banner-close" onClick={onClose}>✕</button>
    </div>
  );
}

function CameraFeed() {
  const [frame, setFrame] = useState(null);
  const [connected, setConnected] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    const connect = () => {
      const ws = createWebSocket();
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);
      ws.onclose = () => {
        setConnected(false);
        setTimeout(connect, 3000); // reconnect after 3s
      };
      ws.onerror = () => ws.close();

      ws.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.event === 'FRAME') {
          setFrame(`data:image/jpeg;base64,${data.frame}`);
          if (data.alert) {
            setAlerts((prev) => [
              { ...data.alert, _key: Date.now() },
              ...prev.slice(0, 2),
            ]);
          }
        } else if (data.event === 'ERROR') {
          console.error('[WS]', data.message);
        }
      };
    };
    connect();
    return () => wsRef.current?.close();
  }, []);

  const removeAlert = (key) =>
    setAlerts((prev) => prev.filter((a) => a._key !== key));

  return (
    <>
      <div className="camera-feed">
        {frame ? (
          <img src={frame} alt="Live camera feed" />
        ) : (
          <div className="no-camera">
            <span style={{ fontSize: 48 }}>📷</span>
            <span>{connected ? 'Waiting for frames...' : 'Connecting to camera...'}</span>
          </div>
        )}
        <div className={`camera-status-badge ${connected ? 'live' : 'offline'}`}>
          <span className={`status-dot ${connected ? 'online' : 'offline'}`} />
          {connected ? 'LIVE' : 'OFFLINE'}
        </div>
      </div>
      {alerts.map((a) => (
        <AlertBanner key={a._key} alert={a} onClose={() => removeAlert(a._key)} />
      ))}
    </>
  );
}

export default CameraFeed;
