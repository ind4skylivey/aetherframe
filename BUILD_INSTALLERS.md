# 🏭 Building Desktop Installers for All Platforms

## Overview

AetherFrame uses **GitHub Actions** to automatically build desktop installers for Linux, macOS, and Windows.

---

## 🎯 What Gets Built

### **Linux**

- `aetherframe_0.1.0_amd64.AppImage` - Portable, no installation needed
- `aetherframe_0.1.0_amd64.deb` - For Debian/Ubuntu

### **macOS**

- `AetherFrame_0.1.0_x64.dmg` - Installer disk image
- `AetherFrame.app` - Application bundle

### **Windows**

- `AetherFrame_0.1.0_x64.msi` - Traditional Windows installer
- `AetherFrame_0.1.0_x64-setup.exe` - Modern NSIS installer

---

## 🚀 How to Build

### **Option 1: Create a Release Tag** (Automatic)

```bash
# Tag a release
git tag v0.1.0
git push origin v0.1.0
```

**What happens:**

1. GitHub Actions triggers automatically
2. Builds on all 3 platforms (15-20 min total)
3. Creates GitHub Release with all installers attached

### **Option 2: Manual Trigger**

1. Go to: https://github.com/ind4skylivey/aetherframe/actions
2. Click "Build Desktop Apps" workflow
3. Click "Run workflow"
4. Enter version (e.g., `v0.1.0`)
5. Click "Run workflow"

**What happens:**

1. Builds on all 3 platforms
2. Uploads artifacts (no release created)
3. Download from Actions tab

---

## 📦 Download Built Installers

### **From GitHub Releases** (after tagging)

1. Go to: https://github.com/ind4skylivey/aetherframe/releases
2. Find your version (e.g., v0.1.0)
3. Download for your platform:
   - **Linux**: Download `.AppImage` or `.deb`
   - **macOS**: Download `.dmg`
   - **Windows**: Download `.exe` or `.msi`

### **From GitHub Actions** (manual build)

1. Go to: https://github.com/ind4skylivey/aetherframe/actions
2. Click on the workflow run
3. Scroll to "Artifacts"
4. Download:
   - `aetherframe-linux`
   - `aetherframe-macos`
   - `aetherframe-windows`

---

## 🔧 Prerequisites (First Time Only)

### **1. Enable GitHub Actions**

Already enabled! ✅

### **2. Add App Icons** (Before first build)

You need to create icons in `packages/frontend/src-tauri/icons/`:

**Required files:**

- `icon.png` (1024x1024) - Base icon
- `32x32.png`
- `128x128.png`
- `128x128@2x.png`
- `icon.icns` (macOS)
- `icon.ico` (Windows)

**Quick way:**

```bash
# Install icon generator
npm install -g @tauri-apps/tauricon

# Generate all sizes from one image
cd packages/frontend/src-tauri
tauricon path/to/your-icon-1024x1024.png
```

### **3. Optional: Code Signing** (For trusted installers)

**Windows:**

```bash
# Get a code signing certificate
# Add to GitHub Secrets:
# - WINDOWS_CERTIFICATE
# - WINDOWS_CERTIFICATE_PASSWORD
```

**macOS:**

```bash
# Get Apple Developer certificate
# Add to GitHub Secrets:
# - APPLE_CERTIFICATE
# - APPLE_CERTIFICATE_PASSWORD
# - APPLE_ID
# - APPLE_TEAM_ID
```

---

## 🎬 Build Process Details

### **Time Estimates**

| Platform  | Build Time     |
| --------- | -------------- |
| Linux     | ~5-8 minutes   |
| macOS     | ~8-12 minutes  |
| Windows   | ~6-10 minutes  |
| **Total** | ~15-25 minutes |

### **Build Matrix**

The workflow runs **3 parallel jobs**:

```yaml
matrix:
  platform:
    - ubuntu-22.04 # → Linux builds
    - macos-latest # → macOS builds
    - windows-latest # → Windows builds
```

### **What Each Job Does**

1. **Checkout code**
2. **Install Node.js 18**
3. **Install Rust**
4. **Install platform dependencies** (Linux only)
5. **Install npm packages**
6. **Build Tauri app** (`npm run tauri:build`)
7. **Upload artifacts**

---

## 📊 Monitoring Builds

### **Watch Build Progress**

1. Go to: https://github.com/ind4skylivey/aetherframe/actions
2. Click on latest workflow run
3. Click on any platform job to see logs

### **Build Status Badge**

Add to README:

```markdown
[![Build Desktop Apps](https://github.com/ind4skylivey/aetherframe/actions/workflows/build-desktop.yml/badge.svg)](https://github.com/ind4skylivey/aetherframe/actions/workflows/build-desktop.yml)
```

---

## 🐛 Troubleshooting

### **Build Fails on Linux**

Usually missing dependencies. Check the workflow includes:

```yaml
libwebkit2gtk-4.0-dev
build-essential
libssl-dev
libgtk-3-dev
libayatana-appindicator3-dev
librsvg2-dev
```

### **Build Fails on macOS**

Usually Xcode tools. The workflow uses:

```yaml
- uses: dtolnay/rust-toolchain@stable
```

This should auto-install needed tools.

### **Build Fails on Windows**

Usually Visual Studio tools. GitHub's Windows runners include them, so shouldn't fail.

### **Icons Missing**

```
Error: Failed to bundle project: icons not found
```

**Fix:**

1. Create icons in `packages/frontend/src-tauri/icons/`
2. Or use default Tauri icons temporarily
3. Push and retry

---

## 📝 Creating Your First Release

### **Step by Step:**

1. **Prepare icons** (if haven't already):

```bash
cd packages/frontend/src-tauri/icons
# Place your icon files here
```

2. **Update version** in `packages/frontend/src-tauri/Cargo.toml`:

```toml
[package]
version = "0.1.0"
```

3. **Update version** in `packages/frontend/src-tauri/tauri.conf.json`:

```json
{
  "package": {
    "version": "0.1.0"
  }
}
```

4. **Commit changes**:

```bash
git add .
git commit -m "chore: bump version to 0.1.0"
git push
```

5. **Create and push tag**:

```bash
git tag v0.1.0
git push origin v0.1.0
```

6. **Wait for build** (~20 minutes)

7. **Check release**:
   - Go to https://github.com/ind4skylivey/aetherframe/releases
   - You should see v0.1.0 with all installers!

---

## 🎨 Icon Guidelines

### **Design Recommendations**

- **Simple**: Should be recognizable at 16x16
- **Contrast**: Dark theme? Use light icon and vice versa
- **No text**: Icons with text don't scale well
- **Square**: 1:1 aspect ratio

### **Example Tools**

- **Figma** - Design icon
- **GIMP** - Edit PNG
- **Inkscape** - Vector graphics
- **Icon Kitchen** - Online generator

### **AetherFrame Icon Ideas**

Since it's a malware analysis tool:

- 🔍 Magnifying glass over binary code
- 🛡️ Shield with circuit patterns
- ⚡ Lightning bolt (matches name!)
- 🌌 Aether symbol with tech elements

---

## 📢 Distributing to Users

### **Add Download Section to README**

```markdown
## 📥 Download

### Desktop Apps

[![Linux](https://img.shields.io/badge/Linux-AppImage%20%7C%20.deb-blue?logo=linux)](https://github.com/ind4skylivey/aetherframe/releases/latest)
[![macOS](https://img.shields.io/badge/macOS-.dmg-black?logo=apple)](https://github.com/ind4skylivey/aetherframe/releases/latest)
[![Windows](https://img.shields.io/badge/Windows-.exe%20%7C%20.msi-blue?logo=windows)](https://github.com/ind4skylivey/aetherframe/releases/latest)

Download the latest release for your platform from [Releases](https://github.com/ind4skylivey/aetherframe/releases/latest).
```

### **Installation Instructions**

**Linux:**

```bash
# AppImage
chmod +x aetherframe_*.AppImage
./aetherframe_*.AppImage

# Debian/Ubuntu
sudo dpkg -i aetherframe_*.deb
```

**macOS:**

```bash
# Open .dmg
# Drag AetherFrame.app to Applications
# Launch from Applications folder
```

**Windows:**

```
# Run installer
# Follow wizard
# Launch from Start Menu
```

---

## ✅ Checklist for First Build

- [ ] Icons created in `src-tauri/icons/`
- [ ] Version updated in `Cargo.toml`
- [ ] Version updated in `tauri.conf.json`
- [ ] Changes committed to git
- [ ] Tag created: `git tag v0.1.0`
- [ ] Tag pushed: `git push origin v0.1.0`
- [ ] GitHub Actions workflow triggered
- [ ] Build completed successfully
- [ ] Release created with all installers
- [ ] Downloaded and tested on each platform

---

## 🚀 Next Steps

After successful build:

1. **Test installers** on real machines
2. **Get code signing certificates** (for trusted installs)
3. **Set up auto-updates** (Tauri updater feature)
4. **Create landing page** for downloads
5. **Announce release** on GitHub, social media

---

**Status**: ✅ GitHub Actions Configured
**Next**: Create app icons and trigger first build!
**Files**: `.github/workflows/build-desktop.yml`

## 🔧 Troubleshooting

### Linux: Black/Blank Screen (EGL Error)

If the AppImage shows a black screen with EGL errors in the console:

```bash
Could not create default EGL display: EGL_BAD_PARAMETER
```

**Solution**: Run with software rendering:

```bash
WEBKIT_DISABLE_COMPOSITING_MODE=1 LIBGL_ALWAYS_SOFTWARE=1 ./aether-frame_*.AppImage
```

Or create a launcher script:

```bash
#!/bin/bash
export WEBKIT_DISABLE_COMPOSITING_MODE=1
export LIBGL_ALWAYS_SOFTWARE=1
./aether-frame_*.AppImage
```

This disables hardware acceleration and uses software rendering, which is more compatible across different Linux systems.

