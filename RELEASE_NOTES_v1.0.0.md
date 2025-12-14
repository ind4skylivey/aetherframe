# 🎉 AetherFrame v1.0.0 - First Official Release

## 🌟 What's New

AetherFrame is now available as a **complete malware analysis platform** with cross-platform desktop applications!

### ✨ Key Features

- 🚀 **Full Monorepo Ecosystem** - Backend, Frontend, Desktop App, and 6 Analysis Plugins
- 🖥️ **ReverisNoctis Desktop App** - Cross-platform Tauri application for Windows, macOS, and Linux
- 🧩 **6 Analysis Plugins** - Umbriel, Noema, Valkyrie, LainTrace, Mnemosyne, Static Analyzer
- 📊 **Interactive Analytics Dashboard** - Real-time monitoring with 6 chart types
- ⚡ **Automated Pipelines** - FastAPI + Celery orchestration
- 💾 **Complete Stack** - PostgreSQL, Redis, MinIO pre-configured

## 📦 Download

### Windows

- **Installer (MSI)**: `AetherFrame_0.1.0_x64_en-US.msi` - Recommended for Windows users
- **Portable (EXE)**: `AetherFrame_0.1.0_x64-setup.exe` - No installation required

### macOS

- **DMG Package**: `AetherFrame_0.1.0_aarch64.dmg` - For Apple Silicon (M1/M2/M3)
- **App Bundle**: `AetherFrame.app` - Direct application

### Linux

- **Debian/Ubuntu (DEB)**: `aether-frame_0.1.0_amd64.deb` - **Recommended**
- **AppImage**: `aether-frame_0.1.0_amd64.AppImage` - Portable

## 🔧 Installation

### Windows

1. Download `.msi` or `.exe`
2. Run installer and follow wizard
3. Launch from Start Menu

### macOS

1. Download `.dmg`
2. Open and drag `AetherFrame.app` to Applications
3. Launch from Applications folder

### Linux

**Debian/Ubuntu (Recommended):**

```bash
sudo dpkg -i aether-frame_0.1.0_amd64.deb
aether-frame
```

**Arch Linux:**

```bash
# Use debtap to convert
yay -S debtap
sudo debtap -u
debtap aether-frame_0.1.0_amd64.deb
sudo pacman -U aether-frame-*.pkg.tar.zst
```

**AppImage:**

```bash
chmod +x aether-frame_0.1.0_amd64.AppImage
./aether-frame_0.1.0_amd64.AppImage
```

### ⚠️ Linux Troubleshooting

If you encounter a black screen or EGL errors:

```bash
WEBKIT_DISABLE_COMPOSITING_MODE=1 LIBGL_ALWAYS_SOFTWARE=1 ./aether-frame_0.1.0_amd64.AppImage
```

Or use the `.deb` package which handles dependencies better.

## 🌐 Web Application

In addition to the desktop app, you can run the full web stack:

```bash
git clone https://github.com/ind4skylivey/aetherframe.git
cd aetherframe
./start.sh
```

Access at: http://localhost:3000

## 📚 Documentation

- **README**: [Main Documentation](https://github.com/ind4skylivey/aetherframe#readme)
- **Build Guide**: [BUILD_INSTALLERS.md](https://github.com/ind4skylivey/aetherframe/blob/main/BUILD_INSTALLERS.md)
- **API Docs**: Available at `http://localhost:8000/docs` when running

## 🧩 Plugin Ecosystem

All 6 analysis plugins included:

1. **Umbriel** - Anti-analysis detection (50+ techniques)
2. **Noema** - Intent classification and behavioral analysis
3. **Valkyrie** - Binary validation and integrity checks
4. **LainTrace** - Dynamic tracing with Frida instrumentation
5. **Mnemosyne** - State reconstruction from memory dumps
6. **Static Analyzer** - Comprehensive static analysis

## 🎯 What's Included

- ✅ FastAPI backend with Celery workers
- ✅ React frontend with analytics dashboard
- ✅ ReverisNoctis desktop application (Tauri)
- ✅ PostgreSQL, Redis, MinIO stack
- ✅ 6 analysis plugins
- ✅ Docker Compose setup
- ✅ CLI tools
- ✅ Cross-platform builds

## ⚡ Quick Start

**Desktop App**: Download and run the installer for your platform above.

**Web Stack**:

```bash
git clone https://github.com/ind4skylivey/aetherframe.git
cd aetherframe
./start.sh
```

## 🙏 Acknowledgments

Special thanks to the FastAPI, Tauri, Frida, and PostgreSQL communities.

## 📄 License

MIT License - See [LICENSE.txt](https://github.com/ind4skylivey/aetherframe/blob/main/LICENSE.txt)

---

**Full Changelog**: https://github.com/ind4skylivey/aetherframe/commits/v1.0.0
