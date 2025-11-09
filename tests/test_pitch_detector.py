"""
MusePartition - Pitch Detector Tests
Unit tests for the PitchDetector module
"""

import pytest
import numpy as np
from src.pitch_detector import PitchDetector
from src.types import PitchFrame # Assurez-vous que PitchFrame est correctement défini

class TestPitchDetector:
    """Test suite for PitchDetector class."""

    # --- Fixture Audio de Test (à réutiliser du module AudioProcessor) ---
    @pytest.fixture
    def sample_audio_mono(self):
        """Génère des données audio mono (1s de La4 à 440 Hz)."""
        sr = 22050
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        # Légère rampe pour éviter les clics au début/fin (bonne pratique)
        envelope = np.clip(t * 5, 0, 1) * np.clip((duration - t) * 5, 0, 1)
        audio = 0.5 * np.sin(2 * np.pi * 440 * t) * envelope
        return audio, sr

    @pytest.fixture
    def sample_audio_stereo(self):
        """Génère des données audio stéréo (non supporté par le module)."""
        sr = 22050
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        left = 0.5 * np.sin(2 * np.pi * 440 * t)
        right = 0.3 * np.sin(2 * np.pi * 880 * t)
        audio = np.array([left, right]).T # Format (samples, channels) ou (channels, samples)
        return audio, sr

    # --- Tests d'initialisation ---

    def test_init_default(self):
        """Test l'initialisation par défaut."""
        detector = PitchDetector()
        assert detector.model_capacity == "full"
        assert detector.step_size == 10

    def test_init_custom(self):
        """Test l'initialisation avec des paramètres personnalisés."""
        detector = PitchDetector(model_capacity="tiny", step_size=20)
        assert detector.model_capacity == "tiny"
        assert detector.step_size == 20

    # --- Tests de détection de pitch ---

    def test_detect_pitch_output_format(self, sample_audio_mono):
        """Test que la sortie a le bon format (Liste de PitchFrame)."""
        audio, sr = sample_audio_mono
        detector = PitchDetector(step_size=10) # 10ms step

        # Le temps de traitement peut être long au premier appel (téléchargement modèle)
        pitch_data = detector.detect_pitch(audio, sr)

        assert isinstance(pitch_data, list)
        assert len(pitch_data) > 0 # Doit retourner des frames
        assert isinstance(pitch_data[0], PitchFrame)
        assert hasattr(pitch_data[0], 'time')
        assert hasattr(pitch_data[0], 'frequency')
        assert hasattr(pitch_data[0], 'confidence')

    def test_detect_pitch_accuracy_440hz(self, sample_audio_mono):
        """Test la précision de la détection sur un simple signal sinusoïdal."""
        audio, sr = sample_audio_mono
        # Utiliser un modèle plus rapide pour les tests unitaires
        detector = PitchDetector(model_capacity="tiny", step_size=10)
        pitch_data = detector.detect_pitch(audio, sr)

        # Filtrer les fréquences détectées avec une haute confiance
        confident_freqs = [
            frame.frequency
            for frame in pitch_data
            if frame.confidence > 0.8 # Seuil de confiance élevé
        ]

        # S'assurer qu'au moins 50% des frames ont une haute confiance
        assert len(confident_freqs) > len(pitch_data) / 2

        # La fréquence moyenne détectée doit être très proche de 440 Hz
        avg_freq = np.mean(confident_freqs)

        # Tolérance de 1 Hz (très conservateur)
        assert abs(avg_freq - 440.0) < 1.0

    def test_detect_pitch_non_mono_raises_error(self, sample_audio_stereo):
        """Test que le traitement d'un signal stéréo lève une erreur."""
        audio_stereo, sr = sample_audio_stereo
        detector = PitchDetector()

        # CREPE s'attend à un audio 1D
        with pytest.raises(ValueError, match="L'entrée audio doit être mono"):
            # Nous devons adapter la fixture stéréo pour qu'elle ait ndim=2 (2 canaux)
            # En général, librosa charge en (channels, samples) ou (samples, channels)
            # Si audio_stereo est de forme (N, 2), cela devrait lever l'erreur.
            # Pour s'assurer que le test utilise un tableau 2D:
            audio_2d = audio_stereo if audio_stereo.ndim == 2 else audio_stereo.T
            detector.detect_pitch(audio_2d, sr)