"""
MusePartition - Audio Processing Module
Handles audio file loading, normalization, and preprocessing
"""

from typing import Tuple
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path

from src.types import AudioLoadError


class AudioProcessor:
    """
    Processes audio files for transcription.
    
    Handles loading, normalization, and conversion to mono.
    Supports WAV, MP3, FLAC, and other formats via librosa.
    """
    
    def __init__(self, target_sr: int = 22050):
        """
        Initialize AudioProcessor.
        
        Args:
            target_sr: Target sample rate in Hz (default: 22050)
                      22050 Hz is sufficient for most musical instruments
                      and reduces computational load vs 44100 Hz
        """
        self.target_sr = target_sr
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load an audio file and return audio data with sample rate.
        
        Args:
            file_path: Path to audio file (WAV, MP3, FLAC, etc.)
        
        Returns:
            Tuple of (audio_data, sample_rate):
                - audio_data: numpy array of audio samples
                - sample_rate: sample rate in Hz
        
        Raises:
            AudioLoadError: If file cannot be loaded or doesn't exist
        
        Example:
            >>> processor = AudioProcessor()
            >>> audio, sr = processor.load_audio("recording.wav")
            >>> print(f"Loaded {len(audio)} samples at {sr} Hz")
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise AudioLoadError(f"File not found: {file_path}")
        
        try:
            # Load audio file with librosa
            # sr=None preserves original sample rate
            audio, sr = librosa.load(str(file_path), sr=None, mono=False)
            
            # If already mono, ensure 1D array
            if audio.ndim == 1:
                return audio, sr
            
            # If stereo/multi-channel, return as-is for now
            # User can call to_mono() if needed
            return audio, sr
            
        except Exception as e:
            raise AudioLoadError(f"Failed to load audio file: {e}")
    
    def normalize(
        self, 
        audio: np.ndarray, 
        method: str = "peak",
        target_level: float = 1.0
    ) -> np.ndarray:
        """
        Normalize audio amplitude.
        
        Args:
            audio: Audio data as numpy array
            method: Normalization method:
                   - "peak": Normalize to peak amplitude (default)
                   - "rms": Normalize to target RMS level
            target_level: Target level for normalization (default: 1.0)
        
        Returns:
            Normalized audio array
        
        Raises:
            ValueError: If method is invalid or audio is silent
        
        Example:
            >>> processor = AudioProcessor()
            >>> audio, sr = processor.load_audio("recording.wav")
            >>> normalized = processor.normalize(audio, method="peak")
        """
        if method not in ["peak", "rms"]:
            raise ValueError(f"Invalid normalization method: {method}. Use 'peak' or 'rms'")
        
        # Handle multi-channel audio
        if audio.ndim > 1:
            # Normalize each channel independently
            return np.array([
                self.normalize(channel, method, target_level) 
                for channel in audio
            ])
        
        # Check for silence
        if np.max(np.abs(audio)) < 1e-10:
            raise ValueError("Cannot normalize silent audio")
        
        if method == "peak":
            # Peak normalization: scale so max absolute value = target_level
            peak = np.max(np.abs(audio))
            return audio * (target_level / peak)
        
        elif method == "rms":
            # RMS normalization: scale so RMS = target_level
            rms = np.sqrt(np.mean(audio ** 2))
            if rms < 1e-10:
                raise ValueError("Cannot normalize audio with near-zero RMS")
            return audio * (target_level / rms)
    
    def to_mono(self, audio: np.ndarray) -> np.ndarray:
        """
        Convert stereo or multi-channel audio to mono.
        
        Args:
            audio: Audio data (1D for mono, 2D for stereo/multi-channel)
        
        Returns:
            Mono audio as 1D numpy array
        
        Example:
            >>> processor = AudioProcessor()
            >>> audio, sr = processor.load_audio("stereo.wav")
            >>> mono = processor.to_mono(audio)
            >>> print(mono.shape)  # (n_samples,)
        """
        if audio.ndim == 1:
            # Already mono
            return audio
        
        elif audio.ndim == 2:
            # Average across channels
            return np.mean(audio, axis=0)
        
        else:
            raise ValueError(f"Unexpected audio shape: {audio.shape}")
    
    def preprocess(
        self, 
        file_path: str,
        normalize: bool = True,
        to_mono: bool = True
    ) -> Tuple[np.ndarray, int]:
        """
        Complete preprocessing pipeline: load, normalize, convert to mono.
        
        This is a convenience method that combines load_audio, normalize,
        and to_mono in one call.
        
        Args:
            file_path: Path to audio file
            normalize: Whether to normalize audio (default: True)
            to_mono: Whether to convert to mono (default: True)
        
        Returns:
            Tuple of (processed_audio, sample_rate)
        
        Example:
            >>> processor = AudioProcessor(target_sr=22050)
            >>> audio, sr = processor.preprocess("recording.wav")
            >>> # audio is now mono, normalized, at 22050 Hz
        """
        # Load audio
        audio, sr = self.load_audio(file_path)
        
        # Resample if needed
        if sr != self.target_sr:
            if audio.ndim == 1:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.target_sr)
            else:
                # Resample each channel
                audio = np.array([
                    librosa.resample(channel, orig_sr=sr, target_sr=self.target_sr)
                    for channel in audio
                ])
            sr = self.target_sr
        
        # Convert to mono if requested
        if to_mono and audio.ndim > 1:
            audio = self.to_mono(audio)
        
        # Normalize if requested
        if normalize:
            audio = self.normalize(audio, method="peak")
        
        return audio, sr
    
    def save_audio(
        self,
        audio: np.ndarray,
        output_path: str,
        sample_rate: int = None
    ) -> None:
        """
        Save audio to file.
        
        Args:
            audio: Audio data to save
            output_path: Output file path
            sample_rate: Sample rate (uses target_sr if None)
        
        Example:
            >>> processor = AudioProcessor()
            >>> audio, sr = processor.load_audio("input.wav")
            >>> processed = processor.normalize(audio)
            >>> processor.save_audio(processed, "output.wav", sr)
        """
        if sample_rate is None:
            sample_rate = self.target_sr
        
        sf.write(output_path, audio, sample_rate)
