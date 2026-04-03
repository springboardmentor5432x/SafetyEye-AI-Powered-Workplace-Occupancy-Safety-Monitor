import { useEffect, useRef, useState, useCallback } from 'react';

const WS_STREAM_URL = 'ws://localhost:3000/ws/stream';

export function useVideoStream() {
  const [status, setStatus] = useState('disconnected');
  const [fps, setFps] = useState(0);

  // Canvas ref — VideoFeed attaches the real <canvas> DOM node here
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const frameCountRef = useRef(0);
  const fpsTimerRef = useRef(null);

  const getWs = useCallback(() => wsRef.current, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return wsRef.current;

    setStatus('connecting');
    const ws = new WebSocket(WS_STREAM_URL);
    ws.binaryType = 'arraybuffer';
    wsRef.current = ws;

    ws.onopen = () => {
      // Tell the server to push frames from its video source
      fetch('http://localhost:3000/api/stream-mode/backend', { method: 'POST' })
        .catch(() => {}); // fire-and-forget
      setStatus('connected');
    };

    ws.onmessage = async (e) => {
      if (!(e.data instanceof ArrayBuffer)) return;

      try {
        // createImageBitmap decodes JPEG off the main thread — no object URL needed
        const blob = new Blob([e.data], { type: 'image/jpeg' });
        const bitmap = await createImageBitmap(blob);

        const canvas = canvasRef.current;
        if (!canvas) { bitmap.close(); return; }

        const ctx = canvas.getContext('2d');
        // Resize canvas to match incoming frame once
        if (canvas.width !== bitmap.width || canvas.height !== bitmap.height) {
          canvas.width = bitmap.width;
          canvas.height = bitmap.height;
        }
        ctx.drawImage(bitmap, 0, 0);
        bitmap.close(); // free GPU memory immediately

        frameCountRef.current += 1;
      } catch {
        // ignore decode errors
      }
    };

    ws.onerror = () => setStatus('error');
    ws.onclose = () => {
      setStatus('disconnected');
      setTimeout(connect, 2000);
    };

    return ws;
  }, []);

  const disconnect = useCallback(() => wsRef.current?.close(), []);

  // FPS counter
  useEffect(() => {
    fpsTimerRef.current = setInterval(() => {
      setFps(frameCountRef.current);
      frameCountRef.current = 0;
    }, 1000);
    return () => clearInterval(fpsTimerRef.current);
  }, []);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);

  return { canvasRef, status, fps, connect, disconnect, getWs };
}
