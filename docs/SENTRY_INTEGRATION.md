# Error Tracking with Sentry

AutoFire uses [Sentry](https://sentry.io/) for automatic error tracking and performance monitoring.

## 🆓 Free Tier

- **5,000 errors/month** - Perfect for development and small teams
- **10,000 performance units/month**
- **30-day error retention**
- **Full feature set** (no limitations)
- **Zero cost** - completely free for open source and small projects

## Quick Setup

### 1. Create Free Sentry Account

1. Go to [sentry.io](https://sentry.io/signup/)
2. Sign up (free, no credit card required)
3. Create a new project:
   - Platform: **Python**
   - Project name: **AutoFire**

### 2. Get Your DSN

After creating project, copy the DSN (looks like):

```
https://abc123def456@o1234567.ingest.sentry.io/7654321
```

### 3. Configure AutoFire

Add DSN to `.env` file:

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your DSN
SENTRY_DSN=https://your-key@o1234567.ingest.sentry.io/your-project
AUTOFIRE_ENV=production
```

### 4. Enable in Application

```python
# In app/main.py or boot.py
from app.monitoring import init_sentry

# Initialize Sentry (reads DSN from environment)
init_sentry()

# Or disable for development
init_sentry(enable=False)
```

Done! Errors are now automatically tracked.

## Usage Examples

### Automatic Error Tracking

Sentry automatically captures unhandled exceptions:

```python
from app.monitoring import init_sentry

init_sentry()

# This error will be automatically reported
raise ValueError("Something went wrong!")
```

### Manual Error Capture

```python
from app.monitoring import capture_exception, capture_message

try:
    risky_operation()
except Exception as e:
    # Capture exception with context
    capture_exception(
        e,
        level="warning",
        tags={"operation": "dxf_import"},
        extra={"filename": "plan.dxf"}
    )
```

### User Context

```python
from app.monitoring import set_user

# Set user info (helps track which users hit errors)
set_user(
    user_id="12345",
    email="user@example.com",  # Optional
    username="john_doe"
)
```

### Breadcrumbs (Event Trail)

```python
from app.monitoring import add_breadcrumb

# Add breadcrumbs to track user actions
add_breadcrumb("User opened file", category="file", data={"name": "plan.dxf"})
add_breadcrumb("Started DXF import", category="import")
add_breadcrumb("Parsing entities", category="import", data={"count": 150})

# If error occurs, breadcrumbs show what led to it
```

### Custom Messages

```python
from app.monitoring import capture_message

# Report non-error events
capture_message("User performed bulk import", level="info")
capture_message("Unusual file size detected", level="warning", extra={"size_mb": 500})
```

### Context and Tags

```python
from app.monitoring import configure_scope

def process_import(filename):
    def set_import_context(scope):
        scope.set_tag("feature", "import")
        scope.set_tag("file_type", "dxf")
        scope.set_extra("filename", filename)

    configure_scope(set_import_context)

    # Any errors here will have this context
    import_dxf(filename)
```

## Integration Points

### Main Application Startup

```python
# app/main.py
from app.monitoring import init_sentry
from PySide6.QtWidgets import QApplication
import sys

def main():
    # Initialize Sentry early
    init_sentry()

    app = QApplication(sys.argv)

    # Your app code...

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

### Qt Exception Handler

```python
# app/main.py
from app.monitoring import capture_exception
import sys

def qt_exception_handler(exc_type, exc_value, exc_traceback):
    """Custom exception handler for Qt applications."""
    if exc_type == KeyboardInterrupt:
        sys.exit(0)

    # Log to Sentry
    capture_exception(exc_value)

    # Show error dialog
    show_error_dialog(exc_value)

# Set exception handler
sys.excepthook = qt_exception_handler
```

### Command-Line Tools

```python
# tools/cli/geom_ops.py
from app.monitoring import init_sentry, add_breadcrumb

def main():
    # Enable for production CLI usage
    init_sentry(environment="cli")

    add_breadcrumb("CLI tool started", category="cli")

    # Your CLI code...

if __name__ == "__main__":
    main()
```

## Configuration Options

### Environment Detection

```python
# Automatic environment detection
init_sentry()  # Uses AUTOFIRE_ENV or defaults to 'production'

# Explicit environment
init_sentry(environment="staging")
init_sentry(environment="development")
```

### Sampling Rates

```python
# Sample all errors, 10% of performance traces
init_sentry(
    sample_rate=1.0,          # 100% of errors
    traces_sample_rate=0.1    # 10% of transactions
)

# Reduce sampling for high-volume scenarios
init_sentry(
    sample_rate=0.5,          # 50% of errors
    traces_sample_rate=0.01   # 1% of transactions
)
```

### Development Mode

```python
# Disable in development
import os

enable_sentry = os.getenv("AUTOFIRE_ENV") == "production"
init_sentry(enable=enable_sentry)
```

## Sentry Dashboard

After setup, view errors at [sentry.io](https://sentry.io/):

1. **Issues**: All errors grouped by type
2. **Performance**: Transaction traces and bottlenecks
3. **Releases**: Track errors by version
4. **Alerts**: Email/Slack notifications for new errors

### Useful Features

- **Stack traces**: Full Python traceback
- **Breadcrumbs**: User actions leading to error
- **Context**: Tags, user info, environment
- **Source maps**: Link to exact code line
- **Trends**: Error frequency over time
- **Ignoring**: Mark false positives as ignored

## Best Practices

### 1. Use Breadcrumbs Liberally

```python
# Good: Track user journey
add_breadcrumb("Opened project", category="navigation")
add_breadcrumb("Clicked import button", category="ui")
add_breadcrumb("Selected file", category="file", data={"path": filepath})
add_breadcrumb("Started parsing", category="import")
# Error occurs here - full context available!
```

### 2. Add Context to Errors

```python
# Good: Rich context
try:
    import_dxf(file)
except Exception as e:
    capture_exception(
        e,
        level="error",
        tags={
            "feature": "import",
            "file_type": "dxf",
        },
        extra={
            "filename": file.name,
            "file_size": file.size,
            "entity_count": len(entities),
        }
    )
```

### 3. Set Release Versions

```python
# In deployment, set release
init_sentry(
    dsn=dsn,
    release=f"autofire@{version}"  # e.g., "autofire@0.4.7"
)

# Track which version has errors
```

### 4. Use Environments

```python
# Separate dev/staging/prod errors
init_sentry(environment="production")  # Real users
init_sentry(environment="staging")     # QA testing
init_sentry(environment="development") # Dev machines
```

### 5. Protect PII (Personally Identifiable Information)

```python
# Good: Don't send sensitive data
set_user(user_id="hashed_id_123")  # Hash or anonymize

# Bad: Don't do this
set_user(email="real.email@company.com")  # Could leak PII
```

## Troubleshooting

### "Sentry not initialized"

**Cause**: No DSN provided
**Fix**: Add `SENTRY_DSN` to `.env` file

### Errors not appearing in dashboard

**Cause**: Environment mismatch or disabled
**Fix**:

```python
# Check if actually enabled
init_sentry()  # Should print "✓ Sentry initialized"

# Verify DSN is set
import os
print(os.getenv("SENTRY_DSN"))
```

### Too many events (quota exceeded)

**Cause**: Hitting free tier limit (5k/month)
**Fix**: Reduce sampling

```python
init_sentry(
    sample_rate=0.5,         # Sample 50% of errors
    traces_sample_rate=0.01  # Sample 1% of traces
)
```

### ImportError: sentry_sdk not installed

**Fix**: Install Sentry SDK

```powershell
pip install sentry-sdk[pyside6]
```

## Cost & Quotas

### Free Tier Limits

- **5,000 errors/month**
- **10,000 performance units/month**
- **30-day retention**
- **1 user**

### Paid Plans (if needed)

- **Developer**: $26/month (50k errors)
- **Team**: $80/month (100k errors)
- **Business**: Custom pricing

**Recommendation**: Start with free tier. Upgrade only if you exceed limits.

## Resources

- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)
- [Sentry PySide6 Integration](https://docs.sentry.io/platforms/python/integrations/pyside/)
- [Best Practices](https://docs.sentry.io/product/best-practices/)
- [Pricing](https://sentry.io/pricing/)

## Alternative: Self-Hosted Sentry

For complete control, self-host Sentry:

```bash
# Install via Docker
git clone https://github.com/getsentry/self-hosted.git
cd self-hosted
./install.sh

# Free, unlimited events, requires own server
```

**Pros**: Unlimited events, full control
**Cons**: Requires server, maintenance

For most projects, hosted free tier is recommended.
