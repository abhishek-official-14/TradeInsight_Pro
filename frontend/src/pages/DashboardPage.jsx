import { useCallback, useEffect, useMemo, useState } from 'react';
import { aiSignalApi } from '../api/aiSignalApi';
import { niftyApi } from '../api/niftyApi';
import { protectedApi } from '../api/protectedApi';
import { DraggersList } from '../components/DraggersList';
import { MetricCard } from '../components/MetricCard';
import { SectorHeatmap } from '../components/SectorHeatmap';
import { StrengthMeter } from '../components/StrengthMeter';

const REFRESH_INTERVAL_MS = 60_000;

const sentimentTone = (sentiment) => {
  if (sentiment?.toLowerCase().includes('bear')) return 'negative';
  if (sentiment?.toLowerCase().includes('bull')) return 'positive';
  return 'neutral';
};

const SkeletonCard = () => (
  <article className="metric-card neutral" aria-busy="true">
    <p className="metric-title">Loading…</p>
    <div style={{ width: '55%', height: '28px', borderRadius: '8px', background: 'rgba(255,255,255,0.08)' }} />
    <span className="metric-hint">Fetching latest market data</span>
  </article>
);

const SkeletonPanel = ({ title }) => (
  <article className="panel" aria-busy="true">
    <h3>{title}</h3>
    <p className="metric-hint">Loading…</p>
  </article>
);

export const DashboardPage = () => {
  const [data, setData] = useState({
    niftyImpact: null,
    latestPrice: null,
    sentiment: 'Unavailable',
    aiStrength: null,
    draggers: [],
    sectors: [],
    greeting: '',
  });
  const [loading, setLoading] = useState({
    niftyImpact: true,
    latest: true,
    aiSignal: true,
    draggers: true,
    sectors: true,
    greeting: true,
  });
  const [error, setError] = useState('');

  const loadDashboard = useCallback(async () => {
    setLoading({
      niftyImpact: true,
      latest: true,
      aiSignal: true,
      draggers: true,
      sectors: true,
      greeting: true,
    });
    setError('');

    const [impactResult, latestResult, aiSignalResult, draggersResult, sectorsResult, freeResult] = await Promise.allSettled([
      niftyApi.getImpact(),
      niftyApi.getLatest(),
      aiSignalApi.getLatest(),
      niftyApi.getImpact(),
      niftyApi.getSectorHeatmap(),
      protectedApi.getFreeMessage(),
    ]);

    setData((prev) => {
      const next = { ...prev };

      if (impactResult.status === 'fulfilled') {
        next.niftyImpact = impactResult.value?.total_impact ?? null;
      }

      if (latestResult.status === 'fulfilled') {
        next.latestPrice = latestResult.value?.price ?? null;
      }

      if (aiSignalResult.status === 'fulfilled') {
        next.aiStrength = aiSignalResult.value?.score ?? null;
        next.sentiment = aiSignalResult.value?.classification || 'Unavailable';
      }

      if (draggersResult.status === 'fulfilled') {
        next.draggers = (draggersResult.value?.top_draggers ?? []).slice(0, 5);
      }

      if (sectorsResult.status === 'fulfilled') {
        next.sectors = Object.entries(sectorsResult.value ?? {}).map(([name, score]) => ({ name, score }));
      }

      if (freeResult.status === 'fulfilled') {
        next.greeting = freeResult.value?.message || '';
      }

      return next;
    });

    const results = [impactResult, latestResult, aiSignalResult, draggersResult, sectorsResult, freeResult];
    if (results.every((result) => result.status === 'rejected')) {
      setError('Unable to load dashboard data right now.');
    }

    setLoading({
      niftyImpact: false,
      latest: false,
      aiSignal: false,
      draggers: false,
      sectors: false,
      greeting: false,
    });
  }, []);

  useEffect(() => {
    loadDashboard();

    const timer = window.setInterval(() => {
      loadDashboard();
    }, REFRESH_INTERVAL_MS);

    return () => {
      window.clearInterval(timer);
    };
  }, [loadDashboard]);

  const niftyTone = useMemo(() => {
    if (data.niftyImpact === null) return 'neutral';
    return data.niftyImpact >= 0 ? 'positive' : 'negative';
  }, [data.niftyImpact]);

  return (
    <section className="dashboard-grid">
      {error ? (
        <article className="panel" style={{ gridColumn: 'span 12' }}>
          <p className="error-text">{error}</p>
        </article>
      ) : null}
      {!loading.greeting && data.greeting ? (
        <article className="panel" style={{ gridColumn: 'span 12' }}>
          <p>{data.greeting}</p>
        </article>
      ) : null}

      {loading.latest ? (
        <SkeletonCard />
      ) : (
        <MetricCard
          title="Nifty Last Price"
          value={data.latestPrice === null ? 'N/A' : data.latestPrice}
          tone="neutral"
          hint="Latest market snapshot"
        />
      )}

      {loading.niftyImpact ? (
        <SkeletonCard />
      ) : (
        <MetricCard
          title="Live Nifty Impact"
          value={data.niftyImpact === null ? 'N/A' : `${data.niftyImpact > 0 ? '+' : ''}${data.niftyImpact}%`}
          tone={niftyTone}
          hint="Real-time weighted movement"
        />
      )}

      {loading.aiSignal ? (
        <SkeletonCard />
      ) : (
        <MetricCard
          title="Market Sentiment"
          value={data.sentiment}
          tone={sentimentTone(data.sentiment)}
          hint="Color-coded AI interpretation"
        />
      )}

      {loading.aiSignal ? <SkeletonPanel title="AI Strength Meter" /> : <StrengthMeter value={data.aiStrength ?? 0} />}
      {loading.draggers ? <SkeletonPanel title="Top 5 Draggers" /> : <DraggersList items={data.draggers} />}
      {loading.sectors ? <SkeletonPanel title="Sector Heatmap" /> : <SectorHeatmap sectors={data.sectors} />}
    </section>
  );
};
