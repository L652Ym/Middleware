"""
Arize Phoenix Integration for LangChain Middleware

This module provides Phoenix tracing and monitoring capabilities for LangChain applications.
Phoenix allows you to track, visualize, and debug LLM application behavior in real-time.
"""

import os
from typing import Optional
import phoenix as px
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor


class PhoenixTracer:
    """
    Manages Arize Phoenix tracing for LangChain applications.

    Features:
    - Automatic tracing of LangChain model calls
    - Real-time monitoring dashboard
    - Performance metrics and analytics
    - Request/response logging
    """

    def __init__(self,
                 enabled: bool = None,
                 host: str = None,
                 port: int = None,
                 auto_instrument: bool = True):
        """
        Initialize Phoenix tracer

        Args:
            enabled: Enable/disable Phoenix tracing (defaults to env PHOENIX_ENABLED)
            host: Phoenix server host (defaults to env PHOENIX_HOST or '127.0.0.1')
            port: Phoenix server port (defaults to env PHOENIX_PORT or 6006)
            auto_instrument: Automatically instrument LangChain (default True)
        """
        # Read from environment variables with defaults
        self.enabled = enabled if enabled is not None else os.getenv("PHOENIX_ENABLED", "true").lower() == "true"

        # Clean up host (remove http:// or https:// if present)
        raw_host = host or os.getenv("PHOENIX_HOST", "127.0.0.1")
        self.host = raw_host.replace("http://", "").replace("https://", "").strip()

        self.port = int(port or os.getenv("PHOENIX_PORT", "6006"))
        self.session = None
        self.tracer_provider = None

        if self.enabled:
            self._start_phoenix()
            if auto_instrument:
                self._instrument_langchain()

    def _start_phoenix(self):
        """Start Phoenix session and initialize tracing"""
        try:
            # Launch Phoenix in-process
            self.session = px.launch_app()

            print(f"\n{'='*60}")
            print(f"[PHOENIX] Arize Phoenix Started Successfully")
            print(f"[PHOENIX] Dashboard URL: http://{self.host}:{self.port}")
            print(f"[PHOENIX] Open the dashboard to view real-time traces")
            print(f"{'='*60}\n")

            # Register Phoenix as the OTEL tracer
            self.tracer_provider = register()

        except Exception as e:
            print(f"\n{'='*60}")
            print(f"[PHOENIX WARNING] Failed to start Phoenix")
            print(f"[PHOENIX WARNING] Error: {str(e)}")
            print(f"[PHOENIX WARNING] Agent will continue without tracing")
            print(f"[PHOENIX WARNING] To disable this warning, set PHOENIX_ENABLED=false in .env")
            print(f"{'='*60}\n")
            self.enabled = False

    def _instrument_langchain(self):
        """Instrument LangChain and LangGraph for automatic tracing"""
        if not self.enabled:
            return

        try:
            # Instrument LangChain
            LangChainInstrumentor().instrument()
            print(f"[PHOENIX] ✓ LangChain instrumentation enabled")

            # Try to instrument LangGraph if available
            try:
                # LangGraph 追踪目前通过 LangChain instrumentation 自动支持
                # 但我们可以添加额外的日志
                print(f"[PHOENIX] ✓ LangGraph will be traced via LangChain instrumentation")
            except Exception as e:
                print(f"[PHOENIX] Note: {str(e)}")

            print(f"[PHOENIX] All LangChain/LangGraph calls will be traced automatically\n")

        except Exception as e:
            print(f"\n[PHOENIX WARNING] Failed to instrument: {str(e)}\n")

    def get_dashboard_url(self) -> str:
        """Get the Phoenix dashboard URL"""
        if self.enabled and self.session:
            return f"http://{self.host}:{self.port}"
        return ""

    def is_enabled(self) -> bool:
        """Check if Phoenix tracing is enabled"""
        return self.enabled

    def stop(self):
        """Stop Phoenix session"""
        if self.session:
            try:
                # Phoenix sessions are managed automatically
                print("\n[PHOENIX] Session ended")
            except Exception as e:
                print(f"\n[PHOENIX WARNING] Error stopping session: {str(e)}")


# Global Phoenix tracer instance
_phoenix_tracer: Optional[PhoenixTracer] = None


def init_phoenix(enabled: bool = None,
                host: str = None,
                port: int = None,
                auto_instrument: bool = True) -> PhoenixTracer:
    """
    Initialize Phoenix tracing (singleton pattern)

    Args:
        enabled: Enable/disable Phoenix tracing
        host: Phoenix server host
        port: Phoenix server port
        auto_instrument: Automatically instrument LangChain

    Returns:
        PhoenixTracer instance
    """
    global _phoenix_tracer

    if _phoenix_tracer is None:
        _phoenix_tracer = PhoenixTracer(
            enabled=enabled,
            host=host,
            port=port,
            auto_instrument=auto_instrument
        )

    return _phoenix_tracer


def get_phoenix_tracer() -> Optional[PhoenixTracer]:
    """
    Get the global Phoenix tracer instance

    Returns:
        PhoenixTracer instance or None if not initialized
    """
    return _phoenix_tracer


def stop_phoenix():
    """Stop the global Phoenix tracer"""
    global _phoenix_tracer

    if _phoenix_tracer:
        _phoenix_tracer.stop()
        _phoenix_tracer = None
