import styles from './StatsBar.module.css';

export default function StatsBar({ events }) {
  const counts = events.reduce((acc, ev) => {
    acc[ev.violation_type] = (acc[ev.violation_type] ?? 0) + 1;
    return acc;
  }, {});

  const top = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4);

  return (
    <div className={styles.bar}>
      {top.map(([type, count]) => (
        <div key={type} className={styles.stat}>
          <span className={styles.label}>{type}</span>
          <span className={styles.value}>{count}</span>
        </div>
      ))}
      {top.length === 0 && (
        <span className={styles.clear}>◉ ALL CLEAR</span>
      )}
    </div>
  );
}
