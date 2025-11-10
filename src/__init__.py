"""
MusePartition - Audio to Music Score Transcription
Main package initialization
"""

__version__ = "0.1.0"
__author__ = "Bertrand Virfollet"

# Expose main classes at package level
from src.audio_processor import AudioProcessor
from src.pitch_detector import PitchDetector
from src.note_segmenter import NoteSegmenter
from src.quantizer import MusicalQuantizer
from src.utils import DebugTracer, IntermediateStorage

__all__ = [
    "AudioProcessor",
    "PitchDetector",
    "NoteSegmenter",
    "MusicalQuantizer",
    "DebugTracer",
    "IntermediateStorage",
]

