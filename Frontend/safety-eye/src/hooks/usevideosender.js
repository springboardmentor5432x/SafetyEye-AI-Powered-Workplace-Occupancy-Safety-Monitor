import { useEffect, useRef, useState, useCallback } from 'react';

const FRAME_RATE = 30;

export function useVideoSender(getWs) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const requestRef = useRef(null);
  const loopRef = useRef(null);

  // Create off-screen elements once, fixed at 320×240
  if (!videoRef.current && typeof document !== 'undefined') {
    videoRef.current = document.createElement('video');
    videoRef.current.muted = true;
    videoRef.current.playsInline = true;
    canvasRef.current = document.createElement('canvas');
    canvasRef.current.width = 320;
    canvasRef.current.height = 240;
  }

  const sendFrame = useCallback(() => {
    const ws = getWs?.();
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || video.readyState < 2) return;

    if (canvas.width !== 320) { canvas.width = 320; canvas.height = 240; }
    canvas.getContext('2d').drawImage(video, 0, 0, 320, 240);

    canvas.toBlob((blob) => {
      const ws2 = getWs?.();
      if (blob && ws2?.readyState === WebSocket.OPEN) {
        ws2.send(blob);
      }
    }, 'image/jpeg', 0.6);
  }, [getWs]);

  const stopStream = useCallback(() => {
    setIsStreaming(false);
    if (loopRef.current) clearInterval(loopRef.current);
    loopRef.current = null;

    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(t => t.stop());
      videoRef.current.srcObject = null;
    }
  }, []);

  const startStream = useCallback(async () => {
    if (isStreaming) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 320 }, height: { ideal: 240 } },
        audio: false,
      });

      videoRef.current.srcObject = stream;
      await videoRef.current.play();

      // Wait for WS to be open (it's managed by useVideoStream)
      const waitForWs = () => {
        const ws = getWs?.();
        if (ws?.readyState === WebSocket.OPEN) {
          setIsStreaming(true);
          setError(null);
          loopRef.current = setInterval(sendFrame, 1000 / FRAME_RATE);
        } else {
          setTimeout(waitForWs, 200);
        }
      };
      waitForWs();
    } catch (err) {
      setError(`Camera error: ${err.message}`);
    }
  }, [isStreaming, getWs, sendFrame]);

  useEffect(() => {
    return () => stopStream();
  }, [stopStream]);

  return { startStream, stopStream, isStreaming, error };
}
