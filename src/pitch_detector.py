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

    def __init__(
        self, 
        model_capacity: str = "medium", 
        step_size: int = 10, 
        confidence_threshold: float = 0.5,
        verbose: int = 0
    ):
        """
        Initialise le PitchDetector.

        Args:
            model_capacity: Capacité du modèle CREPE. Options:
                - "tiny": Très rapide, moins précis (~10x plus rapide que full)
                - "small": Rapide, précision correcte
                - "medium": Équilibré, recommandé pour production (défaut)
                - "large": Précis, plus lent
                - "full": Maximum précision, très lent (~10x medium)
            step_size: Taille de l'étape en millisecondes entre détections (défaut: 10ms).
                Plus petit = plus précis mais plus lent.
            confidence_threshold: Seuil de confiance minimum [0, 1] (défaut: 0.5).
                Les détections avec confidence < seuil sont filtrées.
                Recommandé: 0.5 (équilibré), 0.8 (stricte), 0.3 (permissive)
            verbose: Niveau de verbosité CREPE (0=silencieux, 1=info, 2=debug).
        
        Note:
            Le modèle CREPE est chargé lors du premier appel à detect_pitch(),
            pas lors de l'initialisation. Premier appel peut prendre 10-30s.
        
        Example:
            >>> # Configuration recommandée production
            >>> detector = PitchDetector(model_capacity="medium", confidence_threshold=0.5)
            >>> 
            >>> # Configuration tests rapides
            >>> detector = PitchDetector(model_capacity="tiny", step_size=20)
        """
        self.model_capacity = model_capacity
        self.step_size = step_size
        self.confidence_threshold = confidence_threshold
        self.verbose = verbose
        # Note: CREPE charge le modèle au premier appel, pas dans __init__.

    def detect_pitch(self, audio: np.ndarray, sr: int) -> List[PitchFrame]:
        """
        Détecte la fréquence fondamentale (F0) du signal audio.

        Args:
            audio: Signal audio mono normalisé (1D numpy array).
                Recommandé: amplitude dans [-1, 1], sample rate 22050 ou 44100 Hz.
            sr: Sample rate (taux d'échantillonnage) en Hz.

        Returns:
            Liste de PitchFrame triée chronologiquement.
            Seules les détections avec confidence >= confidence_threshold sont incluses.
            Chaque PitchFrame contient:
                - time (float): Timestamp en secondes
                - frequency (float): Fréquence en Hz
                - confidence (float): Confiance de la détection [0, 1]

        Raises:
            ValueError: Si l'audio n'est pas mono (ndim != 1).

        Example:
            >>> from src.audio_processor import AudioProcessor
            >>> processor = AudioProcessor(target_sr=22050)
            >>> audio, sr = processor.preprocess("flute.wav")
            >>> 
            >>> detector = PitchDetector()
            >>> pitch_data = detector.detect_pitch(audio, sr)
            >>> 
            >>> print(f"Detected {len(pitch_data)} pitch frames")
            >>> avg_freq = sum(p.frequency for p in pitch_data) / len(pitch_data)
            >>> print(f"Average frequency: {avg_freq:.2f} Hz")
        
        Note:
            - Premier appel télécharge le modèle CREPE (~10-100MB selon capacité)
            - Les frames avec confidence < threshold sont automatiquement filtrées
            - Pour audio silencieux, peut retourner liste vide
        """
        # CREPE s'attend à un tableau NumPy 1D (mono)
        if audio.ndim > 1:
            raise ValueError("L'entrée audio doit être mono (1D).")

        # 1. Exécution de CREPE
        time, frequency, confidence, activation = crepe.predict(
            audio,
            sr,
            model_capacity=self.model_capacity,
            step_size=self.step_size,
            verbose=self.verbose
        )

        # 2. Conversion des résultats en liste de PitchFrame avec filtrage
        pitch_frames = []
        for t, f, c in zip(time, frequency, confidence):
            # Filtrer par seuil de confiance
            if c >= self.confidence_threshold:
                pitch_frames.append(
                    PitchFrame(
                        time=float(t.item()), 
                        frequency=float(f.item()), 
                        confidence=float(c.item())
                    )
                )

        return pitch_frames
