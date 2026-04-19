import os
import logging
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

logger = logging.getLogger(__name__)


def setup_observability(app: FastAPI):
    try:
        resource = Resource(attributes={
            "service.name": "course-ai-assistant",
            "service.version": "1.0.0"
        })
        tracer_provider = TracerProvider(resource=resource)

        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
        if otlp_endpoint:
            exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
            tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
            logger.info(f"OTel traces → {otlp_endpoint}")

        trace.set_tracer_provider(tracer_provider)
        FastAPIInstrumentor.instrument_app(app)
    except Exception as e:
        logger.warning(f"OTel init skipped: {e}")

    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator(
            excluded_handlers=["/health", "/docs", "/openapi.json", "/redoc"]
        ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

        logger.info("Prometheus metrics enabled at /metrics")
    except Exception as e:
        logger.warning(f"Prometheus init skipped: {e}")

    print("Observability stack initialized (OTel + Prometheus)")