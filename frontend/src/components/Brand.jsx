export function Brand({ compact = false }) {
  return (
    <div className="brand">
      <div className={`brand-mark ${compact ? 'small' : ''}`}>S</div>
      <div>
        <strong>sentinela</strong>
        <span>central IoT</span>
      </div>
    </div>
  )
}
