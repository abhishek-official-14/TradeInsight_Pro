import styles from './DesignSystemPage.module.css';

const colorTokens = [
  ['Background', '#060B16'],
  ['Surface', '#101A2B'],
  ['Surface Elevated', '#16243A'],
  ['Border', '#223754'],
  ['Text Primary', '#E5EEFF'],
  ['Text Muted', '#93A7C7'],
  ['Primary', '#1EA7FD'],
  ['Primary Alt', '#4F7BFF'],
  ['Success', '#24D18A'],
  ['Warning', '#FFBE55'],
  ['Danger', '#FF647C']
];

const typographyScale = [
  ['Display', '48px / 56px', '700'],
  ['H1', '36px / 44px', '700'],
  ['H2', '30px / 38px', '700'],
  ['H3', '24px / 32px', '600'],
  ['Body L', '18px / 28px', '400'],
  ['Body', '16px / 24px', '400'],
  ['Label', '14px / 20px', '500'],
  ['Caption', '12px / 16px', '500']
];

export const DesignSystemPage = () => (
  <main className={`page-shell ${styles.page}`}>
    <header>
      <p className={styles.kicker}>Design Foundations</p>
      <h1>TradeInsight Pro Design System</h1>
      <p className={styles.subtitle}>A professional fintech-first UI language for analytical workflows and fast decision making.</p>
    </header>

    <section className={styles.section}>
      <h2>Dark Theme Color Palette</h2>
      <div className={styles.colorGrid}>
        {colorTokens.map(([label, value]) => (
          <article key={label} className={styles.colorCard}>
            <div className={styles.swatch} style={{ backgroundColor: value }} />
            <h3>{label}</h3>
            <code>{value}</code>
          </article>
        ))}
      </div>
    </section>

    <section className={styles.section}>
      <h2>Typography Scale</h2>
      <div className={`${styles.surface} ${styles.typographyWrap}`}>
        {typographyScale.map(([token, size, weight]) => (
          <div key={token} className={styles.typeRow}>
            <p>{token}</p>
            <p>{size}</p>
            <p>{weight}</p>
          </div>
        ))}
      </div>
    </section>

    <section className={styles.section}>
      <h2>Card Component</h2>
      <article className={styles.featureCard}>
        <div>
          <p className={styles.kpiLabel}>Portfolio Exposure</p>
          <h3>₹8.42L</h3>
          <p className={styles.positive}>+3.9% vs previous close</p>
        </div>
        <button className={styles.textButton} type="button">View details</button>
      </article>
    </section>

    <section className={styles.section}>
      <h2>Button Variants</h2>
      <div className={styles.buttonRow}>
        <button className={styles.btnPrimary} type="button">Primary</button>
        <button className={styles.btnSecondary} type="button">Secondary</button>
        <button className={styles.btnGhost} type="button">Ghost</button>
        <button className={styles.btnDanger} type="button">Danger</button>
      </div>
    </section>

    <section className={styles.section}>
      <h2>Badge Variants</h2>
      <div className={styles.badgeRow}>
        <span className={`${styles.badge} ${styles.badgeInfo}`}>Realtime</span>
        <span className={`${styles.badge} ${styles.badgeSuccess}`}>Bullish</span>
        <span className={`${styles.badge} ${styles.badgeWarning}`}>Watchlist</span>
        <span className={`${styles.badge} ${styles.badgeDanger}`}>High Risk</span>
      </div>
    </section>

    <section className={styles.section}>
      <h2>Table Style</h2>
      <div className={styles.surface}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Instrument</th>
              <th>LTP</th>
              <th>Change</th>
              <th>Volume</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>NIFTY 25100 CE</td>
              <td>₹142.3</td>
              <td className={styles.positive}>+5.3%</td>
              <td>1.2M</td>
            </tr>
            <tr>
              <td>BANKNIFTY 54000 PE</td>
              <td>₹176.4</td>
              <td className={styles.negative}>-2.1%</td>
              <td>924K</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section className={styles.section}>
      <h2>Modal Style</h2>
      <div className={styles.modalBackdrop}>
        <div className={styles.modal}>
          <h3>Enable Intraday Alerts</h3>
          <p>Configure notifications for option chain breakouts and unusual volume in underlyings.</p>
          <div className={styles.buttonRow}>
            <button className={styles.btnGhost} type="button">Cancel</button>
            <button className={styles.btnPrimary} type="button">Save Configuration</button>
          </div>
        </div>
      </div>
    </section>

    <section className={styles.section}>
      <h2>Layout Grid</h2>
      <div className={styles.layoutGrid}>
        <div className={styles.gridItem}>4 Columns</div>
        <div className={styles.gridItem}>4 Columns</div>
        <div className={styles.gridItem}>4 Columns</div>
        <div className={`${styles.gridItem} ${styles.gridSpan8}`}>8 Columns</div>
        <div className={`${styles.gridItem} ${styles.gridSpan4}`}>4 Columns</div>
      </div>
    </section>
  </main>
);
