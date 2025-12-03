# Performance Baseline Tests

## Overview

Performance baseline tests measure the execution time of critical CAD operations and detect performance regressions. The tests use `pytest-benchmark` for consistent, statistically valid benchmarking.

## Running Locally

### Install dependencies

```powershell
pip install pytest-benchmark
```

### Run all benchmarks

```powershell
pytest tests/performance/ --benchmark-only -v
```

### Run with detailed statistics

```powershell
pytest tests/performance/ --benchmark-only --benchmark-verbose -v
```

### Compare with previous baseline

```powershell
# Save current baseline
pytest tests/performance/ --benchmark-only --benchmark-save=baseline

# Run again and compare
pytest tests/performance/ --benchmark-only --benchmark-compare=baseline
```

### Generate histogram charts

```powershell
pytest tests/performance/ --benchmark-only --benchmark-histogram=histograms/benchmark
```

## Baseline Metrics (v0.7.0)

Current performance baselines on reference hardware (to be established):

| Operation | Expected Time | Threshold |
|-----------|--------------|-----------|
| Line creation | ~1-10 μs | 1.5x |
| Fillet (perpendicular) | ~10-50 μs | 2.0x |
| Fillet (oblique) | ~20-100 μs | 2.0x |
| Point creation | ~1-5 μs | 1.5x |
| Batch lines (100) | ~100-500 μs | 2.0x |
| Batch fillets (10) | ~200-1000 μs | 2.0x |

*Thresholds indicate when performance degradation triggers a warning (e.g., 1.5x = 50% slower).*

## CI Integration

Performance tests run automatically on:

- **Push to main**: Stores results and tracks trends
- **Pull requests**: Compares against main baseline
- **Manual trigger**: Via GitHub Actions UI

### Regression Detection

The CI workflow:

1. Runs benchmarks with 10+ rounds for statistical validity
2. Compares results against stored baselines
3. Alerts via commit comment if performance degrades >150%
4. Does NOT fail the build (warnings only)

### Viewing Results

- **GitHub Actions**: Check "Performance Benchmarks" workflow artifacts
- **Commit comments**: Automatic alerts on regressions
- **Benchmark history**: Tracked in `gh-pages` branch (if configured)

## Adding New Benchmarks

1. Add test function to `tests/performance/test_baselines.py`:

   ```python
   @pytest.mark.benchmark
   def test_new_operation_baseline(self, benchmark):
       """Baseline: Your operation description."""

       def run_operation():
           # Your operation code
           return result

       result = benchmark(run_operation)
       assert result is not None
       # Baseline: ~expected time
   ```

2. Run locally to establish baseline:

   ```powershell
   pytest tests/performance/test_baselines.py::TestPerformanceBaselines::test_new_operation_baseline --benchmark-only -v
   ```

3. Update `PERFORMANCE_THRESHOLDS` dict with regression threshold

4. Document expected time in this README

## Performance Optimization Workflow

1. **Identify bottleneck**: Run benchmarks to find slow operations
2. **Optimize code**: Improve algorithm or implementation
3. **Verify improvement**: Re-run benchmarks and compare
4. **Document**: Update baseline metrics in this README

Example:

```powershell
# Before optimization
pytest tests/performance/ --benchmark-only --benchmark-save=before

# ... make code changes ...

# After optimization
pytest tests/performance/ --benchmark-only --benchmark-compare=before
```

## Troubleshooting

### Tests fail with "benchmark not available"

Install pytest-benchmark: `pip install pytest-benchmark`

### Results vary widely

- Close other applications to reduce noise
- Use `--benchmark-warmup=on` for JIT optimization
- Increase rounds: `--benchmark-min-rounds=20`

### Benchmark too fast to measure

pytest-benchmark automatically calibrates rounds for sub-microsecond operations.

### Want to skip benchmarks during normal tests

Benchmarks are marked with `@pytest.mark.benchmark`. Use:

```powershell
# Run without benchmarks
pytest tests/ -m "not benchmark"

# Run only benchmarks
pytest tests/ -m benchmark
```

## Reference

- [pytest-benchmark documentation](https://pytest-benchmark.readthedocs.io/)
- [GitHub Action Benchmark](https://github.com/benchmark-action/github-action-benchmark)

## Future Enhancements

- [ ] Add DXF import/export benchmarks
- [ ] Add GUI rendering benchmarks (requires headless setup)
- [ ] Track memory usage alongside execution time
- [ ] Add device placement operation benchmarks
- [ ] Set up benchmark comparison bot for PRs
