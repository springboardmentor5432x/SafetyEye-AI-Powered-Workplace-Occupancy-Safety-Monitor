import { Outlet, NavLink } from 'react-router-dom';
import { Shield, Activity, BarChart2, Database, Settings, Zap, LogOut, User, Brain, Video } from 'lucide-react';

export default function Layout({ user, onLogout }) {
  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo-container">
          <div style={{ 
            background: 'linear-gradient(135deg, #6366f1, #a78bfa)', 
            padding: '8px', 
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)'
          }}>
            <Shield size={22} color="white" />
          </div>
          <div>
            <span className="logo-text">SafetyEye</span>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 500, letterSpacing: '0.08em', textTransform: 'uppercase', marginTop: '2px' }}>
              AI Monitoring v2.0
            </div>
          </div>
        </div>
        
        <div style={{ fontSize: '0.65rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', padding: '0 1rem', marginBottom: '0.5rem' }}>
          Navigation
        </div>
        
        <nav className="sidebar-nav">
          <NavLink to="/" className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')} end>
            <BarChart2 size={18} />
            <span>Dashboard</span>
          </NavLink>
          
          <NavLink to="/cameras" className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}>
            <Video size={18} />
            <span>Camera Setup</span>
          </NavLink>

          <NavLink to="/monitor" className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}>
            <Activity size={18} />
            <span>Live Monitor</span>
          </NavLink>
          
          <NavLink to="/logs" className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}>
            <Database size={18} />
            <span>Incident Logs</span>
          </NavLink>
          
          <NavLink to="/model" className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}>
            <Brain size={18} />
            <span>AI Model</span>
          </NavLink>
          
          <NavLink to="/settings" className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}>
            <Settings size={18} />
            <span>Settings</span>
          </NavLink>
        </nav>

        {/* Engine Info */}
        <div style={{ 
          marginTop: 'auto',
          padding: '1rem',
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(167, 139, 250, 0.05))',
          borderRadius: '0.75rem',
          border: '1px solid rgba(99, 102, 241, 0.1)',
          marginBottom: '0.75rem',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <Zap size={14} color="#a78bfa" />
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-main)' }}>YOLOv8s Engine</span>
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            ByteTrack • Real-Time
          </div>
        </div>

        {/* User Profile & Logout */}
        <div style={{ 
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0.75rem 1rem',
          background: 'rgba(255,255,255,0.02)',
          borderRadius: '0.75rem',
          border: '1px solid var(--glass-border)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
            <div style={{
              width: '32px', height: '32px', borderRadius: '8px',
              background: 'linear-gradient(135deg, #6366f1, #a78bfa)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}>
              <User size={15} color="white" />
            </div>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {user?.name || 'User'}
              </div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {user?.role || 'viewer'}
              </div>
            </div>
          </div>
          <button 
            onClick={onLogout}
            title="Sign out"
            style={{
              background: 'none', border: 'none', cursor: 'pointer', color: '#64748b',
              padding: '6px', borderRadius: '6px', display: 'flex',
              transition: 'color 0.2s, background 0.2s',
            }}
            onMouseEnter={e => { e.currentTarget.style.color = '#f43f5e'; e.currentTarget.style.background = 'rgba(244,63,94,0.1)'; }}
            onMouseLeave={e => { e.currentTarget.style.color = '#64748b'; e.currentTarget.style.background = 'none'; }}
          >
            <LogOut size={16} />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
