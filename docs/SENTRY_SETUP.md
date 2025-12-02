# Sentry Error Tracking Setup

LV CAD integrates with [Sentry](https://sentry.io) for production error tracking and performance monitoring.

## Quick Start

### 1. Get Sentry DSN

1. Create account at [sentry.io](https://sentry.io)
2. Create new project (choose Python)
3. Copy your DSN (looks like `https://xxxxx@xxxxx.ingest.sentry.io/xxxxx`)

### 2. Configure Environment

Set the `SENTRY_DSN` environment variable:

**Windows (PowerShell):**

```powershell
$env:SENTRY_DSN = "https://xxxxx@xxxxx.ingest.sentry.io/xxxxx"
```

**Windows (Persistent):**

```powershell
[System.Environment]::SetEnvironmentVariable('SENTRY_DSN', 'https://xxxxx@xxxxx.ingest.sentry.io/xxxxx', 'User')
```

**Linux/Mac:**

```bash
export SENTRY_DSN="https://xxxxx@xxxxx.ingest.sentry.io/xxxxx"
```

### 3. Run Application

Sentry will automatically initialize when the application starts if `SENTRY_DSN` is set.

## Configuration Options

All configuration via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRY_DSN` | (none) | **Required.** Sentry project DSN |
| `SENTRY_ENVIRONMENT` | `development` | Environment name (production, staging, etc.) |
| `SENTRY_TRACES_SAMPLE_RATE` | `0.1` | Performance monitoring sample rate (0.0-1.0) |
| `SENTRY_PROFILES_SAMPLE_RATE` | `0.1` | Profiling sample rate (0.0-1.0) |

### Example Production Configuration

```powershell
$env:SENTRY_DSN = "https://xxxxx@xxxxx.ingest.sentry.io/xxxxx"
$env:SENTRY_ENVIRONMENT = "production"
$env:SENTRY_TRACES_SAMPLE_RATE = "0.2"
$env:SENTRY_PROFILES_SAMPLE_RATE = "0.1"
```

## What Gets Tracked

### Automatically Tracked

- **Unhandled exceptions** - Any uncaught errors
- **Performance data** - Slow operations and bottlenecks
- **Release versions** - Tied to `VERSION.txt`
- **Environment context** - OS, Python version, dependencies

### Not Tracked

- **Personal data** - `send_default_pii=False` by default
- **Keyboard interrupts** - Filtered out
- **Expected errors** - Handled exceptions don't report unless explicitly captured

## Manual Error Capture

```python
import sentry_sdk

# Capture exception with context
try:
    risky_operation()
except Exception as e:
    sentry_sdk.capture_exception(e)
```

```python
# Capture custom message
sentry_sdk.capture_message("User attempted invalid operation", level="warning")
```

```python
# Add breadcrumbs for debugging
sentry_sdk.add_breadcrumb(
    category="user_action",
    message="User opened device browser",
    level="info"
)
```

## Testing Sentry Integration

```python
# Test error capture
python -c "from backend.tracing import init_tracing; init_tracing('AutoFire'); import sentry_sdk; sentry_sdk.capture_message('Test message from LV CAD')"
```

Check your Sentry dashboard - you should see the test message within seconds.

## Deployment

### Production Checklist

- [x] Set `SENTRY_DSN` in production environment
- [x] Set `SENTRY_ENVIRONMENT=production`
- [x] Verify `VERSION.txt` is up-to-date
- [x] Test error reporting in staging first
- [x] Review sample rates for cost control

### Installer Integration

For Windows installer (NSIS/WiX):

```nsis
; Prompt for Sentry DSN during installation (optional)
!insertmacro MUI_PAGE_CUSTOM SentryConfigPage
```

Or configure post-installation via registry/config file.

## Privacy & Compliance

- **No PII by default** - `send_default_pii=False`
- **Local filtering** - `_sentry_before_send()` scrubs sensitive data
- **EU compliance** - Use Sentry EU region if required
- **Data retention** - Configure in Sentry project settings

## Troubleshooting

**Sentry not capturing errors:**

1. Verify `SENTRY_DSN` is set: `echo $env:SENTRY_DSN`
2. Check sentry-sdk is installed: `pip list | Select-String sentry`
3. Look for initialization errors in console

**Too many events:**

- Reduce `SENTRY_TRACES_SAMPLE_RATE`
- Add filters in `_sentry_before_send()`
- Use Sentry's rate limiting features

**Missing context:**

- Add breadcrumbs before errors occur
- Set user context: `sentry_sdk.set_user({"id": user_id})`
- Add tags: `sentry_sdk.set_tag("feature", "device_placement")`

## Cost Optimization

Sentry pricing based on events:

- **Free tier:** 5,000 errors/month, 10,000 performance transactions/month
- **Optimize:** Use sampling rates, filter noise, aggregate similar errors

Recommended settings for small teams:

```
SENTRY_TRACES_SAMPLE_RATE=0.1    # 10% of transactions
SENTRY_PROFILES_SAMPLE_RATE=0.05 # 5% of transactions
```

## Resources

- [Sentry Python SDK Docs](https://docs.sentry.io/platforms/python/)
- [Performance Monitoring](https://docs.sentry.io/product/performance/)
- [Release Tracking](https://docs.sentry.io/product/releases/)
- [Best Practices](https://docs.sentry.io/platforms/python/best-practices/)
