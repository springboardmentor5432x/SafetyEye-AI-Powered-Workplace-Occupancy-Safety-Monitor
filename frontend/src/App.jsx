import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import LiveMonitor from './pages/LiveMonitor';
import CameraSetup from './pages/CameraSetup';
import IncidentLogs from './pages/IncidentLogs';
import Settings from './pages/Settings';
import ModelPerformance from './pages/ModelPerformance';
import Login from './pages/Login';
import ToastContainer from './components/ToastContainer';
import { useEffect, useState, useRef, useCallback } from 'react';

const API_URL = 'http://localhost:5000';

// Generate a digital beep using native Web Audio API
const playBeep = () => {
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    
    oscillator.type = 'square';
    oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); 
    gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.3);
    
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.3);
  } catch(e) {}
};

function App() {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
  const [toasts, setToasts] = useState([]);
  const lastAlarmRef = useRef(false);
  const lastSeenViolationIdRef = useRef(null);

  // ───── Auth State ─────
  const [authToken, setAuthToken] = useState(localStorage.getItem('authToken') || null);
  const [currentUser, setCurrentUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);

  // Verify token on app load
  useEffect(() => {
    const verifyToken = async () => {
      if (!authToken) {
        setAuthChecked(true);
        return;
      }
      try {
        const res = await fetch(`${API_URL}/api/auth/me`, {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (res.ok) {
          const user = await res.json();
          setCurrentUser(user);
        } else {
          // Token expired or invalid
          setAuthToken(null);
          setCurrentUser(null);
          localStorage.removeItem('authToken');
        }
      } catch (err) {
        // Server not running — keep token, will retry
      }
      setAuthChecked(true);
    };
    verifyToken();
  }, [authToken]);

  const handleLogin = (token, user) => {
    setAuthToken(token);
    setCurrentUser(user);
    localStorage.setItem('authToken', token);
  };

  const handleLogout = async () => {
    try {
      await fetch(`${API_URL}/api/auth/logout`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
    } catch (e) {}
    setAuthToken(null);
    setCurrentUser(null);
    localStorage.removeItem('authToken');
  };

  // ───── Theme ─────
  useEffect(() => {
    if (theme === 'light') {
      document.body.classList.add('light-theme');
    } else {
      document.body.classList.remove('light-theme');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  // ───── Status + Audio + Toast Poller (only when logged in) ─────
  useEffect(() => {
    if (!authToken) return;

    const checkStatus = async () => {
      try {
        const res = await fetch(`${API_URL}/api/status`);
        const data = await res.json();
        
        if (data.alarm && !lastAlarmRef.current) {
          playBeep();
        }
        lastAlarmRef.current = data.alarm;

        if (data.latest_violation) {
          const latestId = data.latest_violation.id;
          if (lastSeenViolationIdRef.current !== null && latestId > lastSeenViolationIdRef.current) {
            setToasts(prev => {
              if (prev.some(t => t.dbId === latestId)) return prev;
              return [...prev, {
                id: Date.now(),
                dbId: latestId,
                violation_type: data.latest_violation.violation_type,
                track_id: data.latest_violation.track_id,
                timestamp: data.latest_violation.timestamp,
              }].slice(-5);
            });
          }
          lastSeenViolationIdRef.current = latestId;
        }
      } catch (err) {}
    };
    
    const interval = setInterval(checkStatus, 3000);
    return () => clearInterval(interval);
  }, [authToken]);

  // Show nothing until auth check completes
  if (!authChecked) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#080c14', color: '#64748b' }}>
        Loading...
      </div>
    );
  }

  // Not logged in → show Login page
  if (!authToken || !currentUser) {
    return <Login onLogin={handleLogin} />;
  }

  // Logged in → show the app
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout user={currentUser} onLogout={handleLogout} />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/cameras" element={<CameraSetup />} />
          <Route path="/monitor" element={<LiveMonitor />} />
          <Route path="/logs" element={<IncidentLogs />} />
          <Route path="/model" element={<ModelPerformance />} />
          <Route path="/settings" element={
            <Settings theme={theme} setTheme={setTheme} user={currentUser} authToken={authToken} />
          } />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
      
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </BrowserRouter>
  );
}

export default App;
