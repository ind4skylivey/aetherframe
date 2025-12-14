import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom';
import Analytics from './pages/Analytics';
import ArtifactsView from './pages/ArtifactsView';
import Dashboard from './pages/Dashboard';
import FindingsView from './pages/FindingsView';
import JobDetails from './pages/JobDetails';
import PipelineLauncher from './pages/PipelineLauncher';

function App() {
  return (
    <BrowserRouter>
      <div className="page">
        <nav className="main-nav">
          <div className="nav-brand">
            <div className="nav-logo"></div>
            <div>
              <h1 className="nav-title">Reveris Noctis</h1>
              <p className="nav-subtitle">AetherFrame Operations Console</p>
            </div>
          </div>
          <div className="nav-links">
            <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              <span className="nav-icon">📊</span>
              Dashboard
            </NavLink>
            <NavLink to="/analytics" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              <span className="nav-icon">📈</span>
              Analytics
            </NavLink>
            <NavLink to="/launch" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              <span className="nav-icon">🚀</span>
              Launch
            </NavLink>
            <NavLink to="/findings" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              <span className="nav-icon">🔍</span>
              Findings
            </NavLink>
            <NavLink to="/artifacts" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              <span className="nav-icon">📦</span>
              Artifacts
            </NavLink>
          </div>
          <LiveMonitor />
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/launch" element={<PipelineLauncher />} />
            <Route path="/job/:jobId" element={<JobDetails />} />
            <Route path="/findings" element={<FindingsView />} />
            <Route path="/artifacts" element={<ArtifactsView />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
