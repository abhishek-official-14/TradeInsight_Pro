export const MetricCard = ({ title, value, tone = 'neutral', hint }) => (
  <article className={`metric-card ${tone}`}>
    <p className="metric-title">{title}</p>
    <h3>{value}</h3>
    {hint && <span className="metric-hint">{hint}</span>}
  </article>
);
