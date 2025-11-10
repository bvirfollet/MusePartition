"""
MusePartition - Transcription Pipeline
Orchestration complète : audio → partition
"""

import time
from pathlib import Path
from typing import Optional, Dict, Any
import json

from src.types import TranscriptionResult
from src.audio_processor import AudioProcessor
from src.pitch_detector import PitchDetector
from src.note_segmenter import NoteSegmenter
from src.quantizer import MusicalQuantizer
from src.score_generator import ScoreGenerator
from src.utils import DebugTracer, IntermediateStorage


class TranscriptionPipeline:
    """
    Pipeline complet de transcription audio vers partition musicale.
    
    Orchestre les modules : AudioProcessor → PitchDetector → NoteSegmenter 
    → MusicalQuantizer → ScoreGenerator
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le pipeline avec configuration.
        
        Args:
            config: Dictionnaire de configuration. Si None, utilise config par défaut.
                   Voir config.example.json pour structure complète.
        
        Example:
            >>> # Config par défaut
            >>> pipeline = TranscriptionPipeline()
            >>> 
            >>> # Config personnalisée
            >>> config = {
            ...     "pitch_detection": {"model_capacity": "small"},
            ...     "quantization": {"bpm": 120.0}
            ... }
            >>> pipeline = TranscriptionPipeline(config)
        """
        self.config = self._load_default_config()
        if config:
            self._merge_config(config)
        
        self._validate_config()
        self._init_modules()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Charge configuration par défaut."""
        return {
            "audio": {
                "target_sr": 22050
            },
            "pitch_detection": {
                "model_capacity": "medium",
                "confidence_threshold": 0.5,
                "step_size": 10
            },
            "note_segmentation": {
                "min_note_duration": 0.05,
                "reference_frequency": 440.0,
                "pitch_tolerance": 0.5
            },
            "quantization": {
                "bpm": None,  # Auto-détection
                "time_signature": "4/4",
                "quantization_grid": "1/16",
                "feel": "straight"
            },
            "score_generation": {
                "time_signature": "4/4",
                "key_signature": "C",
                "clef": "treble",
                "instrument_name": "Flute",
                "title": "Transcription",
                "composer": "MusePartition"
            },
            "output": {
                "base_filename": "score",
                "formats": ["musicxml", "midi", "pdf"]
            },
            "debug": {
                "enabled": False,
                "save_intermediate": False
            }
        }
    
    def _merge_config(self, user_config: Dict[str, Any]):
        """Merge config utilisateur avec config par défaut."""
        for section, params in user_config.items():
            if section in self.config:
                if isinstance(params, dict):
                    self.config[section].update(params)
                else:
                    self.config[section] = params
            else:
                self.config[section] = params
    
    def _validate_config(self):
        """Valide la configuration."""
        # Vérifier sections obligatoires
        required_sections = ["audio", "pitch_detection", "note_segmentation", 
                           "quantization", "score_generation", "output"]
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Section '{section}' manquante dans config")
        
        # Valider formats de sortie
        valid_formats = {"musicxml", "midi", "pdf"}
        output_formats = set(self.config["output"]["formats"])
        invalid = output_formats - valid_formats
        if invalid:
            raise ValueError(f"Formats invalides: {invalid}. Valides: {valid_formats}")
    
    def _init_modules(self):
        """Initialise tous les modules du pipeline."""
        debug = self.config["debug"]["enabled"]
        
        # AudioProcessor
        self.audio_processor = AudioProcessor(
            target_sr=self.config["audio"]["target_sr"]
        )
        
        # PitchDetector
        self.pitch_detector = PitchDetector(
            model_capacity=self.config["pitch_detection"]["model_capacity"],
            confidence_threshold=self.config["pitch_detection"]["confidence_threshold"],
            step_size=self.config["pitch_detection"]["step_size"]
        )
        
        # NoteSegmenter
        self.note_segmenter = NoteSegmenter(
            min_note_duration=self.config["note_segmentation"]["min_note_duration"],
            reference_frequency=self.config["note_segmentation"]["reference_frequency"],
            pitch_tolerance=self.config["note_segmentation"]["pitch_tolerance"],
            debug=debug
        )
        
        # MusicalQuantizer
        self.quantizer = MusicalQuantizer(
            bpm=self.config["quantization"]["bpm"],
            time_signature=self.config["quantization"]["time_signature"],
            quantization_grid=self.config["quantization"]["quantization_grid"],
            feel=self.config["quantization"]["feel"],
            debug=debug
        )
        
        # ScoreGenerator
        self.score_generator = ScoreGenerator(
            time_signature=self.config["score_generation"]["time_signature"],
            key_signature=self.config["score_generation"]["key_signature"],
            clef=self.config["score_generation"]["clef"],
            instrument_name=self.config["score_generation"]["instrument_name"],
            debug=debug
        )
        
        # Utils
        self.tracer = DebugTracer(
            output_dir="output/debug",
            enabled=debug
        )
        
        self.storage = IntermediateStorage(
            output_dir="output/intermediate"
        ) if self.config["debug"]["save_intermediate"] else None
    
    def transcribe(
        self,
        audio_file: str,
        output_dir: str = "output"
    ) -> TranscriptionResult:
        """
        Transcrit un fichier audio en partition musicale.
        
        Args:
            audio_file: Chemin vers fichier audio (WAV, MP3, FLAC).
            output_dir: Répertoire de sortie (défaut: "output").
        
        Returns:
            TranscriptionResult avec chemins fichiers générés et statistiques.
        
        Raises:
            FileNotFoundError: Si audio_file n'existe pas.
            RuntimeError: Si erreur durant transcription.
        
        Example:
            >>> pipeline = TranscriptionPipeline()
            >>> result = pipeline.transcribe("flute.wav", "output/")
            >>> print(f"Partition créée: {result.musicxml_path}")
            >>> print(f"Tempo: {result.bpm:.1f} BPM")
            >>> print(f"Notes: {result.num_notes}")
        """
        start_time = time.time()
        
        # Validation
        audio_path = Path(audio_file)
        if not audio_path.exists():
            raise FileNotFoundError(f"Fichier audio introuvable: {audio_file}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.tracer.log_step("pipeline_start", {
            "audio_file": str(audio_file),
            "output_dir": str(output_dir),
            "config": self.config
        })
        
        try:
            # Étape 1 : Audio Processing
            self.tracer.log_step("step_1_audio_processing", {"status": "start"})
            audio, sr = self.audio_processor.preprocess(str(audio_path))
            self.tracer.log_step("step_1_audio_processing", {
                "status": "complete",
                "duration_s": len(audio) / sr,
                "sample_rate": sr
            })
            
            if self.storage:
                self.storage.save_audio(audio, sr)
            
            # Étape 2 : Pitch Detection
            self.tracer.log_step("step_2_pitch_detection", {"status": "start"})
            pitch_data = self.pitch_detector.detect_pitch(audio, sr)
            self.tracer.log_step("step_2_pitch_detection", {
                "status": "complete",
                "frames": len(pitch_data),
                "avg_confidence": sum(p.confidence for p in pitch_data) / len(pitch_data) if pitch_data else 0
            })
            
            if not pitch_data:
                raise RuntimeError("Aucune donnée pitch détectée. Audio silencieux ou trop bruité ?")
            
            # Étape 3 : Note Segmentation
            self.tracer.log_step("step_3_note_segmentation", {"status": "start"})
            notes = self.note_segmenter.segment_notes(pitch_data)
            self.tracer.log_step("step_3_note_segmentation", {
                "status": "complete",
                "notes": len(notes)
            })
            
            if not notes:
                raise RuntimeError("Aucune note détectée après segmentation.")
            
            # Étape 4 : Musical Quantization
            self.tracer.log_step("step_4_quantization", {"status": "start"})
            
            # Si BPM fourni en config, l'utiliser
            config_bpm = self.config["quantization"]["bpm"]
            
            quantized_notes, detected_bpm = self.quantizer.quantize_notes(
                notes,
                bpm=config_bpm,
                audio=audio if not config_bpm else None,
                sr=sr if not config_bpm else None
            )
            
            self.tracer.log_step("step_4_quantization", {
                "status": "complete",
                "bpm": detected_bpm,
                "bpm_source": "config" if config_bpm else "auto-detected",
                "quantized_notes": len(quantized_notes)
            })
            
            # Étape 5 : Score Generation
            self.tracer.log_step("step_5_score_generation", {"status": "start"})
            
            score_paths = self.score_generator.generate_score(
                quantized_notes,
                bpm=detected_bpm,
                output_dir=str(output_path),
                base_filename=self.config["output"]["base_filename"],
                title=self.config["score_generation"]["title"],
                composer=self.config["score_generation"]["composer"]
            )
            
            self.tracer.log_step("step_5_score_generation", {
                "status": "complete",
                "musicxml": str(score_paths['musicxml']),
                "midi": str(score_paths['midi']),
                "pdf": str(score_paths['pdf']) if score_paths['pdf'] else "skipped"
            })
            
            # Construire résultat
            processing_time = time.time() - start_time
            
            result = TranscriptionResult(
                pdf_path=str(score_paths['pdf']) if score_paths['pdf'] else "",
                musicxml_path=str(score_paths['musicxml']),
                midi_path=str(score_paths['midi']),
                bpm=detected_bpm,
                num_notes=len(quantized_notes),
                processing_time=processing_time
            )
            
            self.tracer.log_step("pipeline_complete", {
                "processing_time_s": processing_time,
                "num_notes": len(quantized_notes),
                "bpm": detected_bpm
            })
            
            return result
        
        except Exception as e:
            self.tracer.log_step("pipeline_error", {
                "error": str(e),
                "type": type(e).__name__
            })
            raise RuntimeError(f"Erreur durant transcription: {e}") from e
    
    @classmethod
    def from_json_file(cls, config_path: str) -> 'TranscriptionPipeline':
        """
        Crée pipeline à partir d'un fichier JSON.
        
        Args:
            config_path: Chemin vers fichier config JSON.
        
        Returns:
            Instance de TranscriptionPipeline.
        
        Example:
            >>> pipeline = TranscriptionPipeline.from_json_file("config.json")
        """
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        return cls(config)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Charge configuration depuis fichier JSON.
    
    Args:
        config_path: Chemin fichier config.
    
    Returns:
        Dictionnaire configuration.
    """
    with open(config_path, 'r') as f:
        return json.load(f)
