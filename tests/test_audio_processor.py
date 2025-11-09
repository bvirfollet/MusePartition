"""
MusePartition - Audio Processor Tests
Unit tests for the AudioProcessor module
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import soundfile as sf

from src.audio_processor import AudioProcessor
from src.types import AudioLoadError


class TestAudioProcessor:
    """Test suite for AudioProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create an AudioProcessor instance for testing."""
        return AudioProcessor(target_sr=22050)
    
    @pytest.fixture
    def sample_audio_mono(self):
        """Generate sample mono audio data."""
        # 1 second of 440 Hz sine wave (A4)
        sr = 22050
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)
        return audio, sr
    
    @pytest.fixture
    def sample_audio_stereo(self):
        """Generate sample stereo audio data."""
        # 1 second of stereo audio (different freqs in each channel)
        sr = 22050
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration))
        left = 0.5 * np.sin(2 * np.pi * 440 * t)
        right = 0.3 * np.sin(2 * np.pi * 880 * t)
        audio = np.array([left, right])
        return audio, sr
    
    @pytest.fixture
    def temp_wav_file(self, sample_audio_mono):
        """Create a temporary WAV file."""
        audio, sr = sample_audio_mono
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            sf.write(f.name, audio, sr)
            yield f.name
        # Cleanup
        Path(f.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def temp_stereo_wav_file(self, sample_audio_stereo):
        """Create a temporary stereo WAV file."""
        audio, sr = sample_audio_stereo
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            # Transpose for soundfile (samples x channels)
            sf.write(f.name, audio.T, sr)
            yield f.name
        # Cleanup
        Path(f.name).unlink(missing_ok=True)
    
    # ===== Constructor Tests =====
    
    def test_init_default(self):
        """Test default initialization."""
        processor = AudioProcessor()
        assert processor.target_sr == 22050
    
    def test_init_custom_sr(self):
        """Test initialization with custom sample rate."""
        processor = AudioProcessor(target_sr=44100)
        assert processor.target_sr == 44100
    
    # ===== load_audio Tests =====
    
    def test_load_audio_success(self, processor, temp_wav_file):
        """Test successful audio loading."""
        audio, sr = processor.load_audio(temp_wav_file)
        
        assert isinstance(audio, np.ndarray)
        assert isinstance(sr, int)
        assert len(audio) > 0
        assert sr == 22050
    
    def test_load_audio_file_not_found(self, processor):
        """Test loading non-existent file raises error."""
        with pytest.raises(AudioLoadError, match="File not found"):
            processor.load_audio("nonexistent_file.wav")
    
    def test_load_audio_invalid_file(self, processor):
        """Test loading invalid file raises error."""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(b"not an audio file")
            f.flush()
            
            with pytest.raises(AudioLoadError, match="Failed to load"):
                processor.load_audio(f.name)
            
            Path(f.name).unlink(missing_ok=True)
    
    def test_load_audio_preserves_stereo(self, processor, temp_stereo_wav_file):
        """Test that stereo audio is loaded as 2D array."""
        audio, sr = processor.load_audio(temp_stereo_wav_file)
        
        assert audio.ndim == 2
        assert audio.shape[0] == 2  # 2 channels
    
    # ===== normalize Tests =====
    
    def test_normalize_peak_default(self, processor, sample_audio_mono):
        """Test peak normalization with default target level."""
        audio, _ = sample_audio_mono
        normalized = processor.normalize(audio)
        
        # Peak should be at 1.0
        assert np.isclose(np.max(np.abs(normalized)), 1.0, atol=1e-6)
    
    def test_normalize_peak_custom_level(self, processor, sample_audio_mono):
        """Test peak normalization with custom target level."""
        audio, _ = sample_audio_mono
        normalized = processor.normalize(audio, target_level=0.5)
        
        # Peak should be at 0.5
        assert np.isclose(np.max(np.abs(normalized)), 0.5, atol=1e-6)
    
    def test_normalize_rms(self, processor, sample_audio_mono):
        """Test RMS normalization."""
        audio, _ = sample_audio_mono
        target_rms = 0.1
        normalized = processor.normalize(audio, method="rms", target_level=target_rms)
        
        # RMS should be close to target
        actual_rms = np.sqrt(np.mean(normalized ** 2))
        assert np.isclose(actual_rms, target_rms, atol=1e-6)
    
    def test_normalize_invalid_method(self, processor, sample_audio_mono):
        """Test that invalid normalization method raises error."""
        audio, _ = sample_audio_mono
        
        with pytest.raises(ValueError, match="Invalid normalization method"):
            processor.normalize(audio, method="invalid")
    
    def test_normalize_silent_audio(self, processor):
        """Test that normalizing silent audio raises error."""
        silent = np.zeros(1000)
        
        with pytest.raises(ValueError, match="Cannot normalize silent audio"):
            processor.normalize(silent)
    
    def test_normalize_stereo(self, processor, sample_audio_stereo):
        """Test normalizing stereo audio."""
        audio, _ = sample_audio_stereo
        normalized = processor.normalize(audio)
        
        # Each channel should be normalized independently
        assert normalized.ndim == 2
        assert normalized.shape == audio.shape
        
        # Each channel's peak should be close to 1.0
        for channel in normalized:
            assert np.max(np.abs(channel)) <= 1.0 + 1e-6
    
    # ===== to_mono Tests =====
    
    def test_to_mono_already_mono(self, processor, sample_audio_mono):
        """Test converting already mono audio returns same data."""
        audio, _ = sample_audio_mono
        mono = processor.to_mono(audio)
        
        assert mono.ndim == 1
        assert len(mono) == len(audio)
        np.testing.assert_array_equal(mono, audio)
    
    def test_to_mono_from_stereo(self, processor, sample_audio_stereo):
        """Test converting stereo to mono averages channels."""
        audio, _ = sample_audio_stereo
        mono = processor.to_mono(audio)
        
        assert mono.ndim == 1
        assert len(mono) == audio.shape[1]
        
        # Should be average of channels
        expected = np.mean(audio, axis=0)
        np.testing.assert_array_almost_equal(mono, expected)
    
    def test_to_mono_invalid_shape(self, processor):
        """Test that 3D+ audio raises error."""
        audio_3d = np.zeros((2, 3, 1000))
        
        with pytest.raises(ValueError, match="Unexpected audio shape"):
            processor.to_mono(audio_3d)
    
    # ===== preprocess Tests =====
    
    def test_preprocess_full_pipeline(self, processor, temp_wav_file):
        """Test complete preprocessing pipeline."""
        audio, sr = processor.preprocess(temp_wav_file)
        
        # Should be mono
        assert audio.ndim == 1
        
        # Should be normalized (peak close to 1.0)
        assert np.max(np.abs(audio)) <= 1.0 + 1e-6
        
        # Should be at target sample rate
        assert sr == processor.target_sr
    
    def test_preprocess_no_normalize(self, processor, temp_wav_file):
        """Test preprocessing without normalization."""
        audio, sr = processor.preprocess(temp_wav_file, normalize=False)
        
        # Peak might not be at 1.0
        assert audio.ndim == 1
        assert sr == processor.target_sr
    
    def test_preprocess_no_mono(self, processor, temp_stereo_wav_file):
        """Test preprocessing without converting to mono."""
        audio, sr = processor.preprocess(
            temp_stereo_wav_file, 
            to_mono=False
        )
        
        # Should still be stereo
        assert audio.ndim == 2
        assert audio.shape[0] == 2
    
    def test_preprocess_resample(self, sample_audio_mono):
        """Test that resampling works correctly."""
        # Create processor with different target SR
        processor = AudioProcessor(target_sr=16000)
        audio, sr = sample_audio_mono
        
        # Create temp file with original SR
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            sf.write(f.name, audio, sr)
            
            # Preprocess should resample
            processed, processed_sr = processor.preprocess(f.name)
            
            assert processed_sr == 16000
            assert len(processed) < len(audio)  # Downsampled
            
            Path(f.name).unlink(missing_ok=True)
    
    # ===== save_audio Tests =====
    
    def test_save_audio(self, processor, sample_audio_mono):
        """Test saving audio to file."""
        audio, sr = sample_audio_mono
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            output_path = f.name
        
        try:
            processor.save_audio(audio, output_path, sr)
            
            # Verify file exists and can be loaded
            assert Path(output_path).exists()
            loaded, loaded_sr = sf.read(output_path)
            
            assert loaded_sr == sr
            np.testing.assert_array_almost_equal(loaded, audio, decimal=4)
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_save_audio_default_sr(self, processor, sample_audio_mono):
        """Test saving audio with default sample rate."""
        audio, _ = sample_audio_mono
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            output_path = f.name
        
        try:
            processor.save_audio(audio, output_path)
            
            _, loaded_sr = sf.read(output_path)
            assert loaded_sr == processor.target_sr
        
        finally:
            Path(output_path).unlink(missing_ok=True)


# ===== Integration Tests =====

class TestAudioProcessorIntegration:
    """Integration tests for AudioProcessor."""
    
    def test_full_workflow(self):
        """Test complete workflow: load -> process -> save."""
        processor = AudioProcessor(target_sr=22050)
        
        # Create sample audio
        sr = 44100
        duration = 0.5
        t = np.linspace(0, duration, int(sr * duration))
        audio = 0.7 * np.sin(2 * np.pi * 440 * t)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            input_path = f.name
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            output_path = f.name
        
        try:
            # Save original
            sf.write(input_path, audio, sr)
            
            # Process
            processed, processed_sr = processor.preprocess(input_path)
            
            # Save processed
            processor.save_audio(processed, output_path, processed_sr)
            
            # Verify output
            assert Path(output_path).exists()
            loaded, loaded_sr = sf.read(output_path)
            
            assert loaded_sr == 22050
            assert loaded.ndim == 1
            assert np.max(np.abs(loaded)) <= 1.0 + 1e-6
        
        finally:
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)
