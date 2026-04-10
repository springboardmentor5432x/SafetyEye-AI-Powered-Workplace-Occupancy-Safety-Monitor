import { useState } from 'react';
import { Shield, Mail, Lock, ArrowRight, AlertCircle, Eye, EyeOff } from 'lucide-react';

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      const res = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      
      const data = await res.json();
      
      if (res.ok) {
        onLogin(data.token, data.user);
      } else {
        setError(data.error || 'Authentication failed');
      }
    } catch (err) {
      setError('Cannot reach the backend server');
    }
    setIsLoading(false);
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#080c14',
      backgroundImage: `
        radial-gradient(ellipse at 30% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 70% 80%, rgba(244, 63, 94, 0.05) 0%, transparent 50%)
      `,
      padding: '20px',
    }}>
      <div style={{
        width: '100%',
        maxWidth: '420px',
        animation: 'fadeIn 0.6s ease',
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '64px',
            height: '64px',
            borderRadius: '18px',
            background: 'linear-gradient(135deg, #6366f1, #a78bfa)',
            boxShadow: '0 8px 32px rgba(99, 102, 241, 0.3)',
            marginBottom: '20px',
          }}>
            <Shield size={32} color="white" />
          </div>
          <h1 style={{
            fontSize: '1.8rem',
            fontWeight: 800,
            background: 'linear-gradient(135deg, #e2e8f0, #94a3b8)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '8px',
          }}>
            SafetyEye
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
            AI-Powered Workplace Safety Platform
          </p>
        </div>

        {/* Login Card */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.6)',
          backdropFilter: 'blur(20px)',
          borderRadius: '1.25rem',
          border: '1px solid rgba(148, 163, 184, 0.08)',
          padding: '36px',
          boxShadow: '0 24px 48px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255,255,255,0.03)',
        }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '6px', color: '#e2e8f0' }}>
            Welcome back
          </h2>
          <p style={{ color: '#64748b', fontSize: '0.85rem', marginBottom: '28px' }}>
            Sign in to access the monitoring dashboard
          </p>

          {error && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '8px',
              background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.2)',
              borderRadius: '10px', padding: '10px 14px', marginBottom: '20px',
              color: '#fb7185', fontSize: '0.82rem', fontWeight: 500,
              animation: 'fadeIn 0.3s ease',
            }}>
              <AlertCircle size={15} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Email */}
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Email Address
              </label>
              <div style={{
                display: 'flex', alignItems: 'center', gap: '10px',
                background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(148,163,184,0.1)',
                borderRadius: '10px', padding: '0 14px',
                transition: 'border-color 0.3s, box-shadow 0.3s',
              }}
              onFocus={e => { e.currentTarget.style.borderColor = 'rgba(99,102,241,0.4)'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.1)'; }}
              onBlur={e => { e.currentTarget.style.borderColor = 'rgba(148,163,184,0.1)'; e.currentTarget.style.boxShadow = 'none'; }}
              >
                <Mail size={16} color="#64748b" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@safetyeye.com"
                  style={{
                    background: 'transparent', border: 'none', color: '#e2e8f0',
                    padding: '12px 0', width: '100%', outline: 'none', fontSize: '0.9rem',
                  }}
                />
              </div>
            </div>

            {/* Password */}
            <div style={{ marginBottom: '28px' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Password
              </label>
              <div style={{
                display: 'flex', alignItems: 'center', gap: '10px',
                background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(148,163,184,0.1)',
                borderRadius: '10px', padding: '0 14px',
                transition: 'border-color 0.3s, box-shadow 0.3s',
              }}
              onFocus={e => { e.currentTarget.style.borderColor = 'rgba(99,102,241,0.4)'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.1)'; }}
              onBlur={e => { e.currentTarget.style.borderColor = 'rgba(148,163,184,0.1)'; e.currentTarget.style.boxShadow = 'none'; }}
              >
                <Lock size={16} color="#64748b" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  style={{
                    background: 'transparent', border: 'none', color: '#e2e8f0',
                    padding: '12px 0', width: '100%', outline: 'none', fontSize: '0.9rem',
                  }}
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b', display: 'flex', padding: '4px' }}>
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              style={{
                width: '100%', padding: '13px',
                background: isLoading ? '#334155' : 'linear-gradient(135deg, #6366f1, #818cf8)',
                color: 'white', border: 'none', borderRadius: '10px',
                fontSize: '0.9rem', fontWeight: 700, cursor: isLoading ? 'wait' : 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
                boxShadow: isLoading ? 'none' : '0 4px 16px rgba(99, 102, 241, 0.35)',
                transition: 'all 0.3s',
              }}
            >
              {isLoading ? 'Authenticating...' : <>Sign In <ArrowRight size={16} /></>}
            </button>
          </form>
        </div>

        {/* Footer hint */}
        <p style={{ textAlign: 'center', color: '#334155', fontSize: '0.75rem', marginTop: '24px' }}>
          Default: admin@safetyeye.com / admin123
        </p>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(12px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
