export const StrengthMeter = ({ value = 0 }) => {
  const normalized = Math.max(0, Math.min(100, value));

  return (
    <article className="panel strength-panel">
      <div className="panel-head">
        <h3>AI Strength Meter</h3>
        <span>{normalized}%</span>
      </div>
      <div className="meter-track" role="progressbar" aria-valuenow={normalized} aria-valuemin="0" aria-valuemax="100">
        <div className="meter-fill" style={{ width: `${normalized}%` }} />
      </div>
    </article>
  );
};
