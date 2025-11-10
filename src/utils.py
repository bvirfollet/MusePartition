"""
MusePartition - Utilities Module
Fonctions utilitaires pour traçage, logging et stockage de résultats intermédiaires
"""

import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

# Configuration du logger
logger = logging.getLogger("musepartition")


class DebugTracer:
    """
    Traçage et logging structuré pour le pipeline de transcription.
    
    Permet de sauvegarder les résultats intermédiaires à chaque étape
    pour faciliter le debug et l'analyse.
    """
    
    def __init__(self, output_dir: str = "output/debug", enabled: bool = True):
        """
        Initialise le tracer de debug.
        
        Args:
            output_dir: Répertoire pour sauvegarder les traces (défaut: output/debug)
            enabled: Activer/désactiver le traçage (défaut: True)
        
        Example:
            >>> tracer = DebugTracer(output_dir="output/debug", enabled=True)
            >>> tracer.log_step("audio_loaded", {"duration": 5.2, "sample_rate": 22050})
        """
        self.output_dir = Path(output_dir)
        self.enabled = enabled
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.enabled:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.log_file = self.output_dir / f"trace_{self.session_id}.log"
            
            # Configuration logger fichier
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.setLevel(logging.DEBUG)
            
            logger.info(f"Debug tracer initialized - Session {self.session_id}")
    
    def log_step(self, step_name: str, metadata: Dict[str, Any]) -> None:
        """
        Enregistre les métadonnées d'une étape du pipeline.
        
        Args:
            step_name: Nom de l'étape (ex: "audio_loaded", "pitch_detected")
            metadata: Dictionnaire de métadonnées à enregistrer
        
        Example:
            >>> tracer.log_step("pitch_detection", {
            ...     "num_frames": 234,
            ...     "avg_confidence": 0.87,
            ...     "processing_time": 2.3
            ... })
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "session_id": self.session_id,
            "step": step_name,
            "metadata": metadata
        }
        
        logger.info(f"Step: {step_name} - {metadata}")
        
        # Sauvegarder aussi en JSON
        json_file = self.output_dir / f"trace_{self.session_id}.json"
        
        # Append to JSON (load existing if present)
        if json_file.exists():
            with open(json_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"session_id": self.session_id, "steps": []}
        
        data["steps"].append(log_entry)
        
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_log_path(self) -> Optional[Path]:
        """Retourne le chemin du fichier de log."""
        return self.log_file if self.enabled else None


class IntermediateStorage:
    """
    Sauvegarde et chargement de résultats intermédiaires du pipeline.
    
    Permet de sauvegarder les données entre étapes pour :
    - Debug et analyse
    - Reprise après échec
    - Comparaison de configurations
    """
    
    def __init__(self, output_dir: str = "output/intermediate"):
        """
        Initialise le système de stockage intermédiaire.
        
        Args:
            output_dir: Répertoire de sauvegarde (défaut: output/intermediate)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_audio(
        self, 
        audio: Any, 
        sample_rate: int, 
        filename: str = "audio_preprocessed.pkl"
    ) -> Path:
        """
        Sauvegarde audio prétraité.
        
        Args:
            audio: Données audio (numpy array)
            sample_rate: Sample rate
            filename: Nom du fichier (défaut: audio_preprocessed.pkl)
        
        Returns:
            Path du fichier sauvegardé
        """
        data = {
            "audio": audio,
            "sample_rate": sample_rate,
            "timestamp": datetime.now().isoformat()
        }
        
        filepath = self.output_dir / filename
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        logger.info(f"Audio saved to {filepath}")
        return filepath
    
    def save_pitch_data(
        self, 
        pitch_frames: List[Any], 
        filename: str = "pitch_data.json"
    ) -> Path:
        """
        Sauvegarde données pitch détectées.
        
        Args:
            pitch_frames: Liste de PitchFrame
            filename: Nom du fichier (défaut: pitch_data.json)
        
        Returns:
            Path du fichier sauvegardé
        """
        # Convertir PitchFrame en dict pour JSON
        data = {
            "pitch_frames": [
                {
                    "time": frame.time,
                    "frequency": frame.frequency,
                    "confidence": frame.confidence
                }
                for frame in pitch_frames
            ],
            "count": len(pitch_frames),
            "timestamp": datetime.now().isoformat()
        }
        
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Pitch data saved to {filepath} ({len(pitch_frames)} frames)")
        return filepath
    
    def save_notes(
        self, 
        notes: List[Any], 
        filename: str = "notes.json"
    ) -> Path:
        """
        Sauvegarde notes segmentées.
        
        Args:
            notes: Liste de Note
            filename: Nom du fichier (défaut: notes.json)
        
        Returns:
            Path du fichier sauvegardé
        """
        data = {
            "notes": [
                {
                    "midi_note": note.midi_note,
                    "start_time": note.start_time,
                    "duration": note.duration
                }
                for note in notes
            ],
            "count": len(notes),
            "timestamp": datetime.now().isoformat()
        }
        
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Notes saved to {filepath} ({len(notes)} notes)")
        return filepath
    
    def save_quantized_notes(
        self, 
        quantized_notes: List[Any], 
        bpm: float,
        filename: str = "quantized_notes.json"
    ) -> Path:
        """
        Sauvegarde notes quantifiées.
        
        Args:
            quantized_notes: Liste de QuantizedNote
            bpm: Tempo détecté
            filename: Nom du fichier (défaut: quantized_notes.json)
        
        Returns:
            Path du fichier sauvegardé
        """
        data = {
            "bpm": bpm,
            "quantized_notes": [
                {
                    "midi_note": note.midi_note,
                    "beat_position": note.beat_position,
                    "duration_beats": note.duration_beats
                }
                for note in quantized_notes
            ],
            "count": len(quantized_notes),
            "timestamp": datetime.now().isoformat()
        }
        
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Quantized notes saved to {filepath} ({len(quantized_notes)} notes)")
        return filepath
    
    def load_audio(self, filename: str = "audio_preprocessed.pkl") -> Dict[str, Any]:
        """
        Charge audio prétraité sauvegardé.
        
        Args:
            filename: Nom du fichier
        
        Returns:
            Dictionnaire contenant audio, sample_rate, timestamp
        """
        filepath = self.output_dir / filename
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        logger.info(f"Audio loaded from {filepath}")
        return data
    
    def load_pitch_data(self, filename: str = "pitch_data.json") -> Dict[str, Any]:
        """
        Charge données pitch sauvegardées.
        
        Args:
            filename: Nom du fichier
        
        Returns:
            Dictionnaire contenant pitch_frames, count, timestamp
        """
        filepath = self.output_dir / filename
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        logger.info(f"Pitch data loaded from {filepath}")
        return data
    
    def list_saved_files(self) -> List[Path]:
        """
        Liste tous les fichiers sauvegardés.
        
        Returns:
            Liste des fichiers Path
        """
        return list(self.output_dir.glob("*"))


def format_duration(seconds: float) -> str:
    """
    Formate une durée en secondes vers format lisible.
    
    Args:
        seconds: Durée en secondes
    
    Returns:
        String formatée (ex: "2m 34s" ou "15.3s")
    
    Example:
        >>> format_duration(154.7)
        '2m 34s'
        >>> format_duration(15.3)
        '15.3s'
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}m {remaining_seconds:.0f}s"


def format_frequency(frequency: float) -> str:
    """
    Formate une fréquence avec note musicale.
    
    Args:
        frequency: Fréquence en Hz
    
    Returns:
        String formatée avec note (ex: "440.0 Hz (A4)")
    
    Example:
        >>> format_frequency(440.0)
        '440.0 Hz (A4)'
        >>> format_frequency(261.63)
        '261.6 Hz (C4)'
    """
    # Conversion Hz → MIDI note number
    import numpy as np
    
    if frequency <= 0:
        return f"{frequency:.1f} Hz (invalid)"
    
    midi_note = int(round(69 + 12 * np.log2(frequency / 440.0)))
    
    # Noms des notes
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    note_name = note_names[midi_note % 12]
    octave = (midi_note // 12) - 1
    
    return f"{frequency:.1f} Hz ({note_name}{octave})"


def print_summary_stats(pitch_frames: List[Any]) -> None:
    """
    Affiche statistiques résumées sur données pitch.
    
    Args:
        pitch_frames: Liste de PitchFrame
    
    Example:
        >>> print_summary_stats(pitch_data)
        Pitch Detection Summary:
        ========================
        Total frames: 234
        Average confidence: 0.87
        Frequency range: 220.0 Hz (A3) - 880.0 Hz (A5)
        Duration: 2.3s
    """
    if not pitch_frames:
        print("No pitch data to summarize")
        return
    
    import numpy as np
    
    frequencies = [p.frequency for p in pitch_frames]
    confidences = [p.confidence for p in pitch_frames]
    times = [p.time for p in pitch_frames]
    
    print("\nPitch Detection Summary:")
    print("=" * 50)
    print(f"Total frames: {len(pitch_frames)}")
    print(f"Average confidence: {np.mean(confidences):.2f}")
    print(f"Frequency range: {format_frequency(min(frequencies))} - {format_frequency(max(frequencies))}")
    print(f"Duration: {format_duration(max(times) - min(times))}")
    print(f"Time span: {min(times):.2f}s - {max(times):.2f}s")
    print("=" * 50)
