import { useState, useEffect } from 'react';
import { Video, RefreshCw, Play, Square, X, Wifi, WifiOff, Radio } from 'lucide-react';

const API_URL = 'http://localhost:5000';
const CAM_IDS = ['cam1', 'cam2', 'cam3', 'cam4'];

export default function CameraSetup() {
  const [cameras, setCameras] = useState({});
  const [sourceInputs, setSourceInputs] = useState({ cam1: '', cam2: '', cam3: '', cam4: '' });
  const [loadingCam, setLoadingCam] = useState(null);
  const [streamKeys, setStreamKeys] = useState({ cam1: 0, cam2: 0, cam3: 0, cam4: 0 });

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
  const detectingCams = CAM_IDS.filter(id => cameras[id]?.detecting);

  const handleConnect = async (camId) => {
    const source = sourceInputs[camId];
    if (!source) return;
    setLoadingCam(camId);
    try {
      const res = await fetch(`${API_URL}/api/set_source`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cam_id: camId, source }),
      });
      if (res.ok) {
        setStreamKeys(prev => ({ ...prev, [camId]: Date.now() }));
      } else {
        const data = await res.json();
        alert(data.message || 'Failed to connect');
      }
    } catch (e) { alert('Cannot reach backend'); }
    setLoadingCam(null);
  };

  const handleDisconnect = async (camId) => {
    try {
      await fetch(`${API_URL}/api/cameras/${camId}/disconnect`, { method: 'POST' });
    } catch (e) {}
  };

  const handleToggle = async (camId, state) => {
    try {
      await fetch(`${API_URL}/api/toggle_detection`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cam_id: camId, state }),
      });
    } catch (e) {}
  };

  return (
    <div style={{ animation: 'fadeIn 0.4s ease' }}>
      <div className="top-bar">
        <div>
          <h1>Camera Setup</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
            Connect and configure up to 4 video sources
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '2px' }}>Connected</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: activeCams.length > 0 ? '#10b981' : '#64748b' }}>{activeCams.length} / 4</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '2px' }}>Detecting</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: detectingCams.length > 0 ? '#a78bfa' : '#64748b' }}>{detectingCams.length} / 4</div>
          </div>
        </div>
      </div>

      {/* Info Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(99,102,241,0.08), rgba(167,139,250,0.04))',
        border: '1px solid rgba(99,102,241,0.12)', borderRadius: '12px',
        padding: '14px 18px', marginBottom: '1.5rem',
        display: 'flex', alignItems: 'center', gap: '12px',
        fontSize: '0.83rem', color: 'var(--text-muted)', lineHeight: '1.5',
      }}>
        <Radio size={18} color="#6366f1" style={{ flexShrink: 0 }} />
        <span>
          Enter <code style={{ background: 'rgba(99,102,241,0.12)', color: '#a78bfa', padding: '1px 7px', borderRadius: '5px' }}>0</code> for webcam,
          a <strong style={{ color: 'var(--text-main)' }}>file path</strong> (e.g. <code style={{ background: 'rgba(99,102,241,0.12)', color: '#a78bfa', padding: '1px 7px', borderRadius: '5px' }}>C:\videos\site.mp4</code>), or an
          <strong style={{ color: 'var(--text-main)' }}> IP camera URL</strong> (e.g. <code style={{ background: 'rgba(99,102,241,0.12)', color: '#a78bfa', padding: '1px 7px', borderRadius: '5px' }}>http://192.168.1.x:8080/video</code>).
          Then go to <strong style={{ color: 'var(--text-main)' }}>Live Monitor</strong> to view the streams.
        </span>
      </div>

      {/* Camera Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }} className="charts-grid">
        {CAM_IDS.map((camId, idx) => {
          const cam = cameras[camId];
          const connected = cam?.connected;
          const detecting = cam?.detecting;
          const num = camId.replace('cam', '');

          return (
            <div key={camId} className="card" style={{
              border: detecting
                ? '1px solid rgba(16,185,129,0.25)'
                : connected
                  ? '1px solid rgba(99,102,241,0.2)'
                  : '1px solid var(--glass-border)',
              transition: 'border-color 0.3s',
              animationDelay: `${idx * 0.08}s`,
            }}>
              {/* Card Header */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{
                    width: '36px', height: '36px', borderRadius: '10px', display: 'flex',
                    alignItems: 'center', justifyContent: 'center',
                    background: detecting
                      ? 'rgba(16,185,129,0.12)'
                      : connected
                        ? 'rgba(99,102,241,0.12)'
                        : 'rgba(255,255,255,0.03)',
                    border: `1px solid ${detecting ? 'rgba(16,185,129,0.2)' : connected ? 'rgba(99,102,241,0.15)' : 'var(--glass-border)'}`,
                  }}>
                    <Video size={16} color={detecting ? '#10b981' : connected ? '#6366f1' : '#64748b'} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>Camera {num}</div>
                    <div style={{ fontSize: '0.7rem', color: detecting ? '#10b981' : connected ? '#a78bfa' : '#64748b', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      {detecting ? '● AI Active' : connected ? '● Connected' : '○ Not connected'}
                    </div>
                  </div>
                </div>
                {connected && (
                  <button onClick={() => handleDisconnect(camId)} title="Disconnect"
                    style={{ background: 'rgba(244,63,94,0.08)', border: '1px solid rgba(244,63,94,0.15)', borderRadius: '8px', cursor: 'pointer', color: '#fb7185', padding: '6px 10px', fontSize: '0.75rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '5px' }}
                    onMouseEnter={e => e.currentTarget.style.background = 'rgba(244,63,94,0.15)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'rgba(244,63,94,0.08)'}>
                    <X size={13} /> Disconnect
                  </button>
                )}
              </div>

              {/* Source Display if connected */}
              {connected && cam?.source && (
                <div style={{
                  background: 'rgba(255,255,255,0.02)', border: '1px solid var(--glass-border)',
                  borderRadius: '8px', padding: '8px 12px', marginBottom: '14px',
                  fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace',
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                }}>
                  📹 {cam.source}
                </div>
              )}

              {/* URL Input (only when not connected) */}
              {!connected && (
                <div style={{ marginBottom: '14px' }}>
                  <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '6px' }}>
                    Source URL / Path
                  </label>
                  <div style={{
                    display: 'flex', gap: '8px',
                  }}>
                    <div style={{
                      display: 'flex', alignItems: 'center', gap: '8px', flex: 1,
                      background: 'rgba(255,255,255,0.02)', border: '1px solid var(--glass-border)',
                      borderRadius: '10px', padding: '0 14px',
                    }}>
                      <Video size={14} color="#64748b" />
                      <input
                        type="text"
                        placeholder="0, /path/to/video.mp4, or http://..."
                        value={sourceInputs[camId]}
                        onChange={e => setSourceInputs(prev => ({ ...prev, [camId]: e.target.value }))}
                        onKeyDown={e => e.key === 'Enter' && handleConnect(camId)}
                        style={{
                          background: 'transparent', border: 'none', color: 'var(--text-main)',
                          padding: '11px 0', width: '100%', outline: 'none', fontSize: '0.85rem',
                        }}
                      />
                    </div>
                    <button onClick={() => handleConnect(camId)} disabled={loadingCam === camId || !sourceInputs[camId]}
                      className="btn-primary" style={{ padding: '11px 18px', whiteSpace: 'nowrap' }}>
                      {loadingCam === camId
                        ? <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><RefreshCw size={13} className="spin" /> Connecting...</span>
                        : 'Connect'}
                    </button>
                  </div>
                </div>
              )}

              {/* Detection Controls (only when connected) */}
              {connected && (
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button onClick={() => handleToggle(camId, true)} disabled={detecting}
                    style={{
                      flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
                      padding: '10px', borderRadius: '10px', border: 'none', fontSize: '0.83rem', fontWeight: 600,
                      background: detecting ? 'rgba(255,255,255,0.03)' : 'linear-gradient(135deg, #10b981, #34d399)',
                      color: detecting ? '#475569' : 'white',
                      cursor: detecting ? 'not-allowed' : 'pointer',
                      boxShadow: detecting ? 'none' : '0 4px 12px rgba(16,185,129,0.25)',
                    }}>
                    <Play size={14} fill={detecting ? 'none' : 'white'} /> Start Detection
                  </button>
                  <button onClick={() => handleToggle(camId, false)} disabled={!detecting}
                    style={{
                      flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
                      padding: '10px', borderRadius: '10px', border: 'none', fontSize: '0.83rem', fontWeight: 600,
                      background: !detecting ? 'rgba(255,255,255,0.03)' : 'linear-gradient(135deg, #f43f5e, #fb7185)',
                      color: !detecting ? '#475569' : 'white',
                      cursor: !detecting ? 'not-allowed' : 'pointer',
                      boxShadow: !detecting ? 'none' : '0 4px 12px rgba(244,63,94,0.25)',
                    }}>
                    <Square size={14} fill={!detecting ? 'none' : 'white'} /> Stop Detection
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
