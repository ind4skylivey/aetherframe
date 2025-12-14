# AetherFrame Ecosystem - Monorepo Structure

This repository uses a hybrid monorepo approach, allowing independent module development while maintaining a cohesive project structure.

## 📦 Packages

### Core Packages

Located in `packages/`:

- **`core`** - AetherFrame backend (FastAPI, Celery, database)
- **`frontend`** - Web UI (React + Vite)
- **`cli`** - Command-line interface tool

### Plugins

Located in `plugins/`:

- **`umbriel`** - Anti-analysis detection
- **`noema`** - Intent classification
- **`valkyrie`** - Binary validation
- **`static-analyzer`** - Static analysis
- **`lain-trace`** - Dynamic tracing
- **`mnemosyne`** - State reconstruction

### Shared Resources

Located in `shared/`:

- **`schemas`** - Common Pydantic schemas
- **`types`** - TypeScript types
- **`configs`** - Shared configurations

### Tools

Located in `tools/`:

- **`plugin-sdk`** - Plugin development kit
- **`testing`** - Shared testing utilities

## 🔧 Working with Modules

### Install Dependencies

All packages at once:

```bash
python scripts/install-all.py
```

Individual package:

```bash
# Backend core
cd packages/core && pip install -e .

# Frontend
cd packages/frontend && npm install

# CLI
cd packages/cli && pip install -e .

# Specific plugin
cd plugins/umbriel && pip install -e .
```

### Development

Each package is independently developable:

```bash
# Work on core
cd packages/core
pytest

# Work on frontend
cd packages/frontend
npm run dev

# Work on plugin
cd plugins/umbriel
pytest tests/
```

### Building

Build individual packages:

```bash
# Core
cd packages/core && python -m build

# Frontend
cd packages/frontend && npm run build

# Plugin
cd plugins/umbriel && python -m build
```

## 📋 Module Independence

Each module can be:

- ✅ Developed independently
- ✅ Tested independently
- ✅ Versioned independently
- ✅ Published to PyPI/npm independently
- ✅ Extracted to separate repo later (if needed)

## 🔗 Module Dependencies

```
frontend → core (API client)
cli → core (API client)
plugins → core (Plugin base classes)
```

## 🚀 Quick Start

See main [README.md](./README.md) for full setup instructions.

### Option 1: Full Ecosystem

```bash
./start.sh
```

### Option 2: Development Mode

```bash
# Terminal 1: Backend
cd packages/core
docker compose up -d

# Terminal 2: Frontend
cd packages/frontend
npm run dev
```

## 📖 Documentation

- [Core Package](./packages/core/README.md)
- [Frontend Package](./packages/frontend/README.md)
- [CLI Package](./packages/cli/README.md)
- [Plugin Development Guide](./tools/plugin-sdk/README.md)

## 🏛️ Project Structure

```
aetherframe-ecosystem/
├── packages/
│   ├── core/              # Backend & API
│   │   ├── setup.py
│   │   ├── pyproject.toml
│   │   └── aetherframe/
│   ├── frontend/          # React UI
│   │   ├── package.json
│   │   └── src/
│   └── cli/               # CLI Tool
│       ├── setup.py
│       └── reveris/
├── plugins/
│   ├── umbriel/
│   │   ├── setup.py
│   │   └── umbriel_plugin/
│   └── noema/
│       ├── setup.py
│       └── noema_plugin/
├── shared/
│   ├── schemas/           # Common schemas
│   └── configs/           # Shared configs
├── tools/
│   └── plugin-sdk/        # Plugin dev kit
├── scripts/
│   └── install-all.py     # Install all packages
└── docs/
    └── architecture/      # Architecture docs
```

## 🔄 Migration Path

If a module needs to become a separate repository:

1. The module is already self-contained
2. Has its own setup.py/package.json
3. Has its own tests
4. Can be git-filtered and moved to new repo
5. Replace with git submodule in main repo

## 📝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development workflow.
