"""Stub AudioProcessor pour tests Pipeline"""
from pathlib import Path
import numpy as np

class AudioProcessor:
    def __init__(self, target_sr=22050):
        self.target_sr = target_sr
    
    def preprocess(self, file_path: str):
        """Charge et prétraite audio."""
        # Stub: retourne array vide
        return np.zeros(self.target_sr * 5), self.target_sr
