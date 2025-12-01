# Performance Benchmarking

AutoFire uses `pytest-benchmark` to track performance of critical geometry operations.

## Running Benchmarks

### Run all benchmarks

```powershell
pytest tests/benchmarks/ --benchmark-only
```

### Run benchmarks and regular tests

```powershell
pytest tests/
```

### Save benchmark results

```powershell
pytest tests/benchmarks/ --benchmark-autosave
```

### Compare with previous results

```powershell
pytest tests/benchmarks/ --benchmark-compare
```

### Generate detailed report

```powershell
pytest tests/benchmarks/ --benchmark-only --benchmark-histogram
```

## Benchmark Suites

### Lines (`test_bench_lines.py`)

- **Line-line intersection**: Simple, diagonal, parallel, large coordinates
- **Parallel checks**: True/false cases, near-parallel edge cases
- **Distance calculations**: Perpendicular, on-line, diagonal
- **Batch operations**: Multiple intersections, parallel checks
- **Stress tests**: Random lines, many pairs
- **Precision tests**: High-precision tolerance

### Circles (`test_bench_circles.py`)

- **Line-circle intersection**: 2 points, tangent, miss, diagonal
- **Circle-circle intersection**: 2 points, tangent, separate, contained
- **Batch operations**: Multiple lines, grid of circles
- **Stress tests**: Many circles, radial lines
- **Edge cases**: Tiny circles, huge circles, high precision

## Performance Targets

| Operation | Target (µs) | Current |
|-----------|-------------|---------|
| Line-line intersection | < 1 | TBD |
| Parallel check | < 0.5 | TBD |
| Point-line distance | < 0.5 | TBD |
| Line-circle (2 pts) | < 2 | TBD |
| Circle-circle (2 pts) | < 3 | TBD |

## Interpreting Results

Benchmark output shows:

- **Min**: Fastest execution time
- **Max**: Slowest execution time
- **Mean**: Average execution time
- **StdDev**: Variation in timing
- **Median**: Middle value (less affected by outliers)
- **IQR**: Interquartile range (50% of runs fall here)
- **Outliers**: Unusually fast/slow runs
- **Rounds**: Number of iterations

## Continuous Monitoring

Benchmarks run automatically in CI on every PR. Results are saved and compared against `main` branch to detect performance regressions.

### CI Workflow

```yaml
- name: Run benchmarks
  run: pytest tests/benchmarks/ --benchmark-only --benchmark-json=benchmark.json

- name: Compare benchmarks
  run: pytest tests/benchmarks/ --benchmark-compare=main
```

## Adding New Benchmarks

1. Create test file in `tests/benchmarks/`
2. Use `benchmark` fixture from pytest-benchmark
3. Follow naming: `test_benchmark_<operation>_<scenario>`
4. Include docstring explaining what's being tested
5. Assert results to verify correctness

Example:

```python
def test_benchmark_my_operation(benchmark):
    """Benchmark my new geometry operation."""
    result = benchmark(my_function, arg1, arg2)
    assert result is not None  # Verify correctness
```

## Best Practices

- **Warmup**: First few runs may be slower (JIT, caching)
- **Isolation**: Run benchmarks on idle system
- **Consistency**: Use same hardware for comparisons
- **Assertions**: Always verify correctness, not just speed
- **Fixtures**: Reuse test data across benchmarks
- **Batching**: Benchmark realistic workloads (multiple ops)

## Optimization Tips

If benchmarks show performance issues:

1. **Profile first**: Use `cProfile` to find bottlenecks
2. **Vectorize**: Use NumPy for array operations
3. **Cache**: Memoize expensive calculations
4. **Algorithms**: Consider O(n) vs O(n²) approaches
5. **Native code**: Use Cython for critical paths (advanced)

## Resources

- [pytest-benchmark docs](https://pytest-benchmark.readthedocs.io/)
- [Python profiling guide](https://docs.python.org/3/library/profile.html)
- [Performance tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
