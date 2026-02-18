import { useState, useEffect, useRef } from 'react'
import { getDatasets } from '../api'

const PLACEHOLDER_DATASETS = [
  { name: 'meta_performance.csv', category: 'Digital Media', rows: 2976, updated: '2025-01-01', status: 'ready' },
  { name: 'google_search.csv', category: 'Digital Media', rows: 2080, updated: '2025-01-01', status: 'ready' },
  { name: 'tv_campaign.csv', category: 'Traditional Media', rows: 2080, updated: '2025-01-01', status: 'ready' },
  { name: 'vehicle_sales.csv', category: 'Sales Pipeline', rows: 12480, updated: '2025-01-01', status: 'ready' },
  { name: 'weekly_channel_spend.csv', category: 'MMM Ready', rows: 572, updated: '2025-01-01', status: 'ready' },
  { name: 'model_ready_data.csv', category: 'MMM Ready', rows: 52, updated: '2025-01-01', status: 'ready' },
]

function StatusBadge({ status }) {
  const colors = {
    ready: { bg: 'rgba(16,185,129,0.12)', color: 'var(--success)' },
    processing: { bg: 'rgba(99,102,241,0.12)', color: 'var(--accent)' },
    error: { bg: 'rgba(239,68,68,0.12)', color: 'var(--danger)' },
  }
  const c = colors[status] || colors.ready
  return (
    <span style={{
      display: 'inline-block', padding: '2px 8px', borderRadius: 20,
      fontSize: 11, fontWeight: 600, background: c.bg, color: c.color,
    }}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}

function CategoryBadge({ category }) {
  const colorMap = {
    'Digital Media': { bg: 'rgba(99,102,241,0.1)', color: 'var(--accent)' },
    'Traditional Media': { bg: 'rgba(139,92,246,0.1)', color: '#8b5cf6' },
    'Sales Pipeline': { bg: 'rgba(16,185,129,0.1)', color: 'var(--success)' },
    'MMM Ready': { bg: 'rgba(245,158,11,0.1)', color: 'var(--warning)' },
  }
  const c = colorMap[category] || { bg: 'var(--bg)', color: 'var(--text-muted)' }
  return (
    <span style={{
      display: 'inline-block', padding: '2px 8px', borderRadius: 20,
      fontSize: 11, fontWeight: 600, background: c.bg, color: c.color,
    }}>
      {category}
    </span>
  )
}

function DropZone({ onFileSelect }) {
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef(null)

  function handleDrop(e) {
    e.preventDefault()
    setDragOver(false)
    const files = Array.from(e.dataTransfer.files)
    if (files.length) onFileSelect(files)
  }

  return (
    <div
      onDragOver={e => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      style={{
        border: `2px dashed ${dragOver ? 'var(--accent)' : 'var(--border)'}`,
        borderRadius: 10, padding: '36px 20px', textAlign: 'center',
        cursor: 'pointer', background: dragOver ? 'var(--accent-muted)' : 'var(--bg-surface)',
        transition: 'border-color 0.15s, background 0.15s',
        marginBottom: 24,
      }}
    >
      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".csv,.json,.parquet"
        style={{ display: 'none' }}
        onChange={e => onFileSelect(Array.from(e.target.files))}
      />
      <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24"
        fill="none" stroke={dragOver ? 'var(--accent)' : 'var(--text-muted)'}
        strokeWidth="1.5" style={{ margin: '0 auto 10px', display: 'block' }}>
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="17 8 12 3 7 8"/>
        <line x1="12" y1="3" x2="12" y2="15"/>
      </svg>
      <p style={{ margin: '0 0 4px', fontWeight: 600, fontSize: 14, color: 'var(--text)' }}>
        Drop files here or click to upload
      </p>
      <p style={{ margin: 0, fontSize: 12, color: 'var(--text-muted)' }}>
        Supports CSV, JSON, Parquet. Max 500 MB.
      </p>
    </div>
  )
}

export default function DataManagement() {
  const [datasets, setDatasets] = useState(PLACEHOLDER_DATASETS)
  const [notification, setNotification] = useState(null)

  useEffect(() => {
    getDatasets().then(data => {
      if (data && data.length) setDatasets(data)
    }).catch(() => {})
  }, [])

  function handleFileSelect(files) {
    setNotification(`${files.length} file(s) queued — API not yet connected.`)
    setTimeout(() => setNotification(null), 4000)
  }

  const categories = [...new Set(datasets.map(d => d.category))]

  return (
    <div style={{ maxWidth: 960 }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700, color: 'var(--text)' }}>Data Management</h1>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--text-muted)' }}>
          Upload datasets and manage the synthetic data pipeline inputs.
        </p>
      </div>

      {/* Notification */}
      {notification && (
        <div style={{
          padding: '10px 16px', borderRadius: 8, marginBottom: 16,
          background: 'var(--accent-muted)', border: '1px solid var(--accent)',
          color: 'var(--accent)', fontSize: 13, fontWeight: 500,
        }}>
          {notification}
        </div>
      )}

      {/* Drop zone */}
      <DropZone onFileSelect={handleFileSelect} />

      {/* Stats row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
        {[
          { label: 'Total Datasets', value: datasets.length },
          { label: 'Digital Media', value: datasets.filter(d => d.category === 'Digital Media').length },
          { label: 'Traditional Media', value: datasets.filter(d => d.category === 'Traditional Media').length },
          { label: 'MMM Ready', value: datasets.filter(d => d.category === 'MMM Ready').length },
        ].map(({ label, value }) => (
          <div key={label} style={{
            background: 'var(--bg-surface)', border: '1px solid var(--border)',
            borderRadius: 10, padding: '14px 16px', textAlign: 'center',
          }}>
            <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--text)' }}>{value}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Dataset table */}
      <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 10, overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, fontSize: 14, fontWeight: 600, color: 'var(--text)' }}>Available Datasets</h3>
          <div style={{ display: 'flex', gap: 6 }}>
            {categories.map(cat => (
              <span key={cat} style={{ fontSize: 11, color: 'var(--text-muted)', background: 'var(--bg)', padding: '3px 8px', borderRadius: 20, border: '1px solid var(--border)' }}>
                {cat}
              </span>
            ))}
          </div>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ background: 'var(--bg)' }}>
              {['Filename', 'Category', 'Rows', 'Last Updated', 'Status', ''].map(h => (
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
            {datasets.map((d, i) => (
              <tr key={d.name} style={{ borderBottom: i < datasets.length - 1 ? '1px solid var(--border)' : 'none' }}>
                <td style={{ padding: '11px 20px', fontFamily: 'monospace', fontSize: 13, color: 'var(--text)', fontWeight: 500 }}>
                  {d.name}
                </td>
                <td style={{ padding: '11px 20px' }}><CategoryBadge category={d.category} /></td>
                <td style={{ padding: '11px 20px', color: 'var(--text-muted)' }}>
                  {d.rows.toLocaleString()}
                </td>
                <td style={{ padding: '11px 20px', color: 'var(--text-muted)' }}>{d.updated}</td>
                <td style={{ padding: '11px 20px' }}><StatusBadge status={d.status} /></td>
                <td style={{ padding: '11px 20px' }}>
                  <button style={{
                    padding: '4px 10px', borderRadius: 6, fontSize: 12, fontWeight: 500,
                    border: '1px solid var(--border)', background: 'var(--bg)',
                    color: 'var(--text)', cursor: 'pointer',
                  }}>
                    Preview
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
