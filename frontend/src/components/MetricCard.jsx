export function MetricCard({ label, value, color, note }) {
  return (
    <article className="metric-card">
      <span className="metric-label">{label}</span>
      <strong className={`metric-value ${color}`}>{value}</strong>
      <span className="metric-note">{note}</span>
    </article>
  )
}
