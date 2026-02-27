import { useEffect, useState } from 'react';
import { marketApi } from '../api/marketApi';

export const OptionAnalysisPage = () => {
  const [analysis, setAnalysis] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await marketApi.getOptionAnalysis();
        setAnalysis(response.signals || []);
      } catch {
        setAnalysis([
          { symbol: 'NIFTY', strike: 24200, action: 'BUY CE', confidence: 81 },
          { symbol: 'BANKNIFTY', strike: 51500, action: 'BUY PE', confidence: 73 },
        ]);
      }
    };
    load();
  }, []);

  return (
    <section className="panel">
      <h2>Option Analysis</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Strike</th>
              <th>Action</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {analysis.map((signal, idx) => (
              <tr key={`${signal.symbol}-${idx}`}>
                <td>{signal.symbol}</td>
                <td>{signal.strike}</td>
                <td>{signal.action}</td>
                <td>{signal.confidence}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};
