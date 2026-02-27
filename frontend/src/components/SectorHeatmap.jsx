const toneByValue = (value) => {
  if (value > 0.8) return 'very-positive';
  if (value > 0.3) return 'positive';
  if (value < -0.8) return 'very-negative';
  if (value < -0.3) return 'negative';
  return 'flat';
};

export const SectorHeatmap = ({ sectors = [] }) => (
  <article className="panel">
    <h3>Sector Heatmap</h3>
    <div className="heatmap-grid">
      {sectors.map((sector) => (
        <div key={sector.name} className={`heat-cell ${toneByValue(sector.score)}`}>
          <span>{sector.name}</span>
          <strong>{sector.score > 0 ? '+' : ''}{sector.score}%</strong>
        </div>
      ))}
    </div>
  </article>
);
