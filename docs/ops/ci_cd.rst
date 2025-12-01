CI/CD Pipeline
==============

AutoFire uses GitHub Actions for continuous integration and deployment.

Workflows
---------

CI Workflow (.github/workflows/ci.yml)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The CI workflow runs on every push and pull request:

1. **Linting**: ruff check for code quality
2. **Formatting**: black format check
3. **Testing**: pytest with coverage reporting
4. **Coverage Upload**: Codecov integration

Build Workflow (.github/workflows/build.yml)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The build workflow creates Windows executables:

1. **Caching**: Virtual environment and PyInstaller build cache
2. **Build**: PyInstaller executable generation
3. **Artifacts**: Upload build artifacts for download
4. **Release**: Create GitHub release on tags

Configuration
-------------

All workflows are configured in ``.github/workflows/`` directory.

Free Services Used
------------------

* **GitHub Actions**: 2,000 minutes/month free
* **Codecov**: Free for open source
* **GitHub Releases**: Free unlimited storage
* **GitHub Pages**: Free static hosting

See Also
--------

* :doc:`build_caching` - Build cache optimization
* :doc:`benchmarking` - Performance testing
* :doc:`monitoring` - Error tracking
