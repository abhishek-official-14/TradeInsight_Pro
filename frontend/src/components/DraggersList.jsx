export const DraggersList = ({ items = [] }) => (
  <article className="panel">
    <h3>Top 5 Draggers</h3>
    <ul className="dragger-list">
      {items.map((item) => (
        <li key={item.symbol}>
          <div>
            <p>{item.symbol}</p>
            <span>{item.weight}% weight</span>
          </div>
          <strong className="negative">{item.impact}%</strong>
        </li>
      ))}
    </ul>
  </article>
);
