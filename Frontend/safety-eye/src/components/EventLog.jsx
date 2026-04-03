import styles from './EventLog.module.css';

const VIOLATION_COLORS = {
  'NO-Hardhat':              '#ff2d78',
  'NO-Mask':                 '#ff6b00',
  'NO-Safety Vest':          '#ffcc00',
  'Person Near Vehicle':     '#ff2d78',
  'Vehicle Over Safety Cone':'#ff6b00',
  'Vehicles Approaching':    '#7b2fff',
};

function getColor(type) {
  return VIOLATION_COLORS[type] ?? '#00f5ff';
}

function formatTime(iso) {
  try {
    return new Date(iso).toLocaleTimeString('en-US', { hour12: false });
  } catch {
    return '--:--:--';
  }
}

export default function EventLog({ events }) {
  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <span className={styles.title}>
          <span className={styles.icon}>⚡</span> VIOLATION LOG
        </span>
        <span className={styles.count}>{events.length}</span>
      </div>

      <div className={styles.list}>
        {events.length === 0 && (
          <div className={styles.empty}>No violations detected</div>
        )}
        {events.map((ev, i) => (
          <div
            key={i}
            className={styles.item}
            style={{ '--ev-color': getColor(ev.violation_type) }}
          >
            <span className={styles.dot} />
            <div className={styles.info}>
              <span className={styles.type}>{ev.violation_type}</span>
              <span className={styles.conf}>{(ev.confidence * 100).toFixed(0)}%</span>
            </div>
            <span className={styles.time}>{formatTime(ev.timestamp)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
