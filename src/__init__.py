"""
MusePartition - Audio to Music Score Transcription
"""

from src.types import (
    PitchFrame,
    Note,
    QuantizedNote,
    TranscriptionResult,
    AudioLoadError,
    PitchDetectionError,
    QuantizationError,
    ScoreGenerationError,
)

from src.audio_processor import AudioProcessor
from src.pitch_detector import PitchDetector
from src.note_segmenter import NoteSegmenter
from src.quantizer import MusicalQuantizer
from src.score_generator import ScoreGenerator
from src.transcription_pipeline import TranscriptionPipeline
from src.utils import (
    DebugTracer,
    IntermediateStorage,
    format_duration,
    format_frequency,
    print_summary_stats,
)

__all__ = [
    # Types
    "PitchFrame",
    "Note",
    "QuantizedNote",
    "TranscriptionResult",
    # Exceptions
    "AudioLoadError",
    "PitchDetectionError",
    "QuantizationError",
    "ScoreGenerationError",
    # Modules
    "AudioProcessor",
    "PitchDetector",
    "NoteSegmenter",
    "MusicalQuantizer",
    "ScoreGenerator",
    "TranscriptionPipeline",
    # Utils
    "DebugTracer",
    "IntermediateStorage",
    "format_duration",
    "format_frequency",
    "print_summary_stats",
]

__version__ = "0.6.0"  # Session 6 completed
