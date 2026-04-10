import { useState, useEffect } from 'react';
import { WifiOff, Radio } from 'lucide-react';

const API_URL = 'http://localhost:5000';
const CAM_IDS = ['cam1', 'cam2', 'cam3', 'cam4'];

export default function LiveMonitor() {
  const [cameras, setCameras] = useState({});

  // Poll camera statuses
  useEffect(() => {
    const poll = async () => {
      try {
        const res = await fetch(`${API_URL}/api/cameras`);
        const data = await res.json();
        const map = {};
        data.forEach(c => { map[c.cam_id] = c; });
        setCameras(map);
      } catch (e) {}
    };
    poll();
    const interval = setInterval(poll, 3000);
    return () => clearInterval(interval);
  }, []);

  const activeCams = CAM_IDS.filter(id => cameras[id]?.connected);

  // Grid layout based on active camera count
  const getGridStyle = () => {
    const count = activeCams.length;
    if (count <= 1) return { gridTemplateColumns: '1fr', gridTemplateRows: '1fr' };
    if (count === 2) return { gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr' };
    return { gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr 1fr' };
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', animation: 'fadeIn 0.4s ease' }}>
      <div className="top-bar">
        <div>
          <h1>Live Monitoring</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
            {activeCams.length} of 4 cameras active
          </p>
        </div>
        <div className="status-pill online">
          <span className="pulse-dot"></span>
          {activeCams.length} STREAMS
        </div>
      </div>

      <div style={{ display: 'flex', gap: '16px', flex: 1, minHeight: 0 }}>
        {/* ── Camera Grid ── */}
        <div style={{
          flex: 1, display: 'grid', gap: '10px', minHeight: 0,
          ...getGridStyle(),
        }}>
          {activeCams.length > 0 ? (
            activeCams.map(camId => {
              const cam = cameras[camId];
              const num = camId.replace('cam', '');
              return (
                <div key={camId} className="card" style={{
                  padding: '0', overflow: 'hidden', display: 'flex', flexDirection: 'column',
                  border: cam?.detecting ? '1px solid rgba(16,185,129,0.15)' : '1px solid var(--glass-border)',
                }}>
                  {/* Camera label bar */}
                  <div style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '8px 12px', borderBottom: '1px solid var(--glass-border)',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Radio size={12} color={cam?.detecting ? '#10b981' : '#64748b'} />
                      <span style={{ fontSize: '0.78rem', fontWeight: 600 }}>Camera {num}</span>
                    </div>
                    <span style={{
                      fontSize: '0.65rem', fontWeight: 600, textTransform: 'uppercase',
                      color: cam?.detecting ? '#10b981' : '#f59e0b',
                    }}>
                      {cam?.detecting ? 'AI Active' : 'Paused'}
                    </span>
                  </div>
                  {/* Video */}
                  <div style={{ flex: 1, background: '#000', position: 'relative' }}>
                    <img
                      src={`${API_URL}/video_feed/${camId}?t=${Date.now()}`}
                      alt={`Camera ${num}`}
                      style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block' }}
                      onError={e => {
                        e.target.style.display = 'none';
                      }}
                    />
                  </div>
                </div>
              );
            })
          ) : (
            <div className="card" style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              height: '100%', flexDirection: 'column', gap: '20px',
              background: 'radial-gradient(ellipse at center, rgba(99,102,241,0.03) 0%, transparent 70%)',
              gridColumn: '1 / -1', gridRow: '1 / -1',
            }}>
              <div style={{
                background: 'linear-gradient(135deg, rgba(99,102,241,0.1), rgba(167,139,250,0.05))',
                padding: '24px', borderRadius: '20px', border: '1px solid rgba(99,102,241,0.1)',
              }}>
                <WifiOff size={40} color="#6366f1" opacity={0.5} />
              </div>
              <div style={{ textAlign: 'center' }}>
                <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '8px' }}>
                  No Cameras Active
                </h2>
                <p style={{ maxWidth: '380px', fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
                  Please go to the <strong>Camera Setup</strong> page to connect and configure your video sources.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
