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

from musepartition_core.audio_processor import AudioProcessor
from musepartition_core.pitch_detector import PitchDetector
from musepartition_core.note_segmenter import NoteSegmenter
from musepartition_core.quantizer import MusicalQuantizer
from musepartition_core.score_generator import ScoreGenerator
from musepartition_core.pipeline import TranscriptionPipeline
from musepartition_core.utils import (
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
