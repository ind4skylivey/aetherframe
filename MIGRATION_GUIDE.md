# Migration Guide: Hybrid Monorepo Structure

## What Changed?

The AetherFrame ecosystem has been restructured from a simple project layout to a hybrid monorepo with clear module boundaries.

### Before

```
aetherframe-ecosystem/
├── AetherFrame/        # Backend
├── ReverisNoctis/      # Frontend + CLI
└── tests/
```

### After

```
aetherframe-ecosystem/
├── packages/
│   ├── core/           # Backend (was AetherFrame/)
│   ├── frontend/       # UI (was ReverisNoctis/src/)
│   └── cli/            # CLI (was ReverisNoctis/cli/)
├── plugins/
│   └── umbriel/        # Plugins extracted
└── shared/             # Shared resources
```

## For Developers

### Update Your Workflow

**Old way:**
```bash
cd AetherFrame
docker-compose up
```

**New way:**
```bash
cd packages/core
docker compose up
```

### Import Changes

**Old:**
```python
from aetherframe.core import pipeline
```

**New:**
```python
# Same imports work! Module namespaces preserved
from aetherframe.core import pipeline
```

### Installing Packages

**Development install (recommended):**
```bash
# From repo root
python scripts/install-all.py

# Or individual packages
cd packages/core && pip install -e .
cd packages/cli && pip install -e .
```

## Benefits

✅ **Clear module boundaries** - Each package is self-contained
✅ **Independent versioning** - Packages can have different versions
✅ **Better testing** - Test modules in isolation
✅ **Future-proof** - Easy to extract modules to separate repos
✅ **Professional structure** - Industry-standard monorepo layout

## Backwards Compatibility

- ✅ All existing imports work
- ✅ Docker Compose configs compatible
- ✅ CLI commands unchanged
- ✅ API endpoints same
- ✅ Plugin interfaces preserved

## Questions?

See [MONOREPO_STRUCTURE.md](./MONOREPO_STRUCTURE.md) for full documentation.
