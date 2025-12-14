import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useFetch } from '../hooks/useApi';

function FindingsView() {
  const { data: findings, loading } = useFetch('/findings');
  const [filter, setFilter] = useState({ severity: 'all', category: 'all' });

  const getSeverityColor = (severity) => {
    const colors = {
      critical: '#ff3366',
      high: '#ff6b6b',
      medium: '#ffd93d',
      low: '#6bcf7f',
      info: '#6af0ff',
    };
    return colors[severity] ||'#9fb0d0';
  };

  const getSeverityIcon = (severity) => {
    const icons = {
      critical: '🔴',
      high: '🟠',
      medium: '🟡',
      low: '🟢',
      info: '🔵',
    };
    return icons[severity] || '⚪';
  };

  const severities = findings ? [...new Set(findings.map(f => f.severity))] : [];
  const categories = findings ? [...new Set(findings.map(f => f.category))] : [];

  const filteredFindings = findings?.filter(f => {
    if (filter.severity !== 'all' && f.severity !== filter.severity) return false;
    if (filter.category !== 'all' && f.category !== filter.category) return false;
    return true;
  }) || [];

  return (
    <div className="findings-view">
      <header className="hero">
        <div>
          <p className="eyebrow">Threat Intelligence</p>
          <h1>All Findings</h1>
          <p className="lede">
            Comprehensive view of all detected threats, vulnerabilities, and analysis results
          </p>
        </div>
        <div className="hero-metrics">
          <div className="hero-metric">
            <div className="label">Total</div>
            <div className="value">{findings?.length || 0}</div>
          </div>
          <div className="hero-metric">
            <div className="label">Critical</div>
            <div className="value" style={{ color: '#ff3366' }}>
              {findings?.filter(f => f.severity === 'critical').length || 0}
            </div>
          </div>
          <div className="hero-metric">
            <div className="label">High</div>
            <div className="value" style={{ color: '#ff6b6b' }}>
              {findings?.filter(f => f.severity === 'high').length || 0}
            </div>
          </div>
        </div>
      </header>

      <div className="filters">
        <div className="filter-group">
          <label>Severity</label>
          <select value={filter.severity} onChange={(e) => setFilter({ ...filter, severity: e.target.value })}>
            <option value="all">All Severities</option>
            {severities.map(sev => (
              <option key={sev} value={sev}>{sev}</option>
            ))}
          </select>
        </div>
        <div className="filter-group">
          <label>Category</label>
          <select value={filter.category} onChange={(e) => setFilter({ ...filter, category: e.target.value })}>
            <option value="all">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
        <div className="filter-stats">
          Showing {filteredFindings.length} of {findings?.length || 0} findings
        </div>
      </div>

      {loading && <div className="loading">Loading findings...</div>}

      {!loading && filteredFindings.length === 0 && (
        <div className="empty-state">No findings match the current filters</div>
      )}

      {!loading && filteredFindings.length > 0 && (
        <div className="findings-list">
          {filteredFindings.map((finding) => (
            <div key={finding.id} className="finding-card">
              <div className="finding-header">
                <div className="finding-severity">
                  <span className="severity-icon">{getSeverityIcon(finding.severity)}</span>
                  <span
                    className="pill"
                    style={{ borderColor: getSeverityColor(finding.severity), color: getSeverityColor(finding.severity) }}
                  >
                    {finding.severity}
                  </span>
                </div>
                <div className="finding-meta-row">
                  <span className="pill pill-ghost">{finding.category}</span>
                  <Link to={`/job/${finding.job_id}`} className="job-link mono">
                    Job #{finding.job_id}
                  </Link>
                </div>
              </div>
              <h3 className="finding-title">{finding.title}</h3>
              <p className="finding-description">{finding.description}</p>

              {finding.evidence && finding.evidence.length > 0 && (
                <div className="evidence-section">
                  <strong>Evidence:</strong>
                  <div className="evidence-list">
                    {finding.evidence.slice(0, 3).map((ev, idx) => (
                      <div key={idx} className="evidence-item">
                        <span className="evidence-type">{ev.type}</span>
                        {ev.location && <span className="evidence-location mono">{ev.location}</span>}
                        {ev.value && <div className="evidence-value mono">{ev.value.substring(0, 100)}</div>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {finding.tags && finding.tags.length > 0 && (
                <div className="finding-tags">
                  {finding.tags.slice(0, 5).map((tag, idx) => (
                    <span key={idx} className="tag">{tag}</span>
                  ))}
                </div>
              )}

              <div className="finding-footer">
                <span className="meta">Confidence: {(finding.confidence * 100).toFixed(0)}%</span>
                {finding.created_at && (
                  <span className="meta">{new Date(finding.created_at).toLocaleString()}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default FindingsView;
