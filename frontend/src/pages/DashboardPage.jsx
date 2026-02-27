import { useEffect, useMemo, useState } from 'react';
import { marketApi } from '../api/marketApi';
import { DraggersList } from '../components/DraggersList';
import { MetricCard } from '../components/MetricCard';
import { SectorHeatmap } from '../components/SectorHeatmap';
import { StrengthMeter } from '../components/StrengthMeter';

const fallback = {
  niftyImpact: 1.42,
  sentiment: 'Bullish',
  aiStrength: 78,
  draggers: [
    { symbol: 'HDFCBANK', weight: 9.3, impact: -0.42 },
    { symbol: 'RELIANCE', weight: 8.2, impact: -0.38 },
    { symbol: 'INFY', weight: 6.1, impact: -0.31 },
    { symbol: 'ICICIBANK', weight: 7.6, impact: -0.28 },
    { symbol: 'LT', weight: 4.2, impact: -0.22 },
  ],
  sectors: [
    { name: 'Banking', score: -0.7 },
    { name: 'IT', score: -0.2 },
    { name: 'Auto', score: 0.6 },
    { name: 'FMCG', score: 0.9 },
    { name: 'Energy', score: -1.1 },
    { name: 'Pharma', score: 0.4 },
  ],
};

const sentimentTone = (sentiment) => {
  if (sentiment?.toLowerCase().includes('bear')) return 'negative';
  if (sentiment?.toLowerCase().includes('bull')) return 'positive';
  return 'neutral';
};

export const DashboardPage = () => {
  const [data, setData] = useState(fallback);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await marketApi.getDashboard();
        setData({ ...fallback, ...response });
      } catch {
        setData(fallback);
      }
    };
    load();
  }, []);

  const niftyTone = useMemo(() => (data.niftyImpact >= 0 ? 'positive' : 'negative'), [data.niftyImpact]);

  return (
    <section className="dashboard-grid">
      <MetricCard title="Live Nifty Impact" value={`${data.niftyImpact > 0 ? '+' : ''}${data.niftyImpact}%`} tone={niftyTone} hint="Real-time weighted movement" />
      <MetricCard title="Market Sentiment" value={data.sentiment} tone={sentimentTone(data.sentiment)} hint="Color-coded AI interpretation" />
      <StrengthMeter value={data.aiStrength} />
      <DraggersList items={data.draggers.slice(0, 5)} />
      <SectorHeatmap sectors={data.sectors} />
    </section>
  );
};
