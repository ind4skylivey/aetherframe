import { Link } from 'react-router-dom';
import { useFetch } from '../hooks/useApi';

function Dashboard() {
  const { data: status, loading: loadStatus } = useFetch('/status');
  const { data: jobs, loading: loadJobs } = useFetch('/jobs');

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

  const recentJobs = jobs?.slice(0, 10) || [];
  const completedJobs = jobs?.filter(j => j.status === 'completed') || [];
  const failedJobs = jobs?.filter(j => j.status === 'failed') || [];
  const runningJobs = jobs?.filter(j => j.status === 'running') || [];

  return (
    <div className="dashboard">
      <header className="hero">
        <div>
          <p className="eyebrow">AetherFrame Operations Console</p>
          <h1>Analysis Dashboard</h1>
          <p className="lede">
            Real-time monitoring and analysis results from the AetherFrame reverse engineering platform
          </p>
        </div>
        <div className="hero-metrics">
          <div className="hero-metric">
            <div className="label">Total Jobs</div>
            <div className="value">{jobs?.length || 0}</div>
          </div>
          <div className="hero-metric">
            <div className="label">Completed</div>
            <div className="value">{completedJobs.length}</div>
          </div>
          <div className="hero-metric">
            <div className="label">Running</div>
            <div className="value">{runningJobs.length}</div>
          </div>
        </div>
      </header>

      {loadStatus && <div className="loading">Loading system status...</div>}

      {!loadStatus && status && (
        <div className="status-overview">
          <div className="panel">
            <strong>System Status</strong>
            <div className="stat-grid">
              <div className="stat-pill">
                <span className="inline">
                  <span className={`status-dot ${status.healthy ? 'status-online' : 'status-offline'}`} />
                  API
                </span>
                <span className={`pill ${status.healthy ? 'pill-completed' : 'pill-failed'}`}>
                  {status.healthy ? 'Online' : 'Offline'}
                </span>
              </div>
              <div className="stat-pill">
                <span className="inline">
                  <span className={`status-dot ${status.celery_ok ? 'status-online' : 'status-offline'}`} />
                  Celery
                </span>
                <span className={`pill ${status.celery_ok ? 'pill-completed' : 'pill-failed'}`}>
                  {status.celery_ok ? 'Ready' : 'Down'}
                </span>
              </div>
            </div>
          </div>

          <div className="panel">
            <strong>Database Counts</strong>
            <div className="stat-grid">
              <div className="stat-pill">
                Jobs <span className="mono">{status.counts?.jobs || 0}</span>
              </div>
              <div className="stat-pill">
                Findings <span className="mono">{status.counts?.findings || 0}</span>
              </div>
              <div className="stat-pill">
                Artifacts <span className="mono">{status.counts?.artifacts || 0}</span>
              </div>
              <div className="stat-pill">
                Events <span className="mono">{status.counts?.events || 0}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="section-title">
        <h2>Recent Jobs</h2>
        <Link to="/launch" className="action-link">Launch New Analysis →</Link>
      </div>

      {loadJobs && <div className="loading">Loading jobs...</div>}

      {!loadJobs && (
        <div className="jobs-list">
          {recentJobs.map((job) => (
            <Link to={`/job/${job.id}`} key={job.id} className="job-card">
              <div className="job-header">
                <div className="job-id">
                  <span className="mono">#{job.id}</span>
                  <span className={`pill pill-${job.status}`}>{job.status}</span>
                </div>
                <div className="job-meta">
                  {new Date(job.created_at).toLocaleString()}
                </div>
              </div>
              <div className="job-body">
                <div className="job-target">
                  <strong>Target:</strong> {job.target}
                </div>
                <div className="job-pipeline">
                  <strong>Pipeline:</strong> {job.pipeline_id || 'default'}
                </div>
              </div>
              {job.meta?.risk_score !== undefined && (
                <div className="job-footer">
                  <div className="risk-indicator">
                    <span>Risk Score:</span>
                    <div className="risk-bar">
                      <div
                        className="risk-fill"
                        style={{
                          width: `${job.meta.risk_score * 100}%`,
                          backgroundColor: job.meta.risk_score > 0.7 ? '#ff3366' : job.meta.risk_score > 0.4 ? '#ffd93d' : '#6bcf7f'
                        }}
                      />
                    </div>
                    <span className="mono">{(job.meta.risk_score * 100).toFixed(0)}%</span>
                  </div>
                </div>
              )}
            </Link>
          ))}

          {recentJobs.length === 0 && (
            <div className="empty-state">
              <p>No jobs yet. <Link to="/launch">Launch your first analysis →</Link></p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Dashboard;
