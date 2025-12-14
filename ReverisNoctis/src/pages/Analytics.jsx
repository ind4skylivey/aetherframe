import {
    CategoryBreakdown,
    ConfidenceDistribution,
    JobTimeline,
    RiskScoreTrend,
    SeverityDistribution,
    ThreatRadar,
} from '../components/Charts';
import { useFetch } from '../hooks/useApi';

function Analytics() {
  const { data: findings, loading: loadFindings } = useFetch('/findings');
  const { data: jobs, loading: loadJobs } = useFetch('/jobs');
  const { data: status } = useFetch('/status');

  const totalFindings = findings?.length || 0;
  const criticalFindings = findings?.filter((f) => f.severity === 'critical').length || 0;
  const highFindings = findings?.filter((f) => f.severity === 'high').length || 0;
  const avgConfidence = findings?.length
    ? (findings.reduce((sum, f) => sum + f.confidence, 0) / findings.length * 100).toFixed(1)
    : 0;

  const completedJobs = jobs?.filter((j) => j.status === 'completed').length || 0;
  const failedJobs = jobs?.filter((j) => j.status === 'failed').length || 0;
  const successRate = jobs?.length
    ? ((completedJobs / jobs.length) * 100).toFixed(1)
    : 0;

  return (
    <div className="analytics">
      <header className="hero">
        <div>
          <p className="eyebrow">Intelligence Dashboard</p>
          <h1>Analytics & Insights</h1>
          <p className="lede">
            Comprehensive analysis and visualization of threat intelligence, job performance, and system metrics
          </p>
        </div>
      </header>

      {/* Key Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">🔍</div>
          <div className="metric-content">
            <div className="metric-label">Total Findings</div>
            <div className="metric-value">{totalFindings}</div>
            <div className="metric-detail">
              <span className="critical-badge">{criticalFindings} critical</span>
              <span className="high-badge">{highFindings} high</span>
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">⚡</div>
          <div className="metric-content">
            <div className="metric-label">Success Rate</div>
            <div className="metric-value">{successRate}%</div>
            <div className="metric-detail">
              {completedJobs} completed / {failedJobs} failed
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">🎯</div>
          <div className="metric-content">
            <div className="metric-label">Avg Confidence</div>
            <div className="metric-value">{avgConfidence}%</div>
            <div className="metric-detail">
              Across all findings
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">🔄</div>
          <div className="metric-content">
            <div className="metric-label">Active Jobs</div>
            <div className="metric-value">{jobs?.filter((j) => j.status === 'running').length || 0}</div>
            <div className="metric-detail">
              Currently processing
            </div>
          </div>
        </div>
      </div>

      {loadFindings || loadJobs ? (
        <div className="loading">Loading analytics data...</div>
      ) : (
        <>
          {/* Primary Charts Row */}
          <div className="charts-row-2">
            <div className="panel chart-panel">
              <SeverityDistribution findings={findings} />
            </div>
            <div className="panel chart-panel">
              <ThreatRadar findings={findings} />
            </div>
          </div>

          {/* Secondary Charts Row */}
          <div className="charts-row-2">
            <div className="panel chart-panel">
              <CategoryBreakdown findings={findings} />
            </div>
            <div className="panel chart-panel">
              <RiskScoreTrend jobs={jobs} />
            </div>
          </div>

          {/* Tertiary Charts Row */}
          <div className="charts-row-2">
            <div className="panel chart-panel">
              <JobTimeline jobs={jobs} />
            </div>
            <div className="panel chart-panel">
              <ConfidenceDistribution findings={findings} />
            </div>
          </div>

          {/* System Health */}
          <div className="panel">
            <strong>System Health Overview</strong>
            <div className="health-grid">
              <div className="health-item">
                <div className="health-label">API Status</div>
                <div className={`health-status ${status?.healthy ? 'online' : 'offline'}`}>
                  {status?.healthy ? '🟢 Online' : '🔴 Offline'}
                </div>
              </div>
              <div className="health-item">
                <div className="health-label">Celery Worker</div>
                <div className={`health-status ${status?.celery_ok ? 'online' : 'offline'}`}>
                  {status?.celery_ok ? '🟢 Ready' : '🔴 Down'}
                </div>
              </div>
              <div className="health-item">
                <div className="health-label">Database</div>
                <div className="health-value">
                  {status?.counts?.jobs || 0} jobs / {status?.counts?.findings || 0} findings
                </div>
              </div>
              <div className="health-item">
                <div className="health-label">Events Recorded</div>
                <div className="health-value">
                  {status?.counts?.events || 0} total
                </div>
              </div>
            </div>
          </div>

          {/* Threat Intelligence Summary */}
          {findings && findings.length > 0 && (
            <div className="panel">
              <strong>Threat Intelligence Summary</strong>
              <div className="threat-summary">
                <div className="threat-stat">
                  <span className="threat-label">Most Common Category:</span>
                  <span className="threat-value">
                    {Object.entries(
                      findings.reduce((acc, f) => {
                        acc[f.category] = (acc[f.category] || 0) + 1;
                        return acc;
                      }, {})
                    ).sort((a, b) => b[1] - a[1])[0]?.[0]?.replace(/_/g, ' ') || 'N/A'}
                  </span>
                </div>
                <div className="threat-stat">
                  <span className="threat-label">Highest Risk Job:</span>
                  <span className="threat-value">
                    #{jobs?.filter((j) => j.meta?.risk_score).sort((a, b) =>
                      (b.meta?.risk_score || 0) - (a.meta?.risk_score || 0)
                    )[0]?.id || 'N/A'}
                  </span>
                </div>
                <div className="threat-stat">
                  <span className="threat-label">Latest Analysis:</span>
                  <span className="threat-value">
                    {jobs?.[0] ? new Date(jobs[0].created_at).toLocaleString() : 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Analytics;
