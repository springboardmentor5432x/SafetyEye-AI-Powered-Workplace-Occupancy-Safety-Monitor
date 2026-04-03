import { useState, useEffect } from 'react';
import { useVideoStream } from './hooks/useVideoStream';
import { useVideoSender } from './hooks/usevideosender';
import { useEvents } from './hooks/useEvents';
import VideoFeed from './components/VideoFeed';
import EventLog from './components/EventLog';
import StatsBar from './components/StatsBar';
import LogViewer from './components/LogViewer';
import styles from './App.module.css';

function Clock() {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return (
    <span className={styles.clockText}>
      {time.toLocaleTimeString('en-US', { hour12: false })}
    </span>
  );
}

export default function App() {
  const { canvasRef, status, fps, getWs } = useVideoStream();
  const { startStream, stopStream, isStreaming, error } = useVideoSender(getWs);
  const events = useEvents();
  const [tab, setTab] = useState('feed'); // 'feed' | 'logs'

  // Backend mode: server pushes frames, frontend only receives
  // useEffect(() => {
  //   if (status === 'connected' && !isStreaming) startStream();
  //   if (status === 'disconnected' && isStreaming) stopStream();
  // }, [status]);

  return (
    <div className={styles.app}>
      <header className={styles.topbar}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>◈</span>
          <span className={styles.logoText}>
            SAFETY<span className={styles.logoAccent}>EYE</span>
          </span>
        </div>
        <nav className={styles.tabs}>
          <button
            className={`${styles.tab} ${tab === 'feed' ? styles.tabActive : ''}`}
            onClick={() => setTab('feed')}
          >
            LIVE FEED
          </button>
          <button
            className={`${styles.tab} ${tab === 'logs' ? styles.tabActive : ''}`}
            onClick={() => setTab('logs')}
          >
            LOGS
          </button>
        </nav>
        <div className={styles.headerRight}>
          <StatsBar events={events} />
          {error && <span className={styles.errorBadge}>{error}</span>}
          <Clock />
        </div>
      </header>

      {tab === 'feed' ? (
        <main className={styles.grid}>
          <section className={styles.feedSection}>
            <VideoFeed canvasRef={canvasRef} status={status} fps={fps} isStreaming={isStreaming} />
          </section>
          <aside className={styles.sidebar}>
            <EventLog events={events} />
          </aside>
        </main>
      ) : (
        <main className={styles.logsPage}>
          <LogViewer active={tab === 'logs'} />
        </main>
      )}
    </div>
  );
}
