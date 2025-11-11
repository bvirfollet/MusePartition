"""Stub MusicalQuantizer pour tests Pipeline"""
from typing import List, Tuple
from src.types import Note, QuantizedNote
import numpy as np

class MusicalQuantizer:
    def __init__(self, bpm=None, time_signature="4/4", quantization_grid="1/16", feel="straight", debug=False):
        self.bpm = bpm
        self.time_signature = time_signature
        self.quantization_grid = quantization_grid
        self.feel = feel
    
    def detect_tempo(self, audio, sr) -> float:
        """Détecte tempo."""
        return 120.0
    
    def quantize_notes(self, notes: List[Note], bpm=None, audio=None, sr=None) -> Tuple[List[QuantizedNote], float]:
        """Quantifie notes."""
        detected_bpm = bpm if bpm else 120.0
        quantized = [
            QuantizedNote(69, 0.0, 1.0),
            QuantizedNote(71, 1.0, 1.0),
        ]
        return quantized, detected_bpm
