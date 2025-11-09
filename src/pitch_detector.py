import numpy as np
from typing import List, Tuple, Optional

# Import de la librairie CREPE
import crepe
# Import du type de données PitchFrame (à définir dans src/types.py)
from src.types import PitchFrame


class PitchDetector:
    """
    Module pour la détection de la fréquence fondamentale (pitch)
    en utilisant l'algorithme CREPE.
    """

    def __init__(self, model_capacity: str = "full", step_size: int = 10, verbose: int = 0):
        """
        Initialise le PitchDetector.

        Args:
            model_capacity (str): Capacité du modèle CREPE (tiny, small, medium, large, full).
                                  "full" est le plus précis mais le plus lent.
            step_size (int): La taille de l'étape en millisecondes entre chaque détection de pitch.
            verbose (int): Niveau de verbosité pour CREPE.
        """
        self.model_capacity = model_capacity
        self.step_size = step_size
        self.verbose = verbose
        # Note: CREPE charge le modèle au premier appel, pas dans __init__.

    def detect_pitch(self, audio: np.ndarray, sr: int) -> List[PitchFrame]:
        """
        Détecte la fréquence fondamentale (F0) du signal audio.

        Args:
            audio (np.ndarray): Le signal audio (mono, normalisé) sous forme de tableau NumPy.
            sr (int): Le taux d'échantillonnage de l'audio.

        Returns:
            List[PitchFrame]: Liste de PitchFrame = (time, frequency, confidence).
        """
        # CREPE s'attend à un tableau NumPy 1D (mono)
        if audio.ndim > 1:
            raise ValueError("L'entrée audio doit être mono (1D).")

        # 1. Exécution de CREPE
        time, frequency, confidence, activation = crepe.predict(
            audio,
            sr,
            model_capacity=self.model_capacity,  # <--- Corrigé : model_capacity est maintenant nommé
            step_size=self.step_size,  # <--- Corrigé : step_size est maintenant nommé
            verbose=self.verbose
        )

        # 2. Conversion des résultats en liste de PitchFrame
        pitch_frames = []
        for t, f, c in zip(time, frequency, confidence):
            pitch_frames.append(PitchFrame(time=t.item(), frequency=f.item(), confidence=c.item()))

        return pitch_frames
