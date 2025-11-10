"""
Tests pour TranscriptionPipeline
Orchestration complète audio → partition
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import json

from src.transcription_pipeline import TranscriptionPipeline, load_config
from src.types import TranscriptionResult


@pytest.fixture
def temp_output_dir():
    """Crée répertoire temporaire."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_audio_file(temp_output_dir):
    """Crée fichier audio stub."""
    audio_path = Path(temp_output_dir) / "test_audio.wav"
    audio_path.touch()
    return str(audio_path)


@pytest.fixture
def sample_config():
    """Config exemple."""
    return {
        "quantization": {
            "bpm": 120.0,
            "time_signature": "4/4"
        },
        "score_generation": {
            "title": "Test Song",
            "composer": "Test Composer"
        }
    }


class TestTranscriptionPipelineInit:
    """Tests d'initialisation."""
    
    def test_init_default(self):
        """Test init avec config par défaut."""
        pipeline = TranscriptionPipeline()
        
        assert pipeline.config is not None
        assert "audio" in pipeline.config
        assert "pitch_detection" in pipeline.config
        assert pipeline.config["audio"]["target_sr"] == 22050
    
    def test_init_with_config(self, sample_config):
        """Test init avec config personnalisée."""
        pipeline = TranscriptionPipeline(sample_config)
        
        assert pipeline.config["quantization"]["bpm"] == 120.0
        assert pipeline.config["score_generation"]["title"] == "Test Song"
    
    def test_init_modules_created(self):
        """Test que tous les modules sont initialisés."""
        pipeline = TranscriptionPipeline()
        
        assert pipeline.audio_processor is not None
        assert pipeline.pitch_detector is not None
        assert pipeline.note_segmenter is not None
        assert pipeline.quantizer is not None
        assert pipeline.score_generator is not None
        assert pipeline.tracer is not None


class TestConfigValidation:
    """Tests validation config."""
    
    def test_validate_invalid_format(self):
        """Test formats de sortie invalides."""
        config = {
            "output": {
                "formats": ["musicxml", "invalid_format"]
            }
        }
        
        with pytest.raises(ValueError, match="Formats invalides"):
            TranscriptionPipeline(config)
    
    def test_validate_missing_section(self):
        """Test section manquante (via config vide)."""
        # Config complètement vide ne devrait pas crash car merge avec default
        pipeline = TranscriptionPipeline({})
        assert pipeline.config is not None


class TestTranscribe:
    """Tests de la méthode transcribe."""
    
    def test_transcribe_file_not_found(self, temp_output_dir):
        """Test avec fichier inexistant."""
        pipeline = TranscriptionPipeline()
        
        with pytest.raises(FileNotFoundError):
            pipeline.transcribe("nonexistent.wav", temp_output_dir)
    
    def test_transcribe_success(self, temp_audio_file, temp_output_dir):
        """Test transcription complète."""
        pipeline = TranscriptionPipeline()
        
        result = pipeline.transcribe(temp_audio_file, temp_output_dir)
        
        # Vérifier type retour
        assert isinstance(result, TranscriptionResult)
        
        # Vérifier champs
        assert result.bpm > 0
        assert result.num_notes > 0
        assert result.processing_time > 0
        assert result.musicxml_path
        assert result.midi_path
    
    def test_transcribe_with_fixed_bpm(self, temp_audio_file, temp_output_dir):
        """Test avec BPM fixe."""
        config = {"quantization": {"bpm": 130.0}}
        pipeline = TranscriptionPipeline(config)
        
        result = pipeline.transcribe(temp_audio_file, temp_output_dir)
        
        # BPM devrait être celui fourni
        assert result.bpm == 130.0
    
    def test_transcribe_creates_output_dir(self, temp_audio_file):
        """Test création automatique répertoire sortie."""
        output_dir = Path(tempfile.gettempdir()) / "test_output_new"
        
        try:
            pipeline = TranscriptionPipeline()
            result = pipeline.transcribe(temp_audio_file, str(output_dir))
            
            assert output_dir.exists()
        finally:
            if output_dir.exists():
                shutil.rmtree(output_dir)


class TestFromJsonFile:
    """Tests chargement depuis JSON."""
    
    def test_from_json_file(self, temp_output_dir):
        """Test chargement config JSON."""
        config_data = {
            "quantization": {"bpm": 140.0},
            "score_generation": {"title": "JSON Test"}
        }
        
        config_path = Path(temp_output_dir) / "test_config.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f)
        
        pipeline = TranscriptionPipeline.from_json_file(str(config_path))
        
        assert pipeline.config["quantization"]["bpm"] == 140.0
        assert pipeline.config["score_generation"]["title"] == "JSON Test"


class TestLoadConfig:
    """Tests fonction load_config."""
    
    def test_load_config(self, temp_output_dir):
        """Test chargement config."""
        config_data = {"test": "value"}
        config_path = Path(temp_output_dir) / "config.json"
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f)
        
        loaded = load_config(str(config_path))
        assert loaded["test"] == "value"


class TestIntegration:
    """Tests d'intégration."""
    
    def test_full_pipeline_with_custom_config(self, temp_audio_file, temp_output_dir):
        """Test pipeline complet avec config personnalisée."""
        config = {
            "quantization": {
                "bpm": 125.0,
                "time_signature": "3/4",
                "quantization_grid": "1/8"
            },
            "score_generation": {
                "title": "Integration Test",
                "composer": "Test Suite",
                "key_signature": "D",
                "clef": "bass"
            },
            "output": {
                "base_filename": "integration_test"
            },
            "debug": {
                "enabled": True
            }
        }
        
        pipeline = TranscriptionPipeline(config)
        result = pipeline.transcribe(temp_audio_file, temp_output_dir)
        
        # Vérifications
        assert result.bpm == 125.0
        assert result.num_notes > 0
        
        # Vérifier fichiers créés
        output_path = Path(temp_output_dir)
        assert (output_path / "integration_test.musicxml").exists()
        assert (output_path / "integration_test.mid").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
