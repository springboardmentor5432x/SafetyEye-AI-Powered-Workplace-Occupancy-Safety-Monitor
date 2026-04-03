import { useEffect, useRef, useState } from 'react';

const LOGS_URL = 'http://localhost:3000/api/logs?n=50';
const INTERVAL_MS = 2000;

export function useLogs(active = true) {
  const [lines, setLines] = useState('');
  const [error, setError] = useState(null);
  const timerRef = useRef(null);

  useEffect(() => {
    if (!active) return;

    async function fetchLogs() {
      try {
        const res = await fetch(LOGS_URL);
        const data = await res.json();
        setLines(data.lines);
        setError(null);
      } catch {
        setError('Failed to fetch logs');
      }
    }

    fetchLogs();
    timerRef.current = setInterval(fetchLogs, INTERVAL_MS);
    return () => clearInterval(timerRef.current);
  }, [active]);

  return { lines, error };
}
