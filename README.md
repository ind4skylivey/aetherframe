# ⚡ AetherFrame - Advanced Malware Analysis Platform

<div align="center">

![Status](https://img.shields.io/badge/status-production--ready-success)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/frontend-React-61DAFB)
![License](https://img.shields.io/badge/license-MIT-green)

**Enterprise-grade reverse engineering and malware analysis platform with real-time threat intelligence**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Screenshots](#-screenshots) • [Roadmap](#-roadmap)

</div>

---

## 🎯 Overview

AetherFrame is a comprehensive malware analysis platform combining powerful backend processing with a stunning, data-rich frontend interface. Built for security researchers, malware analysts, and threat intelligence teams.

### Key Capabilities

- 🛡️ **Multi-stage Analysis Pipelines** - Quick triage → Deep static → Dynamic analysis
- 🔍 **Advanced Threat Detection** - 50+ anti-analysis techniques, packing, obfuscation
- 📊 **Real-time Analytics** - Interactive dashboards with 6 chart types
- 🎨 **Premium UI/UX** - Dark theme with glassmorphism and micro-animations
- 🔄 **Live Monitoring** - Auto-refresh system with 5-second updates
- 📦 **Artifact Management** - Organized storage with MinIO integration

---

## ✨ Features

### Backend (FastAPI + PostgreSQL + Celery)

- **Pipeline Orchestration**

  - Modular plugin system
  - Configurable stages with conditional execution
  - Celery-based async task processing

- **Detection Engines**

  - **Umbriel**: Anti-debugging, anti-VM, anti-Frida detection
  - **Noema**: Intent classification and behavioral analysis
  - **Valkyrie**: Binary validation and integrity checks
  - **Static Analyzer**: Comprehensive static analysis
  - **LainTrace**: Dynamic tracing and instrumentation

- **Data Management**
  - PostgreSQL for structured data (jobs, findings, artifacts)
  - MinIO for artifact storage
  - Redis for task queue management
  - Alembic for database migrations

### Frontend (React + Vite + Recharts)

- **Six Main Views**

  - **Dashboard**: System overview and recent jobs
  - **Analytics** ⭐: 6 interactive charts and threat intelligence
  - **Launch**: Interactive pipeline submission interface
  - **Job Details**: Comprehensive analysis results
  - **Findings**: Filterable threat browser
  - **Artifacts**: Downloadable reports gallery

- **Visualizations**

  - Severity distribution (Pie chart)
  - Category breakdown (Bar chart)
  - Job timeline (Line chart)
  - Threat radar (Radar chart)
  - Risk score trends (Line chart)
  - Confidence distribution (Bar chart)

- **Real-time Features**
  - LiveMonitor sidebar with auto-refresh
  - System health indicators
  - Live metrics counters
  - HMR for instant development updates

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 16+ & npm
- Python 3.11+

### 1. Clone & Setup

```bash
git clone <repository-url>
cd aetherframe-ecosystem
```

### 2. Start Backend

```bash
cd AetherFrame
docker-compose up -d
```

Services will start:

- API: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- MinIO: http://localhost:9001

### 3. Start Frontend

```bash
cd ReverisNoctis
npm install
npm run dev
```

Frontend available at: http://localhost:3000

### 4. Run Analysis (CLI)

```bash
cd ReverisNoctis
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run quicklook pipeline
python cli/main.py run /path/to/binary.exe --pipeline quicklook --wait
```

---

## 📊 Pipeline Types

| Pipeline          | Description                                   | Speed  | Depth      |
| ----------------- | --------------------------------------------- | ------ | ---------- |
| **quicklook**     | Fast triage with anti-analysis detection      | ⚡⚡⚡ | ⭐         |
| **deep-static**   | Comprehensive static analysis + decompilation | ⚡⚡   | ⭐⭐⭐     |
| **dynamic-first** | Runtime analysis with Frida instrumentation   | ⚡     | ⭐⭐⭐⭐   |
| **full-audit**    | Complete analysis: static + dynamic + ML      | ⚡     | ⭐⭐⭐⭐⭐ |

---

## 🎨 Screenshots

### Dashboard

![Dashboard](docs/screenshots/dashboard.png)
_Main dashboard with job overview and system status_

### Analytics

![Analytics](docs/screenshots/analytics.png)
_Interactive analytics with 6 chart types_

### Job Details

![Job Details](docs/screenshots/job-details.png)
_Comprehensive findings, artifacts, and events view_

---

## 📁 Project Structure

```
aetherframe-ecosystem/
├── AetherFrame/              # Backend (FastAPI)
│   ├── aetherframe/
│   │   ├── api/             # REST API endpoints
│   │   ├── core/            # Pipeline engine, tasks
│   │   ├── plugins/         # Detection plugins
│   │   ├── schemas/         # Pydantic models
│   │   └── utils/           # Helpers
│   └── docker-compose.yml
│
├── ReverisNoctis/           # Frontend (React)
│   ├── src/
│   │   ├── pages/           # 6 main pages
│   │   ├── components/      # Charts, LiveMonitor
│   │   ├── hooks/           # API hooks
│   │   └── styles.css       # Premium CSS
│   ├── cli/                 # CLI tool
│   └── package.json
│
└── tests/
    └── samples/             # Test binaries
```

---

## 🔧 Configuration

### Environment Variables

**Backend** (`.env`):

```bash
POSTGRES_URL=postgresql://user:pass@localhost:5432/aetherframe
REDIS_HOST=localhost
REDIS_PORT=6379
MINIO_ENDPOINT=localhost:9000
AETHERFRAME_LICENSE_ENFORCE=false  # For development
```

**Frontend** (`.env`):

```bash
VITE_API_BASE=http://localhost:8000
```

---

## 📖 Documentation

- [Backend Success Summary](backend_success_summary.md)
- [Phase 2: Frontend Complete](PHASE2_FRONTEND_COMPLETE.md)
- [Phase 3: Analytics Complete](PHASE3_ANALYTICS_COMPLETE.md)
- [Project Summary](PROJECT_SUMMARY.md)

### API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🛠️ Development

### Backend Development

```bash
cd AetherFrame
docker-compose up -d postgres redis minio  # Start dependencies only
python -m aetherframe.main  # Run FastAPI in dev mode
celery -A aetherframe.core.celery_app worker --loglevel=info  # Start worker
```

### Frontend Development

```bash
cd ReverisNoctis
npm run dev  # Starts Vite dev server with HMR
```

### Database Migrations

```bash
cd AetherFrame
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

---

## 🗺️ Roadmap

### ✅ Phase 1: Backend Preparation (Complete)

- Pipeline execution
- Plugin system
- Data persistence

### ✅ Phase 2: Frontend Scaffolding (Complete)

- React SPA with routing
- 5 main pages
- Premium design system

### ✅ Phase 3: Analytics & Real-time (Complete)

- 6 interactive charts
- Live monitoring
- Enhanced hooks

### 🚧 Phase 4: Desktop Packaging (Planned)

- Electron/Tauri integration
- Native installers
- System tray support
- Desktop notifications

### 💡 Future Enhancements

- WebSocket real-time push
- Job comparison tool
- PDF/CSV export
- Custom dashboards
- Alert system
- Multi-user auth
- Cloud deployment
- ML-powered classification

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👏 Acknowledgments

- FastAPI for the excellent web framework
- React team for the UI library
- Recharts for beautiful visualizations
- PostgreSQL, Redis, and MinIO teams

---

## 📞 Contact

**Project**: AetherFrame Ecosystem
**Status**: Production Ready (v0.1.0)
**Last Updated**: 2025-12-14

---

<div align="center">

**Built with ⚡ by Antigravity AI**

[⬆ back to top](#-aetherframe---advanced-malware-analysis-platform)

</div>
