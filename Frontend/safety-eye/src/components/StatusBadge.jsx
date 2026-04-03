import styles from './StatusBadge.module.css';

const STATUS_MAP = {
  connected:    { label: 'LIVE',         color: 'ok' },
  connecting:   { label: 'CONNECTING…',  color: 'warn' },
  disconnected: { label: 'OFFLINE',      color: 'muted' },
  error:        { label: 'ERROR',        color: 'danger' },
};

export default function StatusBadge({ status }) {
  const { label, color } = STATUS_MAP[status] ?? STATUS_MAP.disconnected;
  return (
    <span className={`${styles.badge} ${styles[color]}`}>
      <span className={styles.dot} />
      {label}
    </span>
  );
}
