"""
Living Synthesizer - Weather-controlled synthesizer system.

This package provides tools for monitoring weather stations and controlling
MIDI devices based on real-time environmental data.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .monitor import WS2000Monitor
from .wind_smoother import WindSmoother

__all__ = ["WS2000Monitor", "WindSmoother"]
