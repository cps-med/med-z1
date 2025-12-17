# vista/app/handlers/__init__.py
"""
Vista RPC Handlers

Domain-specific RPC handler implementations.
"""

from .demographics import PatientInquiryHandler
from .vitals import LatestVitalsHandler

__all__ = ["PatientInquiryHandler", "LatestVitalsHandler"]
