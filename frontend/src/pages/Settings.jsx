import { useState, useEffect } from 'react';
import { Sliders, Sun, Moon, Volume2, VolumeX, Trash2, Cpu, HardDrive, Activity, Gauge, Zap, Fingerprint, ServerCrash, UserPlus, Users, Shield, X, Mail, Lock, User } from 'lucide-react';

const API_URL = 'http://localhost:5000';

export default function Settings({ theme, setTheme, user, authToken }) {
  const [confidence, setConfidence] = useState(0.4);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [diagnostics, setDiagnostics] = useState({ model: 'Loading...', db_size: '...', server: '...' });
  const [isSaving, setIsSaving] = useState(false);

  // User management state
  const [userList, setUserList] = useState([]);
  const [showAddUser, setShowAddUser] = useState(false);
  const [newUser, setNewUser] = useState({ name: '', email: '', password: '', role: 'viewer' });
  const [userError, setUserError] = useState('');

  const isAdmin = user?.role === 'admin';
  const authHeaders = { 'Authorization': `Bearer ${authToken}`, 'Content-Type': 'application/json' };

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const [settingsRes, statusRes] = await Promise.all([
          fetch(`${API_URL}/api/settings`),
          fetch(`${API_URL}/api/status`)
        ]);
        const settings = await settingsRes.json();
        const status = await statusRes.json();
        setConfidence(settings.confidence);
        setAudioEnabled(settings.audio_alerts);
        setDiagnostics(status.diagnostics || diagnostics);
      } catch (err) {
        console.error("Failed to load settings.");
      }
    };
    loadSettings();
    if (isAdmin) loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const res = await fetch(`${API_URL}/api/users`, { headers: authHeaders });
      if (res.ok) setUserList(await res.json());
    } catch (e) {}
  };

  const saveSettings = async (newConf, newAudio) => {
    setIsSaving(true);
    try {
      await fetch(`${API_URL}/api/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confidence: newConf, audio_alerts: newAudio })
      });
    } catch (err) { console.error(err); }
    setTimeout(() => setIsSaving(false), 500);
  };

  const handleConfidenceChange = (e) => {
    const val = parseFloat(e.target.value);
    setConfidence(val);
    saveSettings(val, audioEnabled);
  };

  const toggleAudio = () => {
    const newVal = !audioEnabled;
    setAudioEnabled(newVal);
    saveSettings(confidence, newVal);
  };

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const handleClearLogs = async () => {
    if (window.confirm("⚠️ This will permanently delete ALL violation logs and photographic evidence. Proceed?")) {
      try {
        await fetch(`${API_URL}/api/logs`, { method: 'DELETE' });
        alert("✅ Database wiped successfully.");
      } catch (e) {
        alert("Failed to clear logs.");
      }
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    setUserError('');
    if (!newUser.name || !newUser.email || !newUser.password) {
      setUserError('All fields are required');
      return;
    }
    try {
      const res = await fetch(`${API_URL}/api/users`, {
        method: 'POST',
        headers: authHeaders,
        body: JSON.stringify(newUser),
      });
      const data = await res.json();
      if (res.ok) {
        setShowAddUser(false);
        setNewUser({ name: '', email: '', password: '', role: 'viewer' });
        loadUsers();
      } else {
        setUserError(data.error || 'Failed to create user');
      }
    } catch (e) {
      setUserError('Failed to reach server');
    }
  };

  const handleDeleteUser = async (userId, userName) => {
    if (window.confirm(`Remove "${userName}" from the system? They will no longer be able to log in.`)) {
      try {
        const res = await fetch(`${API_URL}/api/users/${userId}`, {
          method: 'DELETE',
          headers: authHeaders,
        });
        const data = await res.json();
        if (res.ok) {
          loadUsers();
        } else {
          alert(data.error || 'Failed to delete user');
        }
      } catch (e) {
        alert('Failed to reach server');
      }
    }
  };

  const confPercent = Math.round(confidence * 100);
  const confColor = confPercent > 70 ? '#10b981' : confPercent > 40 ? '#f59e0b' : '#f43f5e';

  return (
    <div style={{ maxWidth: '1060px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '20px', animation: 'fadeIn 0.4s ease' }}>
      <div className="top-bar" style={{ marginBottom: '0' }}>
        <div>
          <h1>System Configuration</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
            Tune AI parameters and manage preferences
          </p>
        </div>
        {isSaving && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: '#10b981' }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981', animation: 'pulse-dot 1s ease infinite' }} />
            Saved
          </div>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* AI Confidence */}
        <div className="card">
          <div className="card-header">
            <div className="card-title" style={{ color: 'var(--accent)' }}>
              <Gauge size={18} /> AI Confidence Threshold
            </div>
          </div>
          <p style={{ color: 'var(--text-muted)', marginBottom: '20px', fontSize: '0.85rem', lineHeight: '1.5' }}>
            Control how certain YOLOv8 must be before flagging a violation. Higher = more strict, fewer false alarms.
          </p>
          <div style={{ background: 'rgba(99,102,241,0.04)', padding: '20px', borderRadius: '12px', border: '1px solid rgba(99,102,241,0.1)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>Threshold</span>
              <div style={{ background: `${confColor}18`, color: confColor, padding: '4px 14px', borderRadius: '999px', fontWeight: 800, fontSize: '0.9rem', border: `1px solid ${confColor}30` }}>
                {confPercent}%
              </div>
            </div>
            <input type="range" min="0.1" max="0.9" step="0.05" value={confidence} onChange={handleConfidenceChange}
              style={{ width: '100%', cursor: 'pointer', accentColor: 'var(--accent)', height: '4px' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              <span>🔓 Loose</span>
              <span>🔒 Strict</span>
            </div>
          </div>
        </div>

        {/* Preferences */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><Zap size={18} color="#a78bfa" /> Interface Preferences</div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 16px', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', border: '1px solid var(--glass-border)' }}>
              <div>
                <strong style={{ display: 'block', marginBottom: '3px', fontSize: '0.9rem' }}>Audio Alerts</strong>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Play warning beep on violations</span>
              </div>
              <button onClick={toggleAudio} style={{ display: 'flex', alignItems: 'center', gap: '7px', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: 600, fontSize: '0.8rem', background: audioEnabled ? 'rgba(16, 185, 129, 0.12)' : 'rgba(244, 63, 94, 0.12)', color: audioEnabled ? '#34d399' : '#fb7185', border: `1px solid ${audioEnabled ? 'rgba(16,185,129,0.2)' : 'rgba(244,63,94,0.2)'}`, transition: 'all 0.25s' }}>
                {audioEnabled ? <><Volume2 size={15} /> ON</> : <><VolumeX size={15} /> OFF</>}
              </button>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 16px', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', border: '1px solid var(--glass-border)' }}>
              <div>
                <strong style={{ display: 'block', marginBottom: '3px', fontSize: '0.9rem' }}>Appearance</strong>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Toggle between dark and light mode</span>
              </div>
              <button onClick={toggleTheme} style={{ display: 'flex', alignItems: 'center', gap: '7px', padding: '8px 16px', borderRadius: '8px', border: '1px solid var(--glass-border)', cursor: 'pointer', fontWeight: 600, fontSize: '0.8rem', background: 'rgba(255,255,255,0.03)', color: 'var(--text-main)', transition: 'all 0.25s' }}>
                {theme === 'dark' ? <><Sun size={15} color="#fbbf24" /> Light</> : <><Moon size={15} color="#6366f1" /> Dark</>}
              </button>
            </div>
          </div>
        </div>

        {/* System Diagnostics */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><Fingerprint size={18} color="var(--text-muted)" /> System Diagnostics</div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
            {[
              { icon: <Cpu size={17} />, label: 'AI Engine', value: `${diagnostics.model} (Custom Trained)`, color: '#a78bfa' },
              { icon: <HardDrive size={17} />, label: 'Database Size', value: diagnostics.db_size, color: '#6366f1' },
              { icon: <Activity size={17} />, label: 'Server Bind', value: diagnostics.server, color: '#10b981' },
            ].map((item, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '13px 4px', borderBottom: i < 2 ? '1px solid var(--glass-border)' : 'none' }}>
                <div style={{ color: item.color, opacity: 0.7 }}>{item.icon}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '2px' }}>{item.label}</div>
                  <div style={{ fontWeight: 500, fontSize: '0.88rem' }}>{item.value}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Danger Zone */}
        <div className="card" style={{ border: '1px solid rgba(244, 63, 94, 0.15)' }}>
          <div className="card-header">
            <div className="card-title" style={{ color: '#f43f5e' }}><ServerCrash size={18} /> Danger Zone</div>
          </div>
          <p style={{ color: 'var(--text-muted)', marginBottom: '20px', fontSize: '0.85rem', lineHeight: '1.5' }}>
            Permanently delete all SQLite violation logs and photographic evidence from disk.
          </p>
          <button onClick={handleClearLogs} className="btn-danger" style={{ width: '100%', justifyContent: 'center', padding: '12px' }}>
            <Trash2 size={16} /> Purge All Data
          </button>
        </div>
      </div>

      {/* ───── User Management (Admin Only) ───── */}
      {isAdmin && (
        <div className="card" style={{ border: '1px solid rgba(99, 102, 241, 0.15)', marginTop: '4px' }}>
          <div className="card-header">
            <div className="card-title" style={{ color: 'var(--accent)' }}>
              <Users size={18} /> Access Control — User Management
            </div>
            <button onClick={() => { setShowAddUser(!showAddUser); setUserError(''); }}
              className="btn-primary" style={{ padding: '7px 14px', fontSize: '0.8rem' }}>
              <UserPlus size={14} /> Add User
            </button>
          </div>

          {/* Add User Form */}
          {showAddUser && (
            <div style={{
              background: 'rgba(99,102,241,0.04)', borderRadius: '12px', padding: '20px',
              border: '1px solid rgba(99,102,241,0.1)', marginBottom: '20px',
              animation: 'fadeIn 0.3s ease',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 600 }}>Register New User</h4>
                <button onClick={() => setShowAddUser(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                  <X size={16} />
                </button>
              </div>

              {userError && (
                <div style={{ background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.2)', borderRadius: '8px', padding: '8px 12px', marginBottom: '14px', color: '#fb7185', fontSize: '0.8rem', fontWeight: 500 }}>
                  {userError}
                </div>
              )}

              <form onSubmit={handleAddUser}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                  <div>
                    <label style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: '5px' }}>Full Name</label>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--glass-border)', borderRadius: '8px', padding: '0 12px' }}>
                      <User size={14} color="#64748b" />
                      <input type="text" value={newUser.name} onChange={e => setNewUser({...newUser, name: e.target.value})} placeholder="John Doe"
                        style={{ background: 'transparent', border: 'none', color: 'var(--text-main)', padding: '10px 0', width: '100%', outline: 'none', fontSize: '0.85rem' }} />
                    </div>
                  </div>
                  <div>
                    <label style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: '5px' }}>Email</label>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--glass-border)', borderRadius: '8px', padding: '0 12px' }}>
                      <Mail size={14} color="#64748b" />
                      <input type="email" value={newUser.email} onChange={e => setNewUser({...newUser, email: e.target.value})} placeholder="user@company.com"
                        style={{ background: 'transparent', border: 'none', color: 'var(--text-main)', padding: '10px 0', width: '100%', outline: 'none', fontSize: '0.85rem' }} />
                    </div>
                  </div>
                  <div>
                    <label style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: '5px' }}>Password</label>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--glass-border)', borderRadius: '8px', padding: '0 12px' }}>
                      <Lock size={14} color="#64748b" />
                      <input type="password" value={newUser.password} onChange={e => setNewUser({...newUser, password: e.target.value})} placeholder="••••••"
                        style={{ background: 'transparent', border: 'none', color: 'var(--text-main)', padding: '10px 0', width: '100%', outline: 'none', fontSize: '0.85rem' }} />
                    </div>
                  </div>
                  <div>
                    <label style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: '5px' }}>Role</label>
                    <select value={newUser.role} onChange={e => setNewUser({...newUser, role: e.target.value})}
                      style={{ width: '100%', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--glass-border)', borderRadius: '8px', padding: '10px 12px', color: 'var(--text-main)', outline: 'none', fontSize: '0.85rem', cursor: 'pointer' }}>
                      <option value="viewer" style={{ background: '#0f172a' }}>Viewer (Read Only)</option>
                      <option value="admin" style={{ background: '#0f172a' }}>Admin (Full Access)</option>
                    </select>
                  </div>
                </div>
                <button type="submit" className="btn-primary" style={{ padding: '10px 20px' }}>
                  <UserPlus size={15} /> Create Account
                </button>
              </form>
            </div>
          )}

          {/* Users List */}
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 4px', textAlign: 'left' }}>
              <thead>
                <tr style={{ color: 'var(--text-muted)' }}>
                  <th style={{ padding: '8px 12px', fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>User</th>
                  <th style={{ padding: '8px 12px', fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Email</th>
                  <th style={{ padding: '8px 12px', fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Role</th>
                  <th style={{ padding: '8px 12px', fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Joined</th>
                  <th style={{ padding: '8px 12px', fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {userList.map(u => (
                  <tr key={u.id} style={{ background: 'rgba(255,255,255,0.015)' }}>
                    <td style={{ padding: '10px 12px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <div style={{ width: '30px', height: '30px', borderRadius: '8px', background: u.role === 'admin' ? 'linear-gradient(135deg, #6366f1, #a78bfa)' : 'linear-gradient(135deg, #334155, #475569)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          {u.role === 'admin' ? <Shield size={13} color="white" /> : <User size={13} color="white" />}
                        </div>
                        <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{u.name}</span>
                      </div>
                    </td>
                    <td style={{ padding: '10px 12px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>{u.email}</td>
                    <td style={{ padding: '10px 12px' }}>
                      <span style={{
                        padding: '3px 10px', borderRadius: '999px', fontSize: '0.72rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em',
                        background: u.role === 'admin' ? 'rgba(99,102,241,0.12)' : 'rgba(148,163,184,0.1)',
                        color: u.role === 'admin' ? '#a5b4fc' : '#94a3b8',
                        border: `1px solid ${u.role === 'admin' ? 'rgba(99,102,241,0.2)' : 'rgba(148,163,184,0.15)'}`,
                      }}>
                        {u.role}
                      </span>
                    </td>
                    <td style={{ padding: '10px 12px', fontSize: '0.8rem', color: 'var(--text-muted)', fontVariantNumeric: 'tabular-nums' }}>
                      {u.created_at?.split(' ')[0] || '—'}
                    </td>
                    <td style={{ padding: '10px 12px' }}>
                      {u.id !== user?.id ? (
                        <button onClick={() => handleDeleteUser(u.id, u.name)}
                          className="btn-ghost" style={{ padding: '5px 10px', fontSize: '0.75rem', color: '#f43f5e' }}>
                          <Trash2 size={13} /> Remove
                        </button>
                      ) : (
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>You</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
