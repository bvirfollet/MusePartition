"""
MusePartition - Custom Types
Defines data structures used throughout the pipeline
"""

from typing import NamedTuple


class PitchFrame(NamedTuple):
    """
    Represents a single pitch detection frame.
    
    Attributes:
        time: Timestamp in seconds
        frequency: Detected frequency in Hz
        confidence: Confidence score [0, 1]
    """
    time: float
    frequency: float
    confidence: float


class Note(NamedTuple):
    """
    Represents a musical note with timing information.
    
    Attributes:
        midi_note: MIDI note number [0, 127] (60 = C4)
        start_time: Note onset time in seconds
        duration: Note duration in seconds
    """
    midi_note: int
    start_time: float
    duration: float


class QuantizedNote(NamedTuple):
    """
    Represents a musically quantized note.
    
    Attributes:
        midi_note: MIDI note number [0, 127]
        beat_position: Position in beats from start
        duration_beats: Duration in beats
    """
    midi_note: int
    beat_position: float
    duration_beats: float


class TranscriptionResult(NamedTuple):
    """
    Contains the results of a complete transcription.
    
    Attributes:
        pdf_path: Path to generated PDF score
        musicxml_path: Path to MusicXML file
        midi_path: Path to MIDI file
        bpm: Detected or set tempo in BPM
        num_notes: Number of notes transcribed
        processing_time: Total processing time in seconds
    """
    pdf_path: str
    musicxml_path: str
    midi_path: str
    bpm: float
    num_notes: int
    processing_time: float


class AudioLoadError(Exception):
    """Raised when audio file cannot be loaded."""
    pass


class PitchDetectionError(Exception):
    """Raised when pitch detection fails."""
    pass


class QuantizationError(Exception):
    """Raised when musical quantization fails."""
    pass


class ScoreGenerationError(Exception):
    """Raised when score generation fails."""
    pass
