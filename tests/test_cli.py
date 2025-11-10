"""
Tests pour CLI
Interface ligne de commande
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import json
import sys
from unittest.mock import patch, MagicMock

from src.cli import create_parser, build_config_from_args, cmd_transcribe


@pytest.fixture
def temp_output_dir():
    """Crée répertoire temporaire."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_audio_file(temp_output_dir):
    """Crée fichier audio stub."""
    audio_path = Path(temp_output_dir) / "test.wav"
    audio_path.touch()
    return str(audio_path)


class TestParser:
    """Tests du parser d'arguments."""
    
    def test_create_parser(self):
        """Test création parser."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "musepartition"
    
    def test_parse_basic_transcribe(self):
        """Test parsing commande basique."""
        parser = create_parser()
        args = parser.parse_args(['transcribe', 'input.wav'])
        
        assert args.command == 'transcribe'
        assert args.input_file == 'input.wav'
        assert args.output == 'output'  # default
    
    def test_parse_with_output(self):
        """Test parsing avec output."""
        parser = create_parser()
        args = parser.parse_args(['transcribe', 'input.wav', '-o', 'results/'])
        
        assert args.output == 'results/'
    
    def test_parse_with_config(self):
        """Test parsing avec config."""
        parser = create_parser()
        args = parser.parse_args(['transcribe', 'input.wav', '--config', 'my_config.json'])
        
        assert args.config == 'my_config.json'
    
    def test_parse_with_bpm(self):
        """Test parsing avec BPM."""
        parser = create_parser()
        args = parser.parse_args(['transcribe', 'input.wav', '--bpm', '120'])
        
        assert args.bpm == 120.0
    
    def test_parse_with_time_signature(self):
        """Test parsing avec signature temporelle."""
        parser = create_parser()
        args = parser.parse_args(['transcribe', 'input.wav', '--time-signature', '3/4'])
        
        assert args.time_signature == '3/4'
    
    def test_parse_with_all_overrides(self):
        """Test parsing avec tous les overrides."""
        parser = create_parser()
        args = parser.parse_args([
            'transcribe', 'input.wav',
            '--bpm', '130',
            '--time-signature', '6/8',
            '--quantization-grid', '1/8',
            '--feel', 'triplet',
            '--key', 'D',
            '--clef', 'bass',
            '--title', 'My Song',
            '--composer', 'John Doe',
            '--model', 'small',
            '--filename', 'myscore',
            '-v',
            '--save-intermediate'
        ])
        
        assert args.bpm == 130.0
        assert args.time_signature == '6/8'
        assert args.quantization_grid == '1/8'
        assert args.feel == 'triplet'
        assert args.key == 'D'
        assert args.clef == 'bass'
        assert args.title == 'My Song'
        assert args.composer == 'John Doe'
        assert args.model == 'small'
        assert args.filename == 'myscore'
        assert args.verbose is True
        assert args.save_intermediate is True


class TestBuildConfig:
    """Tests construction config depuis args."""
    
    def test_build_config_empty(self):
        """Test config vide."""
        parser = create_parser()
        args = parser.parse_args(['transcribe', 'input.wav'])
        
        config = build_config_from_args(args)
        
        # Devrait avoir debug au minimum
        assert 'debug' in config
        assert config['debug']['enabled'] is False
    
    def test_build_config_with_bpm(self):
        """Test config avec BPM."""
        parser = create_parser()
        args = parser.parse_args(['transcribe', 'input.wav', '--bpm', '125'])
        
        config = build_config_from_args(args)
        
        assert config['quantization']['bpm'] == 125.0
    
    def test_build_config_with_time_signature(self):
        """Test config avec signature."""
        parser = create_parser()
        args = parser.parse_args(['transcribe', 'input.wav', '--time-signature', '3/4'])
        
        config = build_config_from_args(args)
        
        assert config['quantization']['time_signature'] == '3/4'
        assert config['score_generation']['time_signature'] == '3/4'
    
    def test_build_config_from_json_file(self, temp_output_dir):
        """Test config depuis JSON + overrides."""
        # Créer JSON
        json_config = {
            "quantization": {"bpm": 100.0},
            "score_generation": {"title": "JSON Title"}
        }
        config_path = Path(temp_output_dir) / "test.json"
        with open(config_path, 'w') as f:
            json.dump(json_config, f)
        
        # Parser args avec override
        parser = create_parser()
        args = parser.parse_args([
            'transcribe', 'input.wav',
            '--config', str(config_path),
            '--bpm', '120'  # Override JSON
        ])
        
        config = build_config_from_args(args)
        
        # BPM override devrait gagner
        assert config['quantization']['bpm'] == 120.0
        # Titre JSON devrait rester
        assert config['score_generation']['title'] == "JSON Title"
    
    def test_build_config_verbose(self):
        """Test mode verbose."""
        parser = create_parser()
        args = parser.parse_args(['transcribe', 'input.wav', '-v'])
        
        config = build_config_from_args(args)
        
        assert config['debug']['enabled'] is True


class TestCmdTranscribe:
    """Tests commande transcribe."""
    
    def test_cmd_transcribe_file_not_found(self, capsys):
        """Test fichier inexistant."""
        parser = create_parser()
        args = parser.parse_args(['transcribe', 'nonexistent.wav'])
        
        exit_code = cmd_transcribe(args)
        
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "introuvable" in captured.out or "Erreur" in captured.out
    
    @patch('src.cli.TranscriptionPipeline')
    def test_cmd_transcribe_success(self, mock_pipeline_class, temp_audio_file, temp_output_dir):
        """Test transcription réussie."""
        # Mock pipeline
        mock_pipeline = MagicMock()
        mock_result = MagicMock()
        mock_result.musicxml_path = f"{temp_output_dir}/score.musicxml"
        mock_result.midi_path = f"{temp_output_dir}/score.mid"
        mock_result.pdf_path = None
        mock_result.bpm = 120.0
        mock_result.num_notes = 42
        mock_result.processing_time = 5.5
        
        mock_pipeline.transcribe.return_value = mock_result
        mock_pipeline_class.return_value = mock_pipeline
        
        # Créer args
        parser = create_parser()
        args = parser.parse_args(['transcribe', temp_audio_file, '-o', temp_output_dir])
        
        # Exécuter
        exit_code = cmd_transcribe(args)
        
        assert exit_code == 0
        mock_pipeline.transcribe.assert_called_once()
    
    @patch('src.cli.TranscriptionPipeline')
    def test_cmd_transcribe_with_error(self, mock_pipeline_class, temp_audio_file, capsys):
        """Test avec erreur durant transcription."""
        # Mock pipeline qui lance exception
        mock_pipeline = MagicMock()
        mock_pipeline.transcribe.side_effect = RuntimeError("Test error")
        mock_pipeline_class.return_value = mock_pipeline
        
        parser = create_parser()
        args = parser.parse_args(['transcribe', temp_audio_file])
        
        exit_code = cmd_transcribe(args)
        
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Erreur" in captured.out


class TestIntegrationCLI:
    """Tests d'intégration CLI."""
    
    def test_full_cli_workflow(self, temp_audio_file, temp_output_dir):
        """Test workflow CLI complet avec stubs."""
        parser = create_parser()
        args = parser.parse_args([
            'transcribe', temp_audio_file,
            '-o', temp_output_dir,
            '--bpm', '120',
            '--title', 'CLI Test',
            '--filename', 'cli_output'
        ])
        
        # Construire config
        config = build_config_from_args(args)
        
        assert config['quantization']['bpm'] == 120.0
        assert config['score_generation']['title'] == 'CLI Test'
        assert config['output']['base_filename'] == 'cli_output'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
