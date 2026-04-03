import styles from './VideoFeed.module.css';
import StatusBadge from './StatusBadge';

export default function VideoFeed({ canvasRef, status, fps, isStreaming }) {
  const connected = status === 'connected';

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <span className={styles.title}>
          <span className={styles.icon}>◈</span> LIVE FEED
          {isStreaming && <span className={styles.streamingDot} title="Sending to server" />}
        </span>
        <div className={styles.meta}>
          <span className={styles.fps}>{fps} FPS</span>
          <StatusBadge status={status} />
        </div>
      </div>

      <div className={styles.screen}>
        {/* Canvas is always mounted so the ref is always valid */}
        <canvas
          ref={canvasRef}
          className={styles.frame}
          style={{ display: connected ? 'block' : 'none' }}
        />
        {!connected && (
          <div className={styles.placeholder}>
            <span className={styles.noSignal}>
              {status === 'connecting' ? 'CONNECTING…' : 'AWAITING FEED'}
            </span>
          </div>
        )}
        <div className={styles.cornerTL} />
        <div className={styles.cornerTR} />
        <div className={styles.cornerBL} />
        <div className={styles.cornerBR} />
      </div>
    </div>
  );
}
