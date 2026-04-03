import { useEffect, useRef, useState, useCallback } from 'react';

const WS_EVENTS_URL = 'ws://localhost:3000/ws/events';
const MAX_EVENTS = 50;

export function useEvents() {
  const [events, setEvents] = useState([]);
  const wsRef = useRef(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_EVENTS_URL);
    wsRef.current = ws;

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.type !== 'violation') return;
        setEvents((prev) => [msg, ...prev].slice(0, MAX_EVENTS));
      } catch {
        // ignore
      }
    };

    ws.onclose = () => setTimeout(connect, 2000);
  }, []);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);

  return events;
}
