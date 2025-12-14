# 🎉 AetherFrame v0.1.0 - First Official Release

## Advanced Malware Analysis Platform

We're excited to announce the **first official release** of AetherFrame! This release brings a complete malware analysis platform with native desktop applications for Linux, macOS, and Windows.

---

## ⚡ What's New

### 🖥️ **Native Desktop Applications**

- **Windows**: .exe and .msi installers
- **macOS**: .dmg disk image and .app bundle
- **Linux**: AppImage (portable) and .deb package (Debian/Ubuntu)

All desktop apps feature:

- System tray integration
- Hide to tray (instead of closing)
- Native window management
- ~10-15 MB size (Tauri-based, not Electron!)

### 🚀 **Core Features**

#### **Backend (FastAPI + Celery)**

- Plugin-based malware analysis orchestration
- Async task processing with Celery
- PostgreSQL for structured data
- MinIO for artifact storage
- Redis for task queue and caching

#### **6 Analysis Plugins**

- **Umbriel**: Anti-analysis detection (50+ techniques)
- **Noema**: Intent classification and behavioral analysis
- **Valkyrie**: Binary validation and integrity checks
- **Static Analyzer**: Comprehensive static analysis
- **LainTrace**: Dynamic tracing with Frida
- **Mnemosyne**: State reconstruction from memory dumps

#### **Frontend (React + Vite)**

- Real-time analytics dashboard with 6 chart types (Recharts)
- Live system monitor with auto-refresh
- Interactive pipeline launcher
- Comprehensive job and findings browser
- Downloadable artifacts gallery
- Premium dark theme with glassmorphism

### 🐳 **Docker Deployment**

- All-in-one setup: `./start.sh`
- Docker Compose with all dependencies
- Zero-config local deployment

### 🏗️ **Hybrid Monorepo Structure**

- Independent packages (core, frontend, cli)
- Extractable plugins
- Clear module boundaries
- Professional architecture

---

## 📥 Installation

### Desktop Apps (Recommended)

**Linux:**

```bash
# AppImage (portable, no installation)
chmod +x aetherframe_0.1.0_amd64.AppImage
./aetherframe_0.1.0_amd64.AppImage

# Debian/Ubuntu (installs to system)
sudo dpkg -i aetherframe_0.1.0_amd64.deb
aetherframe
```

**macOS:**

1. Download `AetherFrame_0.1.0_x64.dmg`
2. Open the .dmg file
3. Drag AetherFrame.app to Applications
4. Launch from Applications folder

**Windows:**

1. Download `AetherFrame_0.1.0_x64-setup.exe`
2. Run the installer
3. Follow the installation wizard
4. Launch from Start Menu

### Docker (Alternative)

```bash
git clone https://github.com/ind4skylivey/aetherframe.git
cd aetherframe
./start.sh
```

Access at http://localhost:3000

---

## 🎯 Pipeline Types

- **quicklook**: Fast triage with anti-analysis detection
- **deep-static**: Comprehensive static analysis
- **dynamic-first**: Runtime analysis with Frida
- **full-audit**: Complete analysis (static + dynamic + ML)

---

## 🔧 System Requirements

### Desktop Apps

- **Linux**: Ubuntu 20.04+, Debian 11+, or compatible
- **macOS**: macOS 10.15 (Catalina) or later
- **Windows**: Windows 10 (1803+) or Windows 11
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 500MB for app, additional for samples

### Docker

- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 10GB disk space

---

## 📚 Documentation

- **Quick Start**: See [README.md](https://github.com/ind4skylivey/aetherframe#readme)
- **Desktop App Guide**: [DESKTOP_APP_GUIDE.md](https://github.com/ind4skylivey/aetherframe/blob/main/packages/frontend/DESKTOP_APP_GUIDE.md)
- **Build Instructions**: [BUILD_INSTALLERS.md](https://github.com/ind4skylivey/aetherframe/blob/main/BUILD_INSTALLERS.md)
- **API Docs**: http://localhost:3000/api/docs (after installation)

---

## 🐛 Known Issues

- macOS .icns icon is a placeholder (will be updated in next release)
- Backend must be running separately for desktop app to function
- Auto-updates not yet implemented (planned for v0.2.0)

---

## 🔄 What's Next (v0.2.0)

- [ ] Embedded backend (desktop app includes FastAPI server)
- [ ] Auto-updates via Tauri updater
- [ ] Professional app icons
- [ ] Code signing for trusted installations
- [ ] ML-powered threat classification
- [ ] WebSocket real-time updates
- [ ] Job comparison tool

---

## 🙏 Acknowledgments

This project builds on excellent open-source tools:

- **Tauri** - Native desktop framework
- **FastAPI** - Modern Python web framework
- **Celery** - Distributed task queue
- **Recharts** - React charting library
- **Frida** - Dynamic instrumentation toolkit

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ind4skylivey/aetherframe/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ind4skylivey/aetherframe/discussions)
- **Author**: [@ind4skylivey](https://github.com/ind4skylivey)

---

## 📜 License

MIT License - see [LICENSE](https://github.com/ind4skylivey/aetherframe/blob/main/LICENSE.txt)

---

<p align="center">
  <strong>🎊 Thank you for trying AetherFrame! 🎊</strong>
</p>

<p align="center">
  <a href="https://github.com/ind4skylivey/aetherframe">⭐ Star on GitHub</a> •
  <a href="https://github.com/ind4skylivey/aetherframe/issues">Report Bug</a> •
  <a href="https://github.com/ind4skylivey/aetherframe/discussions">Request Feature</a>
</p>
