# Monitoring and Observability

## Overview

AutoFireBase includes multiple monitoring capabilities for tracking application health, performance, and errors.

## Error Tracking (Sentry)

### Setup

1. Create a Sentry account at https://sentry.io
2. Create a new project for AutoFireBase
3. Copy your DSN (Data Source Name)
4. Configure in `app/logging_config.py`:

```python
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN_HERE",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)
```

### Features

- **Automatic Error Capture**: Unhandled exceptions reported to Sentry
- **Performance Monitoring**: Transaction tracing for slow operations
- **Release Tracking**: Correlate errors with specific versions
- **User Context**: Associate errors with user actions

### Best Practices

- Use breadcrumbs for debugging context
- Tag errors by module/feature
- Set up alerts for critical errors
- Review performance insights weekly

## Application Logging

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical issues requiring immediate attention

### Log Locations

- **Development**: `debug_run.log` (current directory)
- **Production**: `%APPDATA%\AutoFire\logs\autofire.log`
- **CI/CD**: Console output + artifacts

### Configuration

Edit `app/logging_config.py`:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autofire.log'),
        logging.StreamHandler()
    ]
)
```

## Performance Monitoring

### Benchmarks

Run performance tests:

```powershell
pytest tests/benchmarks/ --benchmark-only
```

Key metrics tracked:
- Geometry algorithm speed (trim, extend, intersect)
- DXF import/export performance
- UI responsiveness (frame time)

### Profiling

Profile specific functions:

```powershell
python -m cProfile -o profile.stats app/main.py
python -m pstats profile.stats
```

Analyze with:
```python
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
```

## Metrics Collection

### Application Metrics

AutoFireBase tracks:
- Session duration
- Feature usage frequency
- File operations (opens, saves, exports)
- Error frequency by type
- Performance benchmarks

### System Metrics

Monitor:
- CPU usage
- Memory consumption
- Disk I/O
- Network latency (for future cloud features)

## Health Checks

### Application Health

```python
# Check if critical components are loaded
def health_check():
    checks = {
        "qt_loaded": QtWidgets.QApplication.instance() is not None,
        "cad_core_loaded": "cad_core" in sys.modules,
        "dxf_support": "ezdxf" in sys.modules,
    }
    return all(checks.values()), checks
```

### Database Health

For future SQLite integration:

```python
def database_health():
    try:
        conn = sqlite3.connect('autofire.db')
        conn.execute("SELECT 1")
        return True
    except Exception as e:
        log.error(f"Database health check failed: {e}")
        return False
```

## Alerting

### Sentry Alerts

Configure in Sentry dashboard:
- Alert on new error types
- Alert on error spike (>10 in 5 minutes)
- Alert on performance degradation
- Alert on release regressions

### Custom Alerts

For self-hosted monitoring:

```python
def alert_on_critical_error(error_type, message):
    """Send alert for critical errors."""
    if should_alert(error_type):
        send_notification(
            subject=f"AutoFire Critical Error: {error_type}",
            body=message,
            priority="high"
        )
```

## Dashboard

### Metrics to Monitor

1. **Error Rate**: Errors per session
2. **Performance**: P50, P95, P99 response times
3. **Usage**: Daily/weekly active users
4. **Features**: Most-used tools
5. **Stability**: Crash-free sessions percentage

### Visualization Tools

- **Sentry Dashboard**: Error and performance tracking
- **pytest-benchmark**: Performance regression detection
- **Custom Scripts**: Generate HTML reports from logs

## Troubleshooting with Monitoring

### High Memory Usage

1. Check Sentry performance traces
2. Review profiler output
3. Analyze heap dumps
4. Check for memory leaks in Qt objects

### Slow Performance

1. Review benchmark results
2. Check CPU profiler
3. Analyze slow transactions in Sentry
4. Verify disk I/O isn't bottleneck

### Frequent Crashes

1. Review Sentry error reports
2. Check stack traces
3. Identify common patterns
4. Reproduce with debug logging

## Compliance and Privacy

- **No PII Logging**: Avoid logging user-identifiable information
- **Data Retention**: Logs retained for 30 days (configurable)
- **Opt-out**: Provide mechanism to disable telemetry
- **GDPR Compliance**: Allow data export/deletion

## Maintenance

### Regular Tasks

- **Daily**: Check Sentry for new errors
- **Weekly**: Review performance metrics
- **Monthly**: Analyze usage patterns
- **Quarterly**: Update monitoring strategy

### Log Rotation

Configure log rotation to prevent disk fill:

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'autofire.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

## Integration with CI/CD

GitHub Actions automatically:
- Run performance benchmarks
- Upload benchmark results as artifacts
- Fail on performance regressions >20%
- Report test coverage

## Future Enhancements

- Real-time monitoring dashboard
- Predictive failure detection
- User behavior analytics
- A/B testing framework
- Distributed tracing (if multi-process)

## Resources

- Sentry Documentation: https://docs.sentry.io/
- Python logging: https://docs.python.org/3/library/logging.html
- pytest-benchmark: https://pytest-benchmark.readthedocs.io/
