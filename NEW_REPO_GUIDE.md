# 🆕 New Repository Setup - Quick Guide

## ✅ Recommended Approach

**Create a brand new repository** while keeping the old one archived.

---

## 🎯 Quick Start

### Run This:

```bash
./scripts/new-repo-setup.sh
```

**Optional**: Specify custom name

```bash
./scripts/new-repo-setup.sh aetherframe
```

---

## 📋 Manual Steps

### 1. Local Setup (Automated by script)

```bash
# Clean git history
rm -rf .git
git init

# Create commit
git add .
git commit -m "feat: initialize AetherFrame monorepo"

# Configure remote
git branch -M main
git remote add origin https://github.com/ind4skylivey/aetherframe.git
```

### 2. On GitHub

**A) Archive old repo:**

1. Go to https://github.com/ind4skylivey/aetherframe-ecosystem
2. Settings → Danger Zone → **Archive**
3. (Optional) Make **Private**

**B) Create new repo:**

1. New Repository
2. Name: **`aetherframe`**
3. Description: "Advanced malware analysis platform with hybrid monorepo architecture"
4. **Public**
5. **Don't initialize**
6. Create

### 3. Push

```bash
git push -u origin main
```

---

## 🎨 Repository Names

### Recommended: `aetherframe`

- ✅ Short and clean
- ✅ Professional
- ✅ Easy to type/remember
- Example: https://github.com/ind4skylivey/aetherframe

### Alternative: `aetherframe-platform`

- More descriptive
- Shows scope
- Example: https://github.com/ind4skylivey/aetherframe-platform

### Keep: `aetherframe-ecosystem`

- Maintains consistency
- If you prefer longer name
- Example: https://github.com/ind4skylivey/aetherframe-ecosystem

---

## ✨ Why This Approach?

| Aspect           | New Repo     | Force Push |
| ---------------- | ------------ | ---------- |
| **Safety**       | ✅ Zero risk | ⚠️ Risky   |
| **Old history**  | ✅ Archived  | ❌ Lost    |
| **Clean start**  | ✅ Perfect   | ✅ Yes     |
| **Rollback**     | ✅ Easy      | ⚠️ Hard    |
| **Professional** | ✅ Very      | ✅ Yes     |

### Advantages:

- ✅ Old repo preserved (can reference anytime)
- ✅ Zero risk of data loss
- ✅ Perfect history from day 1
- ✅ Can use shorter name
- ✅ No force push complications

---

## 📊 Result

### Old Repo (Archived + Private)

```
https://github.com/ind4skylivey/aetherframe-ecosystem
✅ Archived (read-only)
✅ Private (optional)
✅ Full history preserved
✅ Available as backup
```

### New Repo (Active + Public)

```
https://github.com/ind4skylivey/aetherframe
✅ Clean monorepo structure
✅ 1 perfect initial commit
✅ Professional presentation
✅ Ready for Phase 4
```

---

## 🎯 After Setup

Once new repo is created and pushed:

### 1. Configure Repository

- Add topics: `malware-analysis`, `reverse-engineering`, `monorepo`, `fastapi`, `react`, `tauri`
- Add description
- Enable Issues
- Enable Discussions
- Set up GitHub Pages (optional)

### 2. Update Documentation

- Update README badges (if any)
- Update any hardcoded URLs
- Add social preview image

### 3. Proceed to Phase 4

- Desktop packaging with Tauri
- Create installers
- System tray integration

---

## 🔄 What About Links?

**Old links** (`aetherframe-ecosystem`) will:

- Still work (GitHub redirect)
- Show archived status
- Redirect to new repo (if you set it up)

**New links** (`aetherframe`) will:

- Be the canonical URL
- Show active development
- Have clean history

---

## 💡 Pro Tips

### Update Old Repo README

Add to old repo before archiving:

```markdown
# ⚠️ ARCHIVED

This repository has been archived and replaced by:

👉 **https://github.com/ind4skylivey/aetherframe**

The new repository features:

- Clean monorepo structure
- Updated documentation
- Active development

Please use the new repository going forward.
```

### Pin New Repo

On your GitHub profile, **pin** the new `aetherframe` repo to showcase it.

---

## ✅ Checklist

- [ ] Run `./scripts/new-repo-setup.sh`
- [ ] Archive old repo on GitHub
- [ ] Create new repo on GitHub
- [ ] Push: `git push -u origin main`
- [ ] Add topics and description
- [ ] Update old repo README
- [ ] Pin new repo on profile
- [ ] Proceed to Phase 4

---

## 🆘 Need Help?

The script (`new-repo-setup.sh`) will guide you through each step with clear instructions.

---

**Ready?** Run: `./scripts/new-repo-setup.sh`
