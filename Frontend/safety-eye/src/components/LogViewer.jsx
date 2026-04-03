import { useEffect, useRef } from 'react';
import { useLogs } from '../hooks/useLogs';
import styles from './LogViewer.module.css';

export default function LogViewer({ active }) {
  const { lines, error } = useLogs(active);
  const preRef = useRef(null);

  // Auto-scroll to bottom on new content
  useEffect(() => {
    if (preRef.current) {
      preRef.current.scrollTop = preRef.current.scrollHeight;
    }
  }, [lines]);

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <span className={styles.title}>
          <span className={styles.icon}>▶</span> SERVER LOGS
        </span>
        <span className={styles.badge}>LIVE · 2s</span>
      </div>
      {error ? (
        <div className={styles.error}>{error}</div>
      ) : (
        <pre ref={preRef} className={styles.logBox}>
          {lines || 'Waiting for logs…'}
        </pre>
      )}
    </div>
  );
}
