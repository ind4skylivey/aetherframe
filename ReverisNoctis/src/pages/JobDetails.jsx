import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useFetch } from '../hooks/useApi';

function JobDetails() {
  const { jobId } = useParams();
  const { data: job, loading: loadJob } = useFetch(`/jobs/${jobId}`);
  const { data: findings, loading: loadFindings } = useFetch(`/jobs/${jobId}/findings`);
  const { data: artifacts, loading: loadArtifacts } = useFetch(`/jobs/${jobId}/artifacts`);
  const { data: events, loading: loadEvents } = useFetch(`/jobs/${jobId}/events`);

  const [activeTab, setActiveTab] = useState('findings');

  const getSeverityColor = (severity) => {
    const colors = {
      critical: '#ff3366',
      high: '#ff6b6b',
      medium: '#ffd93d',
      low: '#6bcf7f',
      info: '#6af0ff',
    };
    return colors[severity] || '#9fb0d0';
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

  if (loadJob) {
    return <div className="loading">Loading job details...</div>;
  }

  if (!job) {
    return <div className="error-state">Job not found</div>;
  }

  return (
    <div className="job-details">
      <header className="job-details-header">
        <div>
          <p className="eyebrow">Job Analysis</p>
          <h1>Job #{job.id}</h1>
          <div className="job-meta-row">
            <span className={`pill pill-${job.status}`}>{job.status}</span>
            <span className="meta">Pipeline: {job.pipeline_id || 'default'}</span>
            <span className="meta">Created: {new Date(job.created_at).toLocaleString()}</span>
          </div>
        </div>
        <div className="job-stats">
          {job.meta?.risk_score !== undefined && (
            <div className="stat-card">
              <div className="stat-label">Risk Score</div>
              <div className="stat-value" style={{ color: job.meta.risk_score > 0.7 ? '#ff3366' : job.meta.risk_score > 0.4 ? '#ffd93d' : '#6bcf7f' }}>
                {(job.meta.risk_score * 100).toFixed(0)}%
              </div>
            </div>
          )}
        </div>
      </header>

      <div className="panel">
        <strong>Target Information</strong>
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">Target Path</span>
            <span className="mono">{job.target}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Pipeline</span>
            <span>{job.pipeline_id || 'default'}</span>
          </div>
          {job.meta?.execution_time_ms && (
            <div className="info-item">
              <span className="info-label">Execution Time</span>
              <span className="mono">{job.meta.execution_time_ms}ms</span>
            </div>
          )}
        </div>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'findings' ? 'active' : ''}`}
          onClick={() => setActiveTab('findings')}
        >
          🔍 Findings {findings && `(${findings.length})`}
        </button>
        <button
          className={`tab ${activeTab === 'artifacts' ? 'active' : ''}`}
          onClick={() => setActiveTab('artifacts')}
        >
          📦 Artifacts {artifacts && `(${artifacts.length})`}
        </button>
        <button
          className={`tab ${activeTab === 'events' ? 'active' : ''}`}
          onClick={() => setActiveTab('events')}
        >
          📡 Events {events && `(${events.length})`}
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'findings' && (
          <div className="findings-section">
            {loadFindings && <div className="loading">Loading findings...</div>}
            {!loadFindings && findings && findings.length === 0 && (
              <div className="empty-state">No findings generated for this job</div>
            )}
            {!loadFindings && findings && findings.length > 0 && (
              <div className="findings-list">
                {findings.map((finding) => (
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
                      <span className="pill pill-ghost">{finding.category}</span>
                    </div>
                    <h3 className="finding-title">{finding.title}</h3>
                    <p className="finding-description">{finding.description}</p>

                    {finding.evidence && finding.evidence.length > 0 && (
                      <div className="evidence-section">
                        <strong>Evidence:</strong>
                        <div className="evidence-list">
                          {finding.evidence.map((ev, idx) => (
                            <div key={idx} className="evidence-item">
                              <span className="evidence-type">{ev.type}</span>
                              {ev.location && <span className="evidence-location mono">{ev.location}</span>}
                              {ev.value && <div className="evidence-value mono">{ev.value}</div>}
                              {ev.context && <div className="evidence-context meta">{ev.context}</div>}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {finding.tags && finding.tags.length > 0 && (
                      <div className="finding-tags">
                        {finding.tags.map((tag, idx) => (
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
        )}

        {activeTab === 'artifacts' && (
          <div className="artifacts-section">
            {loadArtifacts && <div className="loading">Loading artifacts...</div>}
            {!loadArtifacts && artifacts && artifacts.length === 0 && (
              <div className="empty-state">No artifacts generated for this job</div>
            )}
            {!loadArtifacts && artifacts && artifacts.length > 0 && (
              <div className="artifacts-grid">
                {artifacts.map((artifact) => (
                  <div key={artifact.id} className="artifact-card">
                    <div className="artifact-icon">
                      {artifact.artifact_type === 'json' && '📄'}
                      {artifact.artifact_type === 'html' && '🌐'}
                      {artifact.artifact_type === 'binary' && '🔧'}
                      {artifact.artifact_type === 'image' && '🖼️'}
                    </div>
                    <h3 className="artifact-name">{artifact.name}</h3>
                    <p className="artifact-description">{artifact.description}</p>
                    <div className="artifact-meta">
                      <span className="pill pill-ghost">{artifact.artifact_type}</span>
                      <span className="meta mono">{(artifact.size_bytes / 1024).toFixed(1)} KB</span>
                    </div>
                    {artifact.uri && (
                      <a href={artifact.uri.replace('file://', '/artifacts/')} className="artifact-link" download>
                        Download →
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'events' && (
          <div className="events-section">
            {loadEvents && <div className="loading">Loading events...</div>}
            {!loadEvents && events && events.length === 0 && (
              <div className="empty-state">No events recorded for this job</div>
            )}
            {!loadEvents && events && events.length > 0 && (
              <div className="events-timeline">
                {events.map((event) => (
                  <div key={event.id} className="event-item">
                    <div className="event-marker"></div>
                    <div className="event-content">
                      <div className="event-header">
                        <span className="pill pill-ghost">{event.event_type}</span>
                        <span className="pill pill-ghost">{event.source}</span>
                        <span className="meta">{new Date(event.ts).toLocaleTimeString()}</span>
                      </div>
                      {event.payload && (
                        <pre className="event-payload mono">{JSON.stringify(event.payload, null, 2)}</pre>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default JobDetails;
