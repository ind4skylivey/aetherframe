import { useLiveData } from '../hooks/useApi';

function LiveMonitor() {
  const { data: status, lastUpdate } = useLiveData('/status', 5000);

  if (!status) return null;

  const formatTime = (date) => {
    if (!date) return '';
    return date.toLocaleTimeString();
  };

  return (
    <div className="live-monitor">
      <div className="monitor-header">
        <span className="monitor-title">System Monitor</span>
        {lastUpdate && (
          <span className="monitor-time">{formatTime(lastUpdate)}</span>
        )}
      </div>

      <div className="monitor-stats">
        <div className="monitor-stat">
          <div className={`monitor-dot ${status.healthy ? 'online' : 'offline'}`} />
          <span>API</span>
        </div>
        <div className="monitor-stat">
          <div className={`monitor-dot ${status.celery_ok ? 'online' : 'offline'}`} />
          <span>Worker</span>
        </div>
      </div>

      <div className="monitor-counts">
        <div className="monitor-count">
          <span className="count-value">{status.counts?.jobs || 0}</span>
          <span className="count-label">Jobs</span>
        </div>
        <div className="monitor-count">
          <span className="count-value">{status.counts?.findings || 0}</span>
          <span className="count-label">Findings</span>
        </div>
        <div className="monitor-count">
          <span className="count-value">{status.counts?.artifacts || 0}</span>
          <span className="count-label">Artifacts</span>
        </div>
      </div>

      <div className="monitor-pulse">
        <div className="pulse-indicator"></div>
        <span>Live</span>
      </div>
    </div>
  );
}

export default LiveMonitor;
