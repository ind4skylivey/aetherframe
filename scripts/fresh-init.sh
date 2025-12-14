#!/bin/bash

# AetherFrame Ecosystem - Fresh Repository Initialization
# This script creates a clean monorepo structure from scratch

set -e

REPO_NAME="aetherframe-ecosystem"
BACKUP_DIR="${REPO_NAME}_backup_$(date +%Y%m%d_%H%M%S)"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  AetherFrame Ecosystem - Fresh Monorepo Initialization     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Backup current repository
echo "📦 Step 1: Creating backup..."
if [ -d "../${BACKUP_DIR}" ]; then
    echo "⚠️  Backup already exists, skipping..."
else
    cd ..
    cp -r "$REPO_NAME" "$BACKUP_DIR"
    echo "✅ Backup created: ../${BACKUP_DIR}"
    cd "$REPO_NAME"
fi

echo ""
echo "🗑️  Step 2: Cleaning current git history..."
read -p "⚠️  This will DESTROY all git history. Continue? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Cancelled. Your repository is unchanged."
    exit 0
fi

# Remove .git directory
rm -rf .git
echo "✅ Git history removed"

echo ""
echo "📁 Step 3: Creating clean monorepo structure..."

# Create new structure
mkdir -p packages/{core,frontend,cli}
mkdir -p plugins/{umbriel,noema,valkyrie,static-analyzer,lain-trace,mnemosyne}
mkdir -p shared/{schemas,types,configs}
mkdir -p tools/{plugin-sdk,testing}
mkdir -p docs/{architecture,api,plugins,guides}
mkdir -p scripts
mkdir -p .github/workflows

echo "✅ Directory structure created"

echo ""
echo "📝 Step 4: Organizing existing code..."

# Move existing code to proper locations
if [ -d "AetherFrame/aetherframe" ]; then
    cp -r AetherFrame/aetherframe packages/core/
    cp AetherFrame/requirements.txt packages/core/ 2>/dev/null || true
    cp AetherFrame/docker-compose.yml packages/core/ 2>/dev/null || true
    echo "  ✓ Core backend moved to packages/core/"
fi

if [ -d "ReverisNoctis/src" ]; then
    cp -r ReverisNoctis/src packages/frontend/
    cp ReverisNoctis/package.json packages/frontend/ 2>/dev/null || true
    cp ReverisNoctis/vite.config.js packages/frontend/ 2>/dev/null || true
    cp ReverisNoctis/index.html packages/frontend/ 2>/dev/null || true
    echo "  ✓ Frontend moved to packages/frontend/"
fi

if [ -d "ReverisNoctis/cli" ]; then
    cp -r ReverisNoctis/cli packages/cli/reveris
    echo "  ✓ CLI moved to packages/cli/"
fi

# Extract plugins
if [ -d "AetherFrame/aetherframe/plugins/umbriel" ]; then
    cp -r AetherFrame/aetherframe/plugins/umbriel plugins/
    echo "  ✓ Umbriel plugin extracted"
fi

# Copy docker configs
cp Dockerfile.allinone . 2>/dev/null || true
cp docker-compose.allinone.yml . 2>/dev/null || true
cp -r docker . 2>/dev/null || true
cp start.sh . 2>/dev/null || true

echo ""
echo "🔧 Step 5: Creating package configurations..."

# Root package.json for workspace
cat > package.json << 'EOF'
{
  "name": "aetherframe-ecosystem",
  "version": "0.1.0",
  "private": true,
  "description": "AetherFrame - Advanced Malware Analysis Platform",
  "workspaces": [
    "packages/*"
  ],
  "scripts": {
    "install:all": "python scripts/install-all.py",
    "dev:frontend": "npm run dev --workspace=@aetherframe/frontend",
    "build:frontend": "npm run build --workspace=@aetherframe/frontend",
    "dev:backend": "cd packages/core && docker compose up",
    "start": "./start.sh"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/ind4skylivey/aetherframe-ecosystem.git"
  },
  "author": "ind4skylivey",
  "license": "MIT"
}
EOF

# .gitignore
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

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
dist/
.cache/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Docker
.env
*.log

# Project specific
samples/
*.exe
*.dll
*.dylib
*.so

# Keep structure
!.gitkeep
EOF

# Add .gitkeep to empty directories
find packages plugins shared tools docs -type d -empty -exec touch {}/.gitkeep \;

echo "✅ Package configurations created"

echo ""
echo "📚 Step 6: Creating documentation..."

# Copy documentation files
cp README.md . 2>/dev/null || echo "# AetherFrame Ecosystem" > README.md
cp MONOREPO_STRUCTURE.md . 2>/dev/null || true
cp MIGRATION_GUIDE.md . 2>/dev/null || true
cp PROJECT_SUMMARY.md docs/ 2>/dev/null || true

echo "✅ Documentation organized"

echo ""
echo "🔄 Step 7: Initializing new Git repository..."

git init
git add .
git commit -m "feat: initialize AetherFrame monorepo structure

- Set up hybrid monorepo architecture
- Organize code into packages/, plugins/, shared/
- Add workspace configuration
- Include Docker all-in-one setup
- Add comprehensive documentation

This is the initial commit with clean monorepo structure."

echo "✅ Git repository initialized"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    ✅ SUCCESS!                              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Your repository has been recreated with clean structure!"
echo ""
echo "📁 Backup location: ../${BACKUP_DIR}"
echo ""
echo "🚀 Next steps:"
echo ""
echo "1. Review the new structure:"
echo "   tree -L 2 -I 'node_modules|__pycache__|.git'"
echo ""
echo "2. Set up remote and push:"
echo "   git remote add origin https://github.com/ind4skylivey/aetherframe-ecosystem.git"
echo "   git branch -M main"
echo "   git push -u origin main --force"
echo ""
echo "3. Install dependencies:"
echo "   npm install          # Install workspace"
echo "   npm run install:all  # Install all packages"
echo ""
echo "4. Start development:"
echo "   ./start.sh           # All-in-one mode"
echo "   npm run dev:frontend # Frontend only"
echo "   npm run dev:backend  # Backend only"
echo ""
echo "⚠️  WARNING: The force push will replace your GitHub repository!"
echo "    Make sure you have a backup before pushing."
echo ""
