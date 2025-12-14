#!/bin/bash

# AetherFrame - New Repository Setup
# Creates a fresh repository while preserving the old one

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       AetherFrame - New Repository Creation                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
OLD_REPO="aetherframe-ecosystem"
NEW_REPO_NAME="${1:-aetherframe}"  # Default to 'aetherframe', can override with argument

echo "📋 Configuration:"
echo "  Old repo (will stay): ${OLD_REPO}"
echo "  New repo name: ${NEW_REPO_NAME}"
echo ""

read -p "Continue with this setup? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🔧 Step 1: Creating clean git repository locally..."

# Remove old .git
if [ -d ".git" ]; then
    rm -rf .git
    echo "  ✓ Removed old .git directory"
fi

# Initialize new repo
git init
echo "  ✓ Initialized new git repository"

# Create comprehensive .gitignore if not exists
if [ ! -f ".gitignore" ]; then
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
*.egg

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
dist/
.cache/
.vite/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Environment
.env
.env.local
.env.*.local

# Logs
*.log
logs/

# Docker
docker-compose.override.yml

# OS
.DS_Store
Thumbs.db

# Project specific
samples/*.exe
samples/*.dll
*.exe
*.dll
*.dylib
*.so

# Keep structure
!.gitkeep
EOF
    echo "  ✓ Created comprehensive .gitignore"
fi

echo ""
echo "📝 Step 2: Creating initial commit..."

git add .
git commit -m "feat: initialize AetherFrame monorepo

## Architecture

Hybrid monorepo structure with clear module boundaries:

- **packages/**: Core packages (core, frontend, cli)
- **plugins/**: Analysis plugins (umbriel, noema, valkyrie, etc.)
- **shared/**: Common resources (schemas, types, configs)
- **tools/**: Development tools (plugin-sdk, testing)
- **docs/**: Comprehensive documentation

## Features

- ✅ Advanced malware analysis backend (FastAPI + Celery)
- ✅ Modern web UI with analytics (React + Vite + Recharts)
- ✅ CLI tool for automation
- ✅ Plugin-based architecture
- ✅ Docker all-in-one deployment
- ✅ Real-time monitoring
- ✅ Hybrid monorepo for easy module extraction

## Quick Start

\`\`\`bash
./start.sh
\`\`\`

See README.md for full documentation.

---

This is the initial commit with production-ready monorepo structure."

echo "  ✓ Created initial commit"

echo ""
echo "🌐 Step 3: Setting up GitHub remote..."

git branch -M main
git remote add origin "https://github.com/ind4skylivey/${NEW_REPO_NAME}.git"

echo "  ✓ Remote configured: https://github.com/ind4skylivey/${NEW_REPO_NAME}.git"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                 ✅ LOCAL SETUP COMPLETE!                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣  On GitHub (https://github.com/ind4skylivey):"
echo ""
echo "   A) Archive old repository:"
echo "      • Go to: https://github.com/ind4skylivey/${OLD_REPO}"
echo "      • Settings → General → Danger Zone"
echo "      • Click 'Archive this repository'"
echo "      • (Optional) Change to Private"
echo ""
echo "   B) Create new repository:"
echo "      • Click 'New repository'"
echo "      • Name: ${NEW_REPO_NAME}"
echo "      • Description: 'Advanced malware analysis platform with hybrid monorepo architecture'"
echo "      • Public ✅"
echo "      • DON'T initialize (no README, .gitignore, license)"
echo "      • Click 'Create repository'"
echo ""
echo "2️⃣  Push to new repository:"
echo ""
echo "   git push -u origin main"
echo ""
echo "3️⃣  Set up repository on GitHub:"
echo ""
echo "   • Add topics: malware-analysis, reverse-engineering, monorepo, fastapi, react"
echo "   • Add description"
echo "   • Enable Issues, Discussions"
echo "   • Configure GitHub Pages (if desired)"
echo ""
echo "4️⃣  Update any documentation links:"
echo ""
echo "   • README badges"
echo "   • Documentation references"
echo "   • External links"
echo ""
echo "💡 TIP: The old repository (${OLD_REPO}) will remain as:"
echo "   • Archived (read-only)"
echo "   • Full history preserved"
echo "   • Available for reference"
echo ""
echo "🎉 Ready to push when GitHub repo is created!"
echo ""
