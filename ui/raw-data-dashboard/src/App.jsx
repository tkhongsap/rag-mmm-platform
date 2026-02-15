import React, { useEffect, useMemo, useState } from 'react';
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
  const normalized = ['pass', 'warn', 'fail'].includes(status) ? status : 'unknown';
  return <span className={`pill pill-${normalized}`}>{normalized.toUpperCase()}</span>;
}

function SummaryCard({ label, value, accent, icon }) {
  return (
    <article className="summary-card" style={accent ? { '--card-accent': accent } : undefined}>
      <div className="summary-card-edge" />
      <div className="summary-card-body">
        <span className="summary-card-icon" aria-hidden="true">
          {icon}
        </span>
        <div className="summary-card-text">
          <p className="label">{label}</p>
          <p className="value">{value}</p>
        </div>
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

function EmptyState({ message, icon = '[ ]' }) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">{icon}</div>
      <p>{message || 'No data available'}</p>
    </div>
  );
}

function isCrossFileCheck(check) {
  const fileRef = check.file;
  const checkId = String(check.id || '').toLowerCase();

  if (!fileRef) return true;
  if (checkId.startsWith('cross')) return true;

  const separator = /\s(?:->|\u2192|with|&)\s|,|;/;
  return typeof fileRef === 'string' ? separator.test(fileRef) : false;
}

function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [payload, setPayload] = useState(null);
  const [selectedFile, setSelectedFile] = useState('');
  const [preview, setPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [checkFilter, setCheckFilter] = useState('all');
  const [expandedFiles, setExpandedFiles] = useState(new Set());
  const [previewRows, setPreviewRows] = useState(20);

  const toggleExpand = (fileName, e) => {
    e.stopPropagation();
    setExpandedFiles((prev) => {
      const next = new Set(prev);
      if (next.has(fileName)) {
        next.delete(fileName);
      } else {
        next.add(fileName);
      }
      return next;
    });
  };

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
        const next = await getFilePreview(selectedFile, previewRows);
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
  }, [selectedFile, previewRows]);

  const summary = payload?.summary || {};
  const files = payload?.files || [];
  const checks = payload?.checks || [];

  const passing = useMemo(() => checks.filter((c) => c.status === 'pass').length, [checks]);
  const warn = useMemo(() => checks.filter((c) => c.status === 'warn').length, [checks]);
  const fail = useMemo(() => checks.filter((c) => c.status === 'fail').length, [checks]);
  const checkRate = checks.length === 0 ? 0 : Math.round((passing / checks.length) * 100);

  const filteredChecks = useMemo(
    () => (checkFilter === 'all' ? checks : checks.filter((c) => c.status === checkFilter)),
    [checks, checkFilter],
  );

  const summaryCards = [
    { label: 'Total Files', value: summary.total_files || 0, accent: 'var(--accent)', icon: 'FL' },
    { label: 'CSV Files', value: summary.csv_files || 0, accent: 'var(--accent)', icon: 'CSV' },
    {
      label: 'Total Rows',
      value: (summary.total_rows || 0).toLocaleString(),
      accent: 'var(--text-secondary)',
      icon: 'ROW',
    },
    {
      label: 'Total Size',
      value: formatBytes(summary.total_size_bytes || 0),
      accent: 'var(--text-secondary)',
      icon: 'MB',
    },
    {
      label: 'Checks Passing',
      value: `${passing}/${checks.length} (${checkRate}%)`,
      accent: 'var(--pass)',
      icon: 'OK',
    },
    { label: 'Checks Warn/Fail', value: `${warn} / ${fail}`, accent: 'var(--warn)', icon: 'WF' },
    { label: 'Last Scan', value: formatDate(summary.scanned_at), accent: 'var(--text-muted)', icon: 'TS' },
  ];

  return (
    <main className="container">
      <header className="topbar">
        <div className="topbar-copy">
          <p className="eyebrow">Raw Data Console</p>
          <h1>Raw Data Inventory</h1>
          <p className="subtitle">Synthetic data readiness against PRD checks</p>
        </div>
        <div className="topbar-actions">
          <button onClick={refresh} className="primary" disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          <span>!</span>
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
        <EmptyState message="No data available. Check that the API server is running." icon="?" />
      ) : (
        <>
          <section className="summary-grid">
            {summaryCards.map((card) => (
              <SummaryCard
                key={card.label}
                label={card.label}
                value={card.value}
                accent={card.accent}
                icon={card.icon}
              />
            ))}
          </section>

          <section className="grid">
            <article className="card wide">
              <div className="section-head">
                <h2>Data Files</h2>
                <span className="section-meta">
                  {files.length} file{files.length === 1 ? '' : 's'}
                </span>
              </div>
              {files.length === 0 ? (
                <EmptyState message="No files found in data/raw/" icon="[]" />
              ) : (
                <div className="table-wrap inventory-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th className="expand-col" />
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
                        const expanded = expandedFiles.has(file.file_name);

                        return (
                          <React.Fragment key={file.file_name}>
                            <tr className={selected ? 'selected' : ''} onClick={() => setSelectedFile(file.file_name)}>
                              <td className="expand-cell">
                                {file.is_csv ? (
                                  <button
                                    className={`expand-toggle${expanded ? ' expanded' : ''}`}
                                    onClick={(e) => toggleExpand(file.file_name, e)}
                                    aria-label={expanded ? 'Collapse profiles' : 'Expand profiles'}
                                  >
                                    &gt;
                                  </button>
                                ) : null}
                              </td>
                              <td className="file-name">{file.file_name}</td>
                              <td>{file.is_csv ? file.rows ?? 0 : <span className="na-value">n/a</span>}</td>
                              <td>{file.is_csv ? file.columns ?? 0 : <span className="na-value">n/a</span>}</td>
                              <td>{formatBytes(file.file_size_bytes)}</td>
                              <td>{formatDate(file.last_modified)}</td>
                              <td>
                                {file.overall_missing_ratio != null ? (
                                  `${(file.overall_missing_ratio * 100).toFixed(2)}%`
                                ) : (
                                  <span className="na-value">n/a</span>
                                )}
                              </td>
                              <td>{file.is_csv ? 'CSV' : 'Other'}</td>
                            </tr>
                            {expanded && (
                              <tr className="profiles-row">
                                <td colSpan={8}>
                                  {file.column_profiles?.length ? (
                                    <div className="profiles-wrap">
                                      <table className="profiles-table">
                                        <thead>
                                          <tr>
                                            <th>Column</th>
                                            <th>Dtype</th>
                                            <th>Null Count</th>
                                            <th>Null %</th>
                                            <th>Distinct</th>
                                            <th>Min</th>
                                            <th>Max</th>
                                            <th>Sample</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {file.column_profiles.map((col) => (
                                            <tr key={col.column_name}>
                                              <td className="file-name">{col.column_name}</td>
                                              <td>{col.dtype}</td>
                                              <td>{col.null_count}</td>
                                              <td>{col.null_ratio != null ? `${(col.null_ratio * 100).toFixed(1)}%` : 'n/a'}</td>
                                              <td>{col.distinct_count}</td>
                                              <td className="profile-value" title={col.min != null ? String(col.min) : ''}>
                                                {col.min != null ? String(col.min) : 'n/a'}
                                              </td>
                                              <td className="profile-value" title={col.max != null ? String(col.max) : ''}>
                                                {col.max != null ? String(col.max) : 'n/a'}
                                              </td>
                                              <td
                                                className="profile-value"
                                                title={
                                                  Array.isArray(col.sample_values)
                                                    ? col.sample_values.join(', ')
                                                    : String(col.sample_values ?? '')
                                                }
                                              >
                                                {Array.isArray(col.sample_values)
                                                  ? col.sample_values.join(', ')
                                                  : String(col.sample_values ?? '')}
                                              </td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    </div>
                                  ) : (
                                    <div className="profiles-empty muted">No column profile data available.</div>
                                  )}
                                </td>
                              </tr>
                            )}
                          </React.Fragment>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </article>

            <article className="card">
              <div className="checks-header">
                <div className="section-head">
                  <h2>PRD Conformance</h2>
                  <span className="section-meta">
                    {filteredChecks.length}/{checks.length} visible
                  </span>
                </div>
                {checks.length > 0 && (
                  <div className="check-filters">
                    {[
                      { key: 'all', label: 'All', count: checks.length },
                      { key: 'pass', label: 'Pass', count: passing },
                      { key: 'warn', label: 'Warn', count: warn },
                      { key: 'fail', label: 'Fail', count: fail },
                    ].map((f) => (
                      <button
                        key={f.key}
                        className={`check-filter-btn${checkFilter === f.key ? ' active' : ''}${f.key !== 'all' ? ` check-filter-${f.key}` : ''}`}
                        onClick={() => setCheckFilter(f.key)}
                      >
                        {f.label} <span className="check-filter-count">{f.count}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
              {checks.length === 0 ? (
                <EmptyState message="No conformance checks available" icon="{}" />
              ) : filteredChecks.length === 0 ? (
                <EmptyState message={`No ${checkFilter} checks found`} icon="{}" />
              ) : (
                <div className="table-wrap checks-wrap">
                  <table className="checks-table">
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
                      {filteredChecks.map((check, index) => {
                        const observedText = JSON.stringify(check.observed, null, 2) ?? 'null';
                        const expectedText = JSON.stringify(check.expected, null, 2) ?? 'null';

                        return (
                          <tr key={`${check.file}-${check.id}-${index}`} className={check.status === 'fail' ? 'fail-row' : ''}>
                            <td>
                              <StatusPill status={check.status} />
                            </td>
                            <td className="check-title-cell">
                              <span className="check-title-text">{check.title}</span>
                              {isCrossFileCheck(check) && <span className="cross-file-badge">cross-file</span>}
                            </td>
                            <td className="file-name">{check.file}</td>
                            <td className="check-value">
                              <pre title={observedText}>{observedText}</pre>
                            </td>
                            <td className="check-value">
                              <pre title={expectedText}>{expectedText}</pre>
                            </td>
                            <td>{check.details}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </article>
          </section>

          <article className="card preview-panel">
            <div className="preview-header">
              <div className="preview-title-wrap">
                <h2>File Preview</h2>
                {selectedFile ? (
                  <span className="preview-source file-name">{selectedFile}</span>
                ) : (
                  <span className="preview-source muted">No file selected</span>
                )}
              </div>
              {selectedFile && (
                <label className="row-count-label">
                  Rows
                  <select
                    className="row-count-select"
                    value={previewRows}
                    onChange={(e) => setPreviewRows(Number(e.target.value))}
                  >
                    <option value={10}>10</option>
                    <option value={20}>20</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                  </select>
                </label>
              )}
            </div>
            {selectedFile ? (
              previewLoading ? (
                <div className="preview-loading">
                  <span className="preview-loading-text">Loading preview...</span>
                  <div className="skeleton skeleton-preview-line" />
                  <div className="skeleton skeleton-preview-line" style={{ width: '85%' }} />
                  <div className="skeleton skeleton-preview-line" style={{ width: '70%' }} />
                  <div className="skeleton skeleton-preview-line" style={{ width: '90%' }} />
                  <div className="skeleton skeleton-preview-line" style={{ width: '60%' }} />
                </div>
              ) : preview?.error ? (
                <div className="preview-error">
                  <span>!</span>
                  <span>{preview.error}</span>
                </div>
              ) : preview?.preview_rows?.length > 0 ? (
                <div className="preview-code-block">
                  <table className="preview-table">
                    <thead>
                      <tr>
                        {Object.keys(preview.preview_rows[0] || {}).map((col) => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {preview.preview_rows.map((row, i) => (
                        <tr key={i}>
                          {Object.values(row).map((val, j) => (
                            <td key={j}>{val == null ? '' : String(val)}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : preview?.content != null ? (
                <div className="preview-code-block">
                  <pre>{preview.content}</pre>
                </div>
              ) : (
                <div className="preview-code-block">
                  <pre>{JSON.stringify(preview, null, 2)}</pre>
                </div>
              )
            ) : (
              <EmptyState message="Select a file from the table to view a preview" icon="::" />
            )}
          </article>
        </>
      )}

      {loading && payload === null && (
        <section className="grid panel-loading">
          <article className="card wide">
            <div className="section-head">
              <h2>Data Files</h2>
            </div>
            <div>
              <SkeletonRow />
              <SkeletonRow />
              <SkeletonRow />
            </div>
          </article>
          <article className="card">
            <div className="section-head">
              <h2>PRD Conformance</h2>
            </div>
            <div>
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
