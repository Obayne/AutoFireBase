# Tracing

This workspace includes optional OpenTelemetry tracing you can enable without code changes.

- Default OTLP/HTTP endpoint: <http://localhost:4318> (AI Toolkit collector)
- Enable via environment: `AUTOFIRE_TRACING=1`
- Optional console spans: `AUTOFIRE_TRACING_CONSOLE=1`
- Override endpoint: `OTEL_EXPORTER_OTLP_ENDPOINT=http://host:4318`

## How it works

- A tiny bootstrap in the app startup calls `backend.tracing.init_tracing()` if `AUTOFIRE_TRACING` is truthy.
- If OpenTelemetry packages are missing, initialization is skipped silently.
- When enabled, spans are exported to the OTLP endpoint and (optionally) printed to the console.
- HTTP calls made via `requests` are auto-instrumented.

## Windows PowerShell (user-level)

```powershell
[Environment]::SetEnvironmentVariable('AUTOFIRE_TRACING','1','User')
# Optional: also export to console
[Environment]::SetEnvironmentVariable('AUTOFIRE_TRACING_CONSOLE','1','User')
# Optional: override collector endpoint
[Environment]::SetEnvironmentVariable('OTEL_EXPORTER_OTLP_ENDPOINT','http://localhost:4318','User')
```

Restart VS Code or your shell after setting env vars.

## Collector / Viewer

- Use AI Toolkit's tracing viewer, which starts a local collector on <http://localhost:4318>.
- Alternatively, run any OTLP-compatible collector that accepts HTTP.

## Notes

- Tracing is non-blocking and best-effort; failures never prevent the app from starting.
- You can add more auto-instrumentations (e.g., SQLite, logging) later; the bootstrap is designed to be extended.
