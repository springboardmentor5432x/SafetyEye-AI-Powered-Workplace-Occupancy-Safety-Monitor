import { useState, useEffect } from 'react';
import { AlertTriangle, X, ShieldAlert, Eye } from 'lucide-react';

const TOAST_DURATION = 6000;

export default function ToastContainer({ toasts, removeToast }) {
  return (
    <div style={{
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column-reverse',
      gap: '10px',
      maxWidth: '400px',
    }}>
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
      ))}
    </div>
  );
}

function Toast({ toast, onClose }) {
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsExiting(true);
      setTimeout(onClose, 300);
    }, TOAST_DURATION);
    return () => clearTimeout(timer);
  }, []);

  const getIcon = (type) => {
    if (type?.includes('Hardhat')) return '🪖';
    if (type?.includes('Vest')) return '🦺';
    if (type?.includes('Mask')) return '😷';
    return '⚠️';
  };

  const getAccentColor = (type) => {
    if (type?.includes('Hardhat')) return '#f59e0b';
    if (type?.includes('Vest')) return '#f43f5e';
    if (type?.includes('Mask')) return '#6366f1';
    return '#f43f5e';
  };

  const accentColor = getAccentColor(toast.violation_type);

  return (
    <div style={{
      background: 'rgba(15, 23, 42, 0.95)',
      backdropFilter: 'blur(20px)',
      borderRadius: '14px',
      border: `1px solid ${accentColor}30`,
      boxShadow: `0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.03), inset 0 1px 0 rgba(255,255,255,0.05)`,
      padding: '14px 16px',
      display: 'flex',
      alignItems: 'flex-start',
      gap: '12px',
      animation: isExiting 
        ? 'toastSlideOut 0.3s cubic-bezier(0.4, 0, 1, 1) forwards' 
        : 'toastSlideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards',
      borderLeft: `3px solid ${accentColor}`,
      minWidth: '340px',
    }}>
      {/* Icon */}
      <div style={{
        background: `${accentColor}15`,
        borderRadius: '10px',
        width: '40px',
        height: '40px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '1.3rem',
        flexShrink: 0,
      }}>
        {getIcon(toast.violation_type)}
      </div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
          <ShieldAlert size={13} color={accentColor} />
          <span style={{ fontSize: '0.72rem', fontWeight: 700, color: accentColor, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Safety Alert
          </span>
        </div>
        <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#e2e8f0', marginBottom: '3px' }}>
          {toast.violation_type}
        </div>
        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
          Person #{toast.track_id} • {toast.timestamp?.split(' ')[1] || 'Just now'}
        </div>
      </div>

      {/* Close */}
      <button 
        onClick={() => { setIsExiting(true); setTimeout(onClose, 300); }}
        style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#475569', padding: '4px', borderRadius: '6px', display: 'flex', transition: 'color 0.2s' }}
        onMouseEnter={e => e.currentTarget.style.color = '#94a3b8'}
        onMouseLeave={e => e.currentTarget.style.color = '#475569'}
      >
        <X size={15} />
      </button>

      {/* Progress bar */}
      <div style={{
        position: 'absolute',
        bottom: '0',
        left: '3px',
        right: '0',
        height: '2px',
        borderRadius: '0 0 14px 14px',
        overflow: 'hidden',
      }}>
        <div style={{
          height: '100%',
          background: `linear-gradient(90deg, ${accentColor}, ${accentColor}60)`,
          animation: `toastProgress ${TOAST_DURATION}ms linear forwards`,
        }} />
      </div>

      <style>{`
        @keyframes toastSlideIn {
          from { opacity: 0; transform: translateX(100px) scale(0.95); }
          to { opacity: 1; transform: translateX(0) scale(1); }
        }
        @keyframes toastSlideOut {
          from { opacity: 1; transform: translateX(0) scale(1); }
          to { opacity: 0; transform: translateX(100px) scale(0.95); }
        }
        @keyframes toastProgress {
          from { width: 100%; }
          to { width: 0%; }
        }
      `}</style>
    </div>
  );
}
