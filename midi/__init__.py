"""
MIDI control modules for the Living Synthesizer.

This package contains modules to contorl midi signals with environmental signals.
"""

from .sdr_to_midi import SDRModulator
from .signal_conversion import SignalConverter
from .digitone_control import DigitoneControl

__all__ = ["SDRModulator", "SignalConverter", "DigitoneControl"]
