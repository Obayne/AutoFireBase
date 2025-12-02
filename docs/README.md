# AutoFireBase Documentation

Welcome to the AutoFireBase documentation! This directory contains all project documentation organized by audience and purpose.

## Documentation Structure

### For New Users

- **[Remote Access Setup](REMOTE_ACCESS_SETUP.md)** - Connect from mobile devices (Android, iOS)
- **[Quick Start Guide](REMOTE_TUNNEL_QUICKSTART.md)** - 2-minute setup for remote tunnels
- **[Architecture Overview](ARCHITECTURE.md)** - System design and component overview

### For Developers

- **[Contributing Guidelines](../CONTRIBUTING.md)** - How to contribute to the project
- **[Agent Guide (HAL)](../AGENTS.md)** - Rules for AI agents working on the codebase
- **[Team Structure](TEAM.md)** - Team roles and responsibilities
- **[Documentation Guide](DOCUMENTATION_GUIDE.md)** - How to write and build documentation

### DevOps & Operations

- **[Benchmarking Guide](BENCHMARKING.md)** - Performance testing with pytest-benchmark
- **[Build Caching](BUILD_CACHING.md)** - PyInstaller build optimization
- **[Sentry Integration](SENTRY_INTEGRATION.md)** - Error tracking setup and usage
- **[CI/CD Pipeline](CI_README.md)** - Continuous integration workflow

### Sprint Documentation

- **[Sprint 01](SPRINT_01.md)** - Coverage service and database refactoring
- **[Sprint 01 (alt)](SPRINT-01.md)** - Alternative sprint documentation

### API Reference

Auto-generated API documentation is available in the `api/` directory:

- **[Backend API](api/backend.rst)** - Business logic and services
- **[CAD Core API](api/cad_core.rst)** - Geometry algorithms
- **[Frontend API](api/frontend.rst)** - UI components
- **[App API](api/app.rst)** - Application layer

### Operational Guides

Located in `ops/` directory:

- **[CI/CD](ops/ci_cd.rst)** - GitHub Actions workflows
- **[Benchmarking](ops/benchmarking.rst)** - Performance testing
- **[Build Caching](ops/build_caching.rst)** - Build optimization
- **[Monitoring](ops/monitoring.rst)** - Error tracking and metrics

### Archive

Historical documentation is preserved in `archive/`:

- Deprecated guides
- Legacy architecture docs
- Migration guides

## Building Documentation

### Prerequisites

```powershell
pip install -r requirements-dev.txt
```

### Build HTML Docs (Windows)

```powershell
cd docs
./build.ps1 html
```

### Build HTML Docs (Linux/Mac)

```bash
cd docs
make html
```

### Serve Locally

```powershell
./build.ps1 serve  # Opens http://localhost:8000
```

### Auto-Deploy

Documentation automatically deploys to [GitHub Pages](https://obayne.github.io/AutoFireBase/) when changes are merged to `main`.

## Documentation Standards

### File Naming

- Use **UPPERCASE_WITH_UNDERSCORES.md** for major guides (e.g., `REMOTE_ACCESS_SETUP.md`)
- Use **lowercase_with_underscores.rst** for Sphinx files (e.g., `ci_cd.rst`)
- Use descriptive names that clearly indicate content

### Format Choice

- **Markdown (.md):** Standalone guides, READMEs, user-facing docs
- **reStructuredText (.rst):** Sphinx API docs, cross-referenced technical docs

### Writing Style

- Clear, concise, actionable
- Code examples for all procedures
- Assume beginner-level knowledge
- Use screenshots/diagrams where helpful
- Keep platform-specific instructions separate

### Maintenance

- Update docs with code changes (same PR)
- Remove outdated docs (move to archive/ if historical value)
- Test all code examples before committing
- Run spell check and link validation

## Contributing to Docs

1. **Small changes:** Edit directly via GitHub web interface
2. **Major changes:** Follow standard PR process
3. **New guides:** Use existing docs as templates
4. **API changes:** Sphinx auto-updates, but verify build passes

See [Documentation Guide](DOCUMENTATION_GUIDE.md) for complete authoring guide.

## Need Help?

- **Issues:** [GitHub Issues](https://github.com/Obayne/AutoFireBase/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Obayne/AutoFireBase/discussions)
- **Contributing:** See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

Last Updated: 2025-01-27
