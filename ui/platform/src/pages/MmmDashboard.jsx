const KPI_CARDS = [
  { label: 'Active Channels', value: '11', sub: 'Digital + traditional', color: 'var(--accent)' },
  { label: 'Total Budget', value: '£20M', sub: 'Annual (2025)', color: '#10b981' },
  { label: 'Avg. Blended ROI', value: '—', sub: 'Model not yet run', color: '#f59e0b' },
  { label: 'Weekly Impressions', value: '—', sub: 'Pending aggregation', color: '#8b5cf6' },
]

const CHANNELS = [
  { name: 'Meta (Facebook/Instagram)', type: 'Digital', budget: '£3.2M', status: 'active' },
  { name: 'Google Search', type: 'Digital', budget: '£2.8M', status: 'active' },
  { name: 'DV360 Programmatic', type: 'Digital', budget: '£2.0M', status: 'active' },
  { name: 'TikTok', type: 'Digital', budget: '£1.2M', status: 'active' },
  { name: 'YouTube', type: 'Digital', budget: '£1.6M', status: 'active' },
  { name: 'LinkedIn', type: 'Digital', budget: '£0.6M', status: 'active' },
  { name: 'TV', type: 'Traditional', budget: '£4.0M', status: 'active' },
  { name: 'OOH (Out of Home)', type: 'Traditional', budget: '£1.8M', status: 'active' },
  { name: 'Print', type: 'Traditional', budget: '£1.2M', status: 'active' },
  { name: 'Radio', type: 'Traditional', budget: '£0.8M', status: 'active' },
  { name: 'Events & Activations', type: 'Traditional', budget: '£0.8M', status: 'active' },
]

function KpiCard({ label, value, sub, color }) {
  return (
    <div style={{
      background: 'var(--bg-surface)', border: '1px solid var(--border)',
      borderRadius: 10, padding: '18px 20px', position: 'relative', overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: 0, left: 0, width: 4, height: '100%',
        background: color, borderRadius: '10px 0 0 10px',
      }} />
      <div style={{ paddingLeft: 8 }}>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {label}
        </div>
        <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--text)', margin: '4px 0 2px' }}>
          {value}
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{sub}</div>
      </div>
    </div>
  )
}

function StatusBadge({ type }) {
  const isDigital = type === 'Digital'
  return (
    <span style={{
      display: 'inline-block', padding: '2px 8px', borderRadius: 20, fontSize: 11, fontWeight: 600,
      background: isDigital ? 'var(--accent-muted)' : 'rgba(16,185,129,0.12)',
      color: isDigital ? 'var(--accent)' : 'var(--success)',
    }}>
      {type}
    </span>
  )
}

function PlaceholderChart({ label, height = 160 }) {
  return (
    <div style={{
      height, border: '1px dashed var(--border)', borderRadius: 8,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg)', flexDirection: 'column', gap: 6,
    }}>
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
        fill="none" stroke="var(--text-muted)" strokeWidth="1.5">
        <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
        <line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/>
      </svg>
      <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{label}</span>
    </div>
  )
}

export default function MmmDashboard() {
  return (
    <div style={{ maxWidth: 1000 }}>
      {/* Header */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700, color: 'var(--text)' }}>MMM Dashboard</h1>
          <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--text-muted)' }}>
            Marketing Mix Model insights for DEEPAL / AVATR UK launch (2025).
          </p>
        </div>
        <span style={{
          padding: '5px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600,
          background: 'rgba(245,158,11,0.12)', color: 'var(--warning)',
          border: '1px solid rgba(245,158,11,0.25)',
        }}>
          Model not yet trained
        </span>
      </div>

      {/* KPI cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 24 }}>
        {KPI_CARDS.map(card => <KpiCard key={card.label} {...card} />)}
      </div>

      {/* Charts row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 24 }}>
        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 10, padding: 20 }}>
          <h3 style={{ margin: '0 0 14px', fontSize: 14, fontWeight: 600, color: 'var(--text)' }}>
            Channel Spend Breakdown
          </h3>
          <PlaceholderChart label="Pie / treemap chart will render here" />
        </div>
        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 10, padding: 20 }}>
          <h3 style={{ margin: '0 0 14px', fontSize: 14, fontWeight: 600, color: 'var(--text)' }}>
            Weekly Spend Timeline
          </h3>
          <PlaceholderChart label="Time-series chart will render here" />
        </div>
      </div>

      {/* Wide chart */}
      <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 10, padding: 20, marginBottom: 24 }}>
        <h3 style={{ margin: '0 0 14px', fontSize: 14, fontWeight: 600, color: 'var(--text)' }}>
          Adstock / Saturation Curves
        </h3>
        <PlaceholderChart label="Response curves will render here after model training" height={140} />
      </div>

      {/* Channel table */}
      <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 10, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, fontSize: 14, fontWeight: 600, color: 'var(--text)' }}>Channel Budget Allocation</h3>
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{CHANNELS.length} channels</span>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ background: 'var(--bg)' }}>
              {['Channel', 'Type', 'Budget (2025)', 'ROI', 'Status'].map(h => (
                <th key={h} style={{
                  padding: '10px 20px', textAlign: 'left', fontWeight: 600,
                  fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase',
                  letterSpacing: '0.05em', borderBottom: '1px solid var(--border)',
                }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {CHANNELS.map((ch, i) => (
              <tr key={ch.name} style={{ borderBottom: i < CHANNELS.length - 1 ? '1px solid var(--border)' : 'none' }}>
                <td style={{ padding: '11px 20px', fontWeight: 500, color: 'var(--text)' }}>{ch.name}</td>
                <td style={{ padding: '11px 20px' }}><StatusBadge type={ch.type} /></td>
                <td style={{ padding: '11px 20px', color: 'var(--text)', fontWeight: 500 }}>{ch.budget}</td>
                <td style={{ padding: '11px 20px', color: 'var(--text-muted)' }}>—</td>
                <td style={{ padding: '11px 20px' }}>
                  <span style={{
                    display: 'inline-block', padding: '2px 8px', borderRadius: 20, fontSize: 11, fontWeight: 600,
                    background: 'rgba(16,185,129,0.12)', color: 'var(--success)',
                  }}>
                    Active
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
