"""Stub NoteSegmenter pour tests Pipeline"""
from typing import List
from src.types import PitchFrame, Note

class NoteSegmenter:
    def __init__(self, min_note_duration=0.05, reference_frequency=440.0, pitch_tolerance=0.5, debug=False):
        self.min_note_duration = min_note_duration
        self.reference_frequency = reference_frequency
        self.pitch_tolerance = pitch_tolerance
    
    def segment_notes(self, pitch_frames: List[PitchFrame]) -> List[Note]:
        """Segmente en notes."""
        return [
            Note(69, 0.0, 1.0),  # A4
            Note(71, 1.0, 1.0),  # B4
        ]
