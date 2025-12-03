"""Lightweight OpenTelemetry tracing bootstrap for the app.

This module is optional and safe to import when dependencies are missing.
Enable by setting the AUTOFIRE_TRACING env var to 1/true/yes. It defaults
to exporting traces to the AI Toolkit's local collector at http://localhost:4318.

Environment variables:
- AUTOFIRE_TRACING: enable tracing when set to truthy (1, true, yes)
- OTEL_EXPORTER_OTLP_ENDPOINT: override OTLP/HTTP endpoint (default http://localhost:4318)
- AUTOFIRE_TRACING_CONSOLE: also print spans to console when truthy

Usage:
    from backend.tracing import init_tracing
    init_tracing(service_name="AutoFire")
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TracingConfig:
    service_name: str
    service_version: str | None = None
    otlp_endpoint: str = "http://localhost:4318"
    console_export: bool = False


def _read_version(default: str = "0.0.0") -> str:
    try:
        root = Path(__file__).resolve().parents[1]
        p = root / "VERSION.txt"
        return p.read_text(encoding="utf-8").strip() if p.exists() else default
    except Exception:
        return default


def _init_sentry(service_name: str, service_version: str | None = None) -> None:
    """Initialize Sentry error tracking if available and enabled.

    Enable by setting SENTRY_DSN environment variable.
    """
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return

    try:
        import sentry_sdk
    except ImportError:
        return

    version = service_version or _read_version()
    environment = os.getenv("SENTRY_ENVIRONMENT", "development")

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=f"{service_name}@{version}",
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
        send_default_pii=False,
        attach_stacktrace=True,
        before_send=_sentry_before_send,
    )


def _sentry_before_send(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any] | None:
    """Filter/modify events before sending to Sentry.

    Can be used to scrub sensitive data or filter out certain errors.
    """
    # Filter out keyboard interrupts
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        if isinstance(exc_value, KeyboardInterrupt):
            return None

    return event


def init_tracing(service_name: str, service_version: str | None = None) -> None:
    """Initialize OpenTelemetry tracing and Sentry if dependencies are available.

    This function is safe to call multiple times; repeated calls are ignored.
    """
    # Initialize Sentry first (it has its own global state management)
    _init_sentry(service_name, service_version)

    # Lazy import so missing deps don't crash the app.
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    except Exception:
        # Tracing libs not installed; silently skip.
        return

    # If a tracer provider already exists (initialized earlier), don't replace it.
    if isinstance(trace.get_tracer_provider(), trace.NoOpTracerProvider):
        pass
    else:
        return

    version = service_version or _read_version()
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    console = str(os.getenv("AUTOFIRE_TRACING_CONSOLE", "")).lower() in {"1", "true", "yes"}

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": version,
            "telemetry.sdk.language": "python",
        }
    )

    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # OTLP/HTTP exporter compatible with AI Toolkit default collector
    otlp_exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    if console:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # Auto-instrument common clients (requests). Add more as needed.
    try:
        RequestsInstrumentor().instrument()
    except Exception:
        pass
