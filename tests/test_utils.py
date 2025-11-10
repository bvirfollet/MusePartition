"""
MusePartition - Utils Tests
Unit tests for the utils module
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import numpy as np

from src.utils import (
    DebugTracer, 
    IntermediateStorage, 
    format_duration,
    format_frequency,
    print_summary_stats
)
from src.types import PitchFrame


class TestDebugTracer:
    """Test suite for DebugTracer class."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Crée un répertoire temporaire pour les tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_init_enabled(self, temp_output_dir):
        """Test initialisation avec traçage activé."""
        tracer = DebugTracer(output_dir=temp_output_dir, enabled=True)
        
        assert tracer.enabled is True
        assert tracer.output_dir.exists()
        assert tracer.log_file.exists()
    
    def test_init_disabled(self, temp_output_dir):
        """Test initialisation avec traçage désactivé."""
        tracer = DebugTracer(output_dir=temp_output_dir, enabled=False)
        
        assert tracer.enabled is False
    
    def test_log_step(self, temp_output_dir):
        """Test enregistrement d'une étape."""
        tracer = DebugTracer(output_dir=temp_output_dir, enabled=True)
        
        metadata = {
            "num_frames": 100,
            "avg_confidence": 0.85,
            "processing_time": 2.3
        }
        
        tracer.log_step("test_step", metadata)
        
        # Vérifier que le fichier JSON existe
        json_files = list(Path(temp_output_dir).glob("*.json"))
        assert len(json_files) == 1
        
        # Vérifier contenu JSON
        import json
        with open(json_files[0], 'r') as f:
            data = json.load(f)
        
        assert "session_id" in data
        assert "steps" in data
        assert len(data["steps"]) == 1
        assert data["steps"][0]["step"] == "test_step"
        assert data["steps"][0]["metadata"] == metadata
    
    def test_log_step_disabled(self, temp_output_dir):
        """Test que log_step ne fait rien quand désactivé."""
        tracer = DebugTracer(output_dir=temp_output_dir, enabled=False)
        
        tracer.log_step("test_step", {"key": "value"})
        
        # Aucun fichier ne devrait être créé
        json_files = list(Path(temp_output_dir).glob("*.json"))
        assert len(json_files) == 0


class TestIntermediateStorage:
    """Test suite for IntermediateStorage class."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Crée un répertoire temporaire pour les tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def storage(self, temp_output_dir):
        """Crée une instance IntermediateStorage."""
        return IntermediateStorage(output_dir=temp_output_dir)
    
    @pytest.fixture
    def sample_audio(self):
        """Génère audio de test."""
        sr = 22050
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)
        return audio, sr
    
    @pytest.fixture
    def sample_pitch_frames(self):
        """Génère pitch frames de test."""
        return [
            PitchFrame(time=0.0, frequency=440.0, confidence=0.9),
            PitchFrame(time=0.1, frequency=442.0, confidence=0.85),
            PitchFrame(time=0.2, frequency=441.0, confidence=0.88)
        ]
    
    def test_save_audio(self, storage, sample_audio, temp_output_dir):
        """Test sauvegarde audio."""
        audio, sr = sample_audio
        
        filepath = storage.save_audio(audio, sr, filename="test_audio.pkl")
        
        assert filepath.exists()
        assert filepath.name == "test_audio.pkl"
    
    def test_load_audio(self, storage, sample_audio):
        """Test chargement audio."""
        audio, sr = sample_audio
        
        # Save
        storage.save_audio(audio, sr, filename="test_audio.pkl")
        
        # Load
        loaded = storage.load_audio(filename="test_audio.pkl")
        
        assert "audio" in loaded
        assert "sample_rate" in loaded
        assert loaded["sample_rate"] == sr
        np.testing.assert_array_almost_equal(loaded["audio"], audio)
    
    def test_save_pitch_data(self, storage, sample_pitch_frames, temp_output_dir):
        """Test sauvegarde pitch data."""
        filepath = storage.save_pitch_data(sample_pitch_frames, filename="test_pitch.json")
        
        assert filepath.exists()
        
        # Vérifier contenu JSON
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert "pitch_frames" in data
        assert "count" in data
        assert data["count"] == 3
        assert len(data["pitch_frames"]) == 3
        assert data["pitch_frames"][0]["frequency"] == 440.0
    
    def test_load_pitch_data(self, storage, sample_pitch_frames):
        """Test chargement pitch data."""
        # Save
        storage.save_pitch_data(sample_pitch_frames, filename="test_pitch.json")
        
        # Load
        loaded = storage.load_pitch_data(filename="test_pitch.json")
        
        assert "pitch_frames" in loaded
        assert loaded["count"] == 3
        assert loaded["pitch_frames"][0]["frequency"] == 440.0
    
    def test_list_saved_files(self, storage, sample_audio, sample_pitch_frames):
        """Test listage des fichiers sauvegardés."""
        audio, sr = sample_audio
        
        # Sauvegarder plusieurs fichiers
        storage.save_audio(audio, sr)
        storage.save_pitch_data(sample_pitch_frames)
        
        # Lister
        files = storage.list_saved_files()
        
        assert len(files) >= 2
        assert any("audio" in str(f) for f in files)
        assert any("pitch" in str(f) for f in files)


class TestUtilityFunctions:
    """Test suite for utility functions."""
    
    def test_format_duration_seconds(self):
        """Test formatage durée < 60s."""
        assert format_duration(15.3) == "15.3s"
        assert format_duration(59.9) == "59.9s"
    
    def test_format_duration_minutes(self):
        """Test formatage durée > 60s."""
        assert format_duration(154.7) == "2m 34s"
        assert format_duration(60.0) == "1m 0s"
        assert format_duration(125.0) == "2m 5s"
    
    def test_format_frequency_a4(self):
        """Test formatage fréquence A4 (440 Hz)."""
        result = format_frequency(440.0)
        assert "440.0 Hz" in result
        assert "A4" in result
    
    def test_format_frequency_c4(self):
        """Test formatage fréquence C4 (~261.63 Hz)."""
        result = format_frequency(261.63)
        assert "261.6 Hz" in result
        assert "C4" in result
    
    def test_format_frequency_invalid(self):
        """Test formatage fréquence invalide."""
        result = format_frequency(0.0)
        assert "invalid" in result
        
        result = format_frequency(-10.0)
        assert "invalid" in result
    
    def test_print_summary_stats_empty(self, capsys):
        """Test affichage stats sur liste vide."""
        print_summary_stats([])
        
        captured = capsys.readouterr()
        assert "No pitch data" in captured.out
    
    def test_print_summary_stats_valid(self, capsys):
        """Test affichage stats sur données valides."""
        pitch_frames = [
            PitchFrame(time=0.0, frequency=440.0, confidence=0.9),
            PitchFrame(time=0.1, frequency=442.0, confidence=0.85),
            PitchFrame(time=0.2, frequency=880.0, confidence=0.88)
        ]
        
        print_summary_stats(pitch_frames)
        
        captured = capsys.readouterr()
        assert "Total frames: 3" in captured.out
        assert "Average confidence" in captured.out
        assert "Frequency range" in captured.out
        assert "Duration" in captured.out


# --- Tests d'intégration ---

class TestIntegration:
    """Tests d'intégration utils avec autres modules."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Crée un répertoire temporaire."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_tracer_and_storage_workflow(self, temp_output_dir):
        """Test workflow complet tracer + storage."""
        tracer = DebugTracer(output_dir=f"{temp_output_dir}/debug", enabled=True)
        storage = IntermediateStorage(output_dir=f"{temp_output_dir}/intermediate")
        
        # Simuler étapes pipeline
        tracer.log_step("start", {"input_file": "test.wav"})
        
        # Créer et sauvegarder audio
        audio = np.random.randn(22050)
        sr = 22050
        storage.save_audio(audio, sr)
        
        tracer.log_step("audio_saved", {"duration": len(audio)/sr})
        
        # Créer et sauvegarder pitch data
        pitch_frames = [
            PitchFrame(time=0.0, frequency=440.0, confidence=0.9)
        ]
        storage.save_pitch_data(pitch_frames)
        
        tracer.log_step("pitch_saved", {"num_frames": len(pitch_frames)})
        
        # Vérifier que fichiers existent
        debug_files = list(Path(f"{temp_output_dir}/debug").glob("*"))
        intermediate_files = storage.list_saved_files()
        
        assert len(debug_files) >= 2  # .log + .json
        assert len(intermediate_files) >= 2  # audio + pitch
