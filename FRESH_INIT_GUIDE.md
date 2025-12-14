# 🔄 Fresh Repository Initialization Guide

## Overview

This guide helps you recreate the AetherFrame repository with a **clean monorepo structure** from the beginning, removing all the messy migration history.

---

## ⚡ Quick Start (Recommended)

### Step 1: Run the Fresh Init Script

```bash
./scripts/fresh-init.sh
```

This script will:

1. ✅ Create a backup of your current repository
2. ✅ Remove old git history
3. ✅ Organize code into proper monorepo structure
4. ✅ Create new git repository with clean initial commit
5. ✅ Set up all configuration files

### Step 2: Push to GitHub

```bash
# First, make sure the script completed successfully
git log  # Should show 1 clean initial commit

# Add your GitHub remote
git remote add origin https://github.com/ind4skylivey/aetherframe-ecosystem.git

# Push (this will REPLACE your GitHub repo)
git push -u origin main --force
```

**⚠️ WARNING**: `--force` will destroy your GitHub history. Make sure you have a backup!

---

## 📋 Manual Approach (Alternative)

If you prefer to do it manually:

### 1. Backup Current Repo

```bash
cd ..
cp -r aetherframe-ecosystem aetherframe-ecosystem_backup
cd aetherframe-ecosystem
```

### 2. Remove Git History

```bash
rm -rf .git
git init
```

### 3. Organize Structure

```bash
# Create directories
mkdir -p packages/{core,frontend,cli}
mkdir -p plugins/{umbriel,noema,valkyrie}
mkdir -p shared/{schemas,types,configs}
mkdir -p tools/{plugin-sdk,testing}
mkdir -p docs/{architecture,api,plugins}

# Move existing code
mv AetherFrame/aetherframe packages/core/
mv ReverisNoctis/src packages/frontend/
mv ReverisNoctis/cli packages/cli/reveris

# Move plugins
mv AetherFrame/aetherframe/plugins/umbriel plugins/
```

### 4. Create Root Configuration

```bash
# Create package.json (workspace)
cat > package.json << 'EOF'
{
  "name": "aetherframe-ecosystem",
  "version": "0.1.0",
  "private": true,
  "workspaces": ["packages/*"]
}
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
node_modules/
.env
*.log
dist/
build/
EOF
```

### 5. Initial Commit

```bash
git add .
git commit -m "feat: initialize AetherFrame monorepo

- Set up hybrid monorepo architecture
- Organize into packages/, plugins/, shared/
- Add complete documentation
- Include Docker all-in-one setup"
```

### 6. Push to GitHub

```bash
git remote add origin https://github.com/ind4skylivey/aetherframe-ecosystem.git
git push -u origin main --force
```

---

## 🎯 Resulting Structure

After initialization, your repository will look like:

```
aetherframe-ecosystem/
├── .github/
│   └── workflows/              # CI/CD workflows
├── packages/
│   ├── core/                   # Backend (Python/FastAPI)
│   │   ├── setup.py
│   │   ├── aetherframe/
│   │   └── tests/
│   ├── frontend/               # Web UI (React/Vite)
│   │   ├── package.json
│   │   ├── src/
│   │   └── public/
│   └── cli/                    # CLI Tool (Python)
│       ├── setup.py
│       └── reveris/
├── plugins/
│   ├── umbriel/               # Anti-analysis plugin
│   ├── noema/                 # Intent classification
│   └── .../
├── shared/
│   ├── schemas/               # Common Pydantic schemas
│   ├── types/                 # TypeScript types
│   └── configs/               # Shared configs
├── tools/
│   ├── plugin-sdk/            # Plugin dev kit
│   └── testing/               # Testing utilities
├── docs/
│   ├── architecture/
│   ├── api/
│   └── guides/
├── scripts/
│   ├── fresh-init.sh         # This initialization script
│   └── install-all.py        # Install all packages
├── docker/
│   ├── nginx.conf
│   └── supervisord.conf
├── package.json               # Workspace root
├── .gitignore
├── README.md
├── MONOREPO_STRUCTURE.md
└── start.sh                   # Easy start script
```

---

## ✅ Verification

After running the script, verify everything worked:

### 1. Check Git History

```bash
git log
# Should show only 1 commit: "feat: initialize AetherFrame monorepo..."
```

### 2. Check Structure

```bash
tree -L 2 -I 'node_modules|__pycache__'
# Should show clean monorepo structure
```

### 3. Check Backup

```bash
ls ../aetherframe-ecosystem_backup*
# Should show backup directory with timestamp
```

### 4. Test Functionality

```bash
# Install dependencies
npm install
python scripts/install-all.py

# Test start
./start.sh
```

---

## 🔄 What Gets Preserved

✅ **All your code**
✅ **All configurations**
✅ **All documentation**
✅ **All Docker setups**
✅ **All dependencies**

## ❌ What Gets Removed

❌ **Old git history** (messy commits, experiments)
❌ **Old directory structure** (flat layout)
❌ **Redundant files**

---

## 🎓 Benefits

### Clean History

- 1 professional initial commit
- No "fix typo" or "oops" commits
- Clean for portfolio/showcase

### Proper Structure

- Industry-standard monorepo
- Clear module boundaries
- Easy to understand

### Future-Proof

- Easy to add new packages
- Easy to split modules
- Easy to publish packages

---

## ⚠️ Important Notes

1. **Backup First**: The script creates a backup, but double-check!

2. **GitHub Force Push**: Using `--force` will replace your GitHub repo completely

3. **Collaborators**: Warn any collaborators before force-pushing

4. **Branches**: This creates a new `main` branch from scratch

5. **Issues/PRs**: GitHub issues and PRs will remain (they're separate from git history)

---

## 🆘 Rollback

If something goes wrong:

```bash
# Delete current repo
cd ..
rm -rf aetherframe-ecosystem

# Restore backup
mv aetherframe-ecosystem_backup_TIMESTAMP aetherframe-ecosystem
cd aetherframe-ecosystem

# You're back to where you started
```

---

## 📞 Support

If you encounter issues:

1. Check the backup was created
2. Review the script output for errors
3. Verify file permissions (`chmod +x scripts/fresh-init.sh`)
4. Try the manual approach instead

---

## 🚀 After Initialization

Once your repo is clean:

1. **Update GitHub description**: "Advanced malware analysis platform with hybrid monorepo architecture"

2. **Add topics**: `malware-analysis`, `reverse-engineering`, `monorepo`, `fastapi`, `react`

3. **Proceed to Phase 4**: Desktop packaging with Tauri

---

**Ready to start fresh?**
Run: `./scripts/fresh-init.sh`
