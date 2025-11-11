"""Stub PitchDetector pour tests Pipeline"""
from typing import List
from src.types import PitchFrame

class PitchDetector:
    def __init__(self, model_capacity="medium", confidence_threshold=0.5, step_size=10):
        self.model_capacity = model_capacity
        self.confidence_threshold = confidence_threshold
        self.step_size = step_size
    
    def detect_pitch(self, audio, sr) -> List[PitchFrame]:
        """Détecte pitch."""
        # Stub: retourne notes simples
        return [
            PitchFrame(0.0, 440.0, 0.9),
            PitchFrame(1.0, 493.88, 0.85),
        ]
