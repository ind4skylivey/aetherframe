import { Link } from 'react-router-dom';
import { useFetch } from '../hooks/useApi';

function ArtifactsView() {
  const { data: artifacts, loading } = useFetch('/artifacts');

  const getArtifactIcon = (type) => {
    const icons = {
      json: '📄',
      html: '🌐',
      binary: '🔧',
      image: '🖼️',
      text: '📝',
    };
    return icons[type] || '📦';
  };

  const groupedArtifacts = artifacts?.reduce((acc, artifact) => {
    const type = artifact.artifact_type;
    if (!acc[type]) acc[type] = [];
    acc[type].push(artifact);
    return acc;
  }, {}) || {};

  return (
    <div className="artifacts-view">
      <header className="hero">
        <div>
          <p className="eyebrow">Analysis Outputs</p>
          <h1>Artifacts Gallery</h1>
          <p className="lede">
            All generated reports, dumps, and analysis outputs from completed jobs
          </p>
        </div>
        <div className="hero-metrics">
          <div className="hero-metric">
            <div className="label">Total</div>
            <div className="value">{artifacts?.length || 0}</div>
          </div>
          <div className="hero-metric">
            <div className="label">JSON Reports</div>
            <div className="value">{artifacts?.filter(a => a.artifact_type === 'json').length || 0}</div>
          </div>
          <div className="hero-metric">
            <div className="label">Total Size</div>
            <div className="value">
              {((artifacts?.reduce((sum, a) => sum + a.size_bytes, 0) || 0) / 1024 / 1024).toFixed(1)} MB
            </div>
          </div>
        </div>
      </header>

      {loading && <div className="loading">Loading artifacts...</div>}

      {!loading && artifacts && artifacts.length === 0 && (
        <div className="empty-state">No artifacts generated yet</div>
      )}

      {!loading && artifacts && artifacts.length > 0 && (
        <div className="artifacts-grouped">
          {Object.entries(groupedArtifacts).map(([type, items]) => (
            <div key={type} className="artifact-group">
              <h2 className="group-title">
                <span>{getArtifactIcon(type)}</span>
                {type} Artifacts ({items.length})
              </h2>
              <div className="artifacts-grid">
                {items.map((artifact) => (
                  <div key={artifact.id} className="artifact-card">
                    <div className="artifact-icon-large">
                      {getArtifactIcon(artifact.artifact_type)}
                    </div>
                    <h3 className="artifact-name">{artifact.name}</h3>
                    <p className="artifact-description">{artifact.description}</p>
                    <div className="artifact-meta-grid">
                      <div className="artifact-meta-item">
                        <span className="label">Type</span>
                        <span className="pill pill-ghost">{artifact.artifact_type}</span>
                      </div>
                      <div className="artifact-meta-item">
                        <span className="label">Size</span>
                        <span className="mono">{(artifact.size_bytes / 1024).toFixed(1)} KB</span>
                      </div>
                      <div className="artifact-meta-item">
                        <span className="label">Job</span>
                        <Link to={`/job/${artifact.job_id}`} className="job-link mono">
                          #{artifact.job_id}
                        </Link>
                      </div>
                      {artifact.sha256 && (
                        <div className="artifact-meta-item full-width">
                          <span className="label">SHA-256</span>
                          <span className="mono small">{artifact.sha256.substring(0, 24)}...</span>
                        </div>
                      )}
                    </div>
                    {artifact.created_at && (
                      <div className="artifact-timestamp meta">
                        {new Date(artifact.created_at).toLocaleString()}
                      </div>
                    )}
                    {artifact.uri && (
                      <a href={artifact.uri.replace('file://', '/artifacts/')} className="artifact-download-btn" download>
                        <span>📥</span> Download
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ArtifactsView;
