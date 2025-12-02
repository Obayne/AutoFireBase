# Build Caching Guide

AutoFire implements intelligent build caching to dramatically speed up PyInstaller builds.

## Quick Start

### Use the cached build script

```powershell
.\Build_AutoFire_Cached.ps1
```

**First build**: Normal speed (~2-5 minutes)
**Subsequent builds**: Much faster (~30-60 seconds if no changes)
**No changes**: Instant (skips rebuild entirely)

## How It Works

### Local Caching

The cached build script (`Build_AutoFire_Cached.ps1`) uses intelligent change detection:

1. **Source Hash Tracking**
   - Calculates MD5 hash of all Python source files
   - Stores hash in `build/.cache/build.hash`
   - Skips rebuild if source unchanged

2. **Dependency Tracking**
   - Tracks `requirements.txt` changes
   - Stores hash in `build/.cache/deps.hash`
   - Skips `pip install` if deps unchanged

3. **Build Cache Retention**
   - Keeps `build/` directory between runs
   - PyInstaller reuses compiled bytecode
   - Only rebuilds changed modules

### CI/CD Caching (GitHub Actions)

The build workflow (`.github/workflows/build.yml`) uses GitHub Actions cache:

1. **Pip Cache**
   - Built-in `cache: 'pip'` in setup-python action
   - Caches downloaded packages

2. **Virtual Environment Cache**
   - Caches entire `.venv` directory
   - Key: OS + Python version + requirements hash
   - Restores in seconds vs. minutes to install

3. **PyInstaller Build Cache**
   - Caches `build/` and `dist/` directories
   - Key: OS + source file hashes
   - Reuses compiled artifacts

## Performance Comparison

| Scenario | Standard Build | Cached Build | Speedup |
|----------|---------------|--------------|---------|
| **Fresh build** | ~3-5 min | ~3-5 min | 1x (baseline) |
| **Deps changed** | ~3-5 min | ~2-3 min | 1.5x |
| **Source changed** | ~3-5 min | ~1-2 min | 2-3x |
| **No changes** | ~3-5 min | ~5 sec | 30-60x |

## Cache Management

### View cache status

```powershell
# Check if caches exist
Test-Path build/.cache/build.hash
Test-Path build/.cache/deps.hash
```

### Force rebuild

```powershell
# Clear source hash (forces rebuild)
Remove-Item build/.cache/build.hash

# Clear dependency hash (forces reinstall)
Remove-Item build/.cache/deps.hash

# Clear everything (complete rebuild)
Remove-Item build -Recurse -Force
```

### GitHub Actions cache

```bash
# Caches automatically expire after 7 days of no use
# Manual clear: Settings → Actions → Caches → Delete
```

## Optimization Tips

### For Faster Local Builds

1. **Use SSD**: PyInstaller is I/O intensive
2. **Exclude from antivirus**: Add `build/` and `dist/` to exclusions
3. **Close resource-heavy apps**: More RAM = faster builds
4. **Use cached script**: Always prefer `Build_AutoFire_Cached.ps1`

### For Faster CI Builds

1. **Minimal changes**: Smaller diffs = better cache hits
2. **Stable dependencies**: Pin versions in `requirements.txt`
3. **Separate build job**: Run builds only when needed
4. **Parallel builds**: Use matrix for multiple platforms

## Advanced: ccache Integration (Future)

For even faster builds, consider integrating ccache:

```powershell
# Install ccache
choco install ccache

# Configure PyInstaller to use ccache
$env:CC = "ccache gcc"
$env:CXX = "ccache g++"
```

This caches C extension compilation (30-50% faster for packages with C extensions).

## Troubleshooting

### "Build is up to date!" but I made changes

**Cause**: Cache hash not detecting your changes
**Fix**:

```powershell
Remove-Item build/.cache/build.hash
.\Build_AutoFire_Cached.ps1
```

### Builds taking longer after caching enabled

**Cause**: Hash calculation overhead for large projects
**Fix**: Optimize by excluding test files:

```powershell
# Edit Build_AutoFire_Cached.ps1
# Change: Get-ChildItem -Path "app", "backend", ...
# To:     Get-ChildItem -Path "app", "backend", ... -Exclude "test_*"
```

### GitHub Actions cache not working

**Cause**: Cache key mismatch
**Fix**: Check workflow logs for "Cache hit" messages. If missing:

1. Verify `hashFiles()` patterns are correct
2. Check cache size limits (10GB per repo)
3. Review cache key in workflow file

### Out of disk space

**Cause**: Build artifacts accumulating
**Fix**:

```powershell
# Clean old builds
Remove-Item dist -Recurse -Force
Remove-Item build -Recurse -Force

# Keep cache
New-Item -ItemType Directory build/.cache -Force
```

## Monitoring

### View cache effectiveness

```powershell
# Local cache stats
Write-Host "Build cache size:"
(Get-ChildItem build -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host "Last build:"
(Get-Item build/.cache/build.hash).LastWriteTime
```

### CI cache stats

Check GitHub Actions logs for:

- "Cache restored from key: ..."
- "Cache saved with key: ..."
- Build time comparisons

## Resources

- [PyInstaller Performance](https://pyinstaller.org/en/stable/performance.html)
- [GitHub Actions Cache](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [ccache documentation](https://ccache.dev/)
