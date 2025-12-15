# vista/app/handlers/__init__.py
"""
Vista RPC Handlers

Domain-specific RPC handler implementations.
"""

from .demographics import PatientInquiryHandler

__all__ = ["PatientInquiryHandler"]
