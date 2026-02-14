import { useEffect, useMemo, useState } from 'react';
import { getSummary, getFilePreview } from './api';

function formatBytes(bytes) {
  const units = ['B', 'KB', 'MB', 'GB'];
  let value = Number(bytes || 0);
  let index = 0;

  while (value >= 1024 && index < units.length - 1) {
    value /= 1024;
    index += 1;
  }

  return `${value.toFixed(index === 0 ? 0 : 2)} ${units[index]}`;
}

function formatDate(value) {
  if (!value) return 'n/a';
  return new Date(value).toLocaleString();
}

function StatusPill({ status }) {
  const text = status || 'unknown';
  return <span className={`pill pill-${text}`}>{text.toUpperCase()}</span>;
}

function SummaryCard({ label, value, accent }) {
  return (
    <article className="summary-card" style={accent ? { '--card-accent': accent } : undefined}>
      <div className="summary-card-accent" />
      <div className="summary-card-content">
        <p className="label">{label}</p>
        <p className="value">{value}</p>
      </div>
    </article>
  );
}

function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton skeleton-label" />
      <div className="skeleton skeleton-value" />
    </div>
  );
}

function SkeletonRow() {
  return (
    <div className="skeleton-row">
      <div className="skeleton skeleton-cell" />
      <div className="skeleton skeleton-cell" />
      <div className="skeleton skeleton-cell" />
      <div className="skeleton skeleton-cell" />
      <div className="skeleton skeleton-cell" />
    </div>
  );
}

function EmptyState({ message }) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">&#128193;</div>
      <p>{message || 'No data available'}</p>
    </div>
  );
}

function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [payload, setPayload] = useState(null);
  const [selectedFile, setSelectedFile] = useState('');
  const [preview, setPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  const refresh = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getSummary();
      setPayload(data);
      if (!selectedFile && data.files?.length) {
        setSelectedFile(data.files[0].file_name);
      }
    } catch (err) {
      setError(err.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  useEffect(() => {
    if (!selectedFile) {
      setPreview(null);
      return;
    }

    let cancelled = false;
    const run = async () => {
      setPreviewLoading(true);
      try {
        const next = await getFilePreview(selectedFile, 20);
        if (!cancelled) {
          setPreview(next);
        }
      } catch (err) {
        if (!cancelled) {
          setPreview({ error: err.message });
        }
      } finally {
        if (!cancelled) {
          setPreviewLoading(false);
        }
      }
    };

    run();
    return () => {
      cancelled = true;
    };
  }, [selectedFile]);

  const summary = payload?.summary || {};
  const files = payload?.files || [];
  const checks = payload?.checks || [];

  const passing = useMemo(() => checks.filter((c) => c.status === 'pass').length, [checks]);
  const warn = useMemo(() => checks.filter((c) => c.status === 'warn').length, [checks]);
  const fail = useMemo(() => checks.filter((c) => c.status === 'fail').length, [checks]);
  const checkRate = checks.length === 0 ? 0 : Math.round((passing / checks.length) * 100);

  return (
    <main className="container">
      <header className="topbar">
        <div>
          <h1>Raw Data Inventory</h1>
          <p>Synthetic data readiness against PRD checks</p>
        </div>
        <button onClick={refresh} className="primary" disabled={loading}>
          {loading ? 'Refreshing\u2026' : 'Refresh'}
        </button>
      </header>

      {error && (
        <div className="error-banner">
          <span>&#9888;</span>
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <section className="summary-grid">
          {Array.from({ length: 7 }, (_, i) => (
            <SkeletonCard key={i} />
          ))}
        </section>
      ) : !payload ? (
        <EmptyState message="No data available. Check that the API server is running." />
      ) : (
        <>
          <section className="summary-grid">
            <SummaryCard label="Total Files" value={summary.total_files || 0} accent="var(--accent)" />
            <SummaryCard label="CSV Files" value={summary.csv_files || 0} accent="var(--accent)" />
            <SummaryCard label="Total Rows" value={(summary.total_rows || 0).toLocaleString()} accent="var(--text-secondary)" />
            <SummaryCard label="Total Size" value={formatBytes(summary.total_size_bytes || 0)} accent="var(--text-secondary)" />
            <SummaryCard label="Checks Passing" value={`${passing}/${checks.length} (${checkRate}%)`} accent="var(--pass)" />
            <SummaryCard label="Checks Warn/Fail" value={`${warn} / ${fail}`} accent="var(--warn)" />
            <SummaryCard label="Last Scan" value={formatDate(summary.scanned_at)} accent="var(--text-muted)" />
          </section>

          <section className="grid">
            <article className="card wide">
              <h2>Data Files</h2>
              {files.length === 0 ? (
                <EmptyState message="No files found in data/raw/" />
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>File</th>
                        <th>Rows</th>
                        <th>Columns</th>
                        <th>Size</th>
                        <th>Modified</th>
                        <th>Null Ratio</th>
                        <th>Type</th>
                      </tr>
                    </thead>
                    <tbody>
                      {files.map((file) => {
                        const selected = file.file_name === selectedFile;
                        return (
                          <tr
                            key={file.file_name}
                            className={selected ? 'selected' : ''}
                            onClick={() => setSelectedFile(file.file_name)}
                          >
                            <td className="file-name">{file.file_name}</td>
                            <td>{file.is_csv ? file.rows : <span className="na-value">n/a</span>}</td>
                            <td>{file.is_csv ? file.columns : <span className="na-value">n/a</span>}</td>
                            <td>{formatBytes(file.file_size_bytes)}</td>
                            <td>{formatDate(file.last_modified)}</td>
                            <td>{file.overall_missing_ratio != null ? `${(file.overall_missing_ratio * 100).toFixed(2)}%` : <span className="na-value">n/a</span>}</td>
                            <td>{file.is_csv ? 'CSV' : 'Other'}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </article>

            <article className="card">
              <h2>PRD Conformance</h2>
              {checks.length === 0 ? (
                <EmptyState message="No conformance checks available" />
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Status</th>
                        <th>Check</th>
                        <th>File</th>
                        <th>Observed</th>
                        <th>Expected</th>
                        <th>Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      {checks.map((check) => (
                        <tr key={`${check.file}-${check.id}`}>
                          <td><StatusPill status={check.status} /></td>
                          <td>{check.title}</td>
                          <td>{check.file}</td>
                          <td>
                            <pre>{JSON.stringify(check.observed, null, 2)}</pre>
                          </td>
                          <td>
                            <pre>{JSON.stringify(check.expected, null, 2)}</pre>
                          </td>
                          <td>{check.details}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </article>
          </section>

          <article className="card">
            <h2>File Preview</h2>
            {selectedFile ? (
              <>
                <p className="muted">Source: {selectedFile}</p>
                {previewLoading ? (
                  <p className="muted">Loading preview...</p>
                ) : preview?.error ? (
                  <p className="error">{preview.error}</p>
                ) : (
                  <pre>{JSON.stringify(preview?.preview_rows ?? [], null, 2)}</pre>
                )}
              </>
            ) : (
              <p className="muted">Select a file from the table to view a preview.</p>
            )}
          </article>
        </>
      )}

      {loading && payload === null && (
        <section className="grid" style={{ marginTop: '14px' }}>
          <article className="card wide">
            <h2>Data Files</h2>
            <div style={{ padding: '8px 0' }}>
              <SkeletonRow />
              <SkeletonRow />
              <SkeletonRow />
            </div>
          </article>
          <article className="card">
            <h2>PRD Conformance</h2>
            <div style={{ padding: '8px 0' }}>
              <SkeletonRow />
              <SkeletonRow />
              <SkeletonRow />
            </div>
          </article>
        </section>
      )}
    </main>
  );
}

export default App;
