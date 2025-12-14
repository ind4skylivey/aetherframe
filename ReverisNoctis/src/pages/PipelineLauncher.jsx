import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';

const PIPELINES = [
  { id: 'quicklook', name: 'Quick Look', description: 'Fast triage: anti-analysis, basic static, intent detection' },
  { id: 'deep-static', name: 'Deep Static', description: 'Comprehensive static analysis with detailed decompilation' },
  { id: 'dynamic-first', name: 'Dynamic First', description: 'Runtime analysis with Frida instrumentation' },
  { id: 'full-audit', name: 'Full Audit', description: 'Complete analysis: static, dynamic, and threat modeling' },
];

function PipelineLauncher() {
  const navigate = useNavigate();
  const { post } = useApi();
  const [form, setForm] = useState({
    target: '',
    pipeline_id: 'quicklook',
    tags: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      const payload = {
        target: form.target,
        pipeline_id: form.pipeline_id,
        tags: form.tags ? form.tags.split(',').map(t => t.trim()) : [],
      };

      const job = await post('/jobs', payload);
      navigate(`/job/${job.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="pipeline-launcher">
      <header className="hero">
        <div>
          <p className="eyebrow">Analysis Orchestration</p>
          <h1>Launch Pipeline</h1>
          <p className="lede">
            Submit a binary for analysis using one of the configured pipelines
          </p>
        </div>
      </header>

      <div className="launch-content">
        <div className="panel launch-form-panel">
          <strong>Configuration</strong>
          <form onSubmit={handleSubmit} className="launch-form">
            <label>
              Target File Path
              <input
                type="text"
                value={form.target}
                onChange={(e) => setForm({ ...form, target: e.target.value })}
                placeholder="/path/to/binary.exe"
                required
              />
              <span className="input-hint">Absolute path to the target binary on the server</span>
            </label>

            <label>
              Pipeline
              <div className="pipeline-selector">
                {PIPELINES.map((pipeline) => (
                  <button
                    key={pipeline.id}
                    type="button"
                    className={`pipeline-option ${form.pipeline_id === pipeline.id ? 'selected' : ''}`}
                    onClick={() => setForm({ ...form, pipeline_id: pipeline.id })}
                  >
                    <div className="pipeline-option-name">{pipeline.name}</div>
                    <div className="pipeline-option-desc">{pipeline.description}</div>
                  </button>
                ))}
              </div>
            </label>

            <label>
              Tags (optional)
              <input
                type="text"
                value={form.tags}
                onChange={(e) => setForm({ ...form, tags: e.target.value })}
                placeholder="malware, triage, urgent"
              />
              <span className="input-hint">Comma-separated tags for organization</span>
            </label>

            {error && (
              <div className="error-message">
                <span>⚠️</span> {error}
              </div>
            )}

            <button type="submit" disabled={submitting} className="launch-button">
              {submitting ? 'Launching...' : '🚀 Launch Analysis'}
            </button>
          </form>
        </div>

        <div className="panel pipeline-info">
          <strong>Pipeline Details</strong>
          {PIPELINES.filter(p => p.id === form.pipeline_id).map((pipeline) => (
            <div key={pipeline.id} className="pipeline-details">
              <h3>{pipeline.name}</h3>
              <p>{pipeline.description}</p>

              <div className="pipeline-stages">
                <h4>Stages</h4>
                {pipeline.id === 'quicklook' && (
                  <ul>
                    <li><span className="stage-icon">🛡️</span> Anti-Analysis Detection (Umbriel)</li>
                    <li><span className="stage-icon">📊</span> Static Analysis</li>
                    <li><span className="stage-icon">🎯</span> Intent Inference (Noema)</li>
                  </ul>
                )}
                {pipeline.id === 'deep-static' && (
                  <ul>
                    <li><span className="stage-icon">🛡️</span> Anti-Analysis Detection</li>
                    <li><span className="stage-icon">📊</span> Comprehensive Static Analysis</li>
                    <li><span className="stage-icon">🔬</span> Decompilation</li>
                    <li><span className="stage-icon">🎯</span> Threat Modeling</li>
                  </ul>
                )}
                {pipeline.id === 'dynamic-first' && (
                  <ul>
                    <li><span className="stage-icon">🎬</span> Dynamic Tracing (LainTrace)</li>
                    <li><span className="stage-icon">🧠</span> State Reconstruction (Mnemosyne)</li>
                    <li><span className="stage-icon">🔍</span> Behavior Analysis</li>
                  </ul>
                )}
                {pipeline.id === 'full-audit' && (
                  <ul>
                    <li><span className="stage-icon">🛡️</span> Anti-Analysis Detection</li>
                    <li><span className="stage-icon">📊</span> Deep Static Analysis</li>
                    <li><span className="stage-icon">🎬</span> Dynamic Analysis</li>
                    <li><span className="stage-icon">🧠</span> State Reconstruction</li>
                    <li><span className="stage-icon">🎯</span> Threat Intelligence</li>
                  </ul>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default PipelineLauncher;
