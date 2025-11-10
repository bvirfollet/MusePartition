"""
MusePartition - Musical Quantizer Module
Détection tempo et quantification rythmique des notes
"""

import numpy as np
import librosa
from typing import List, Optional, Tuple
from src.types import Note, QuantizedNote
from src.utils import DebugTracer


class MusicalQuantizer:
    """
    Quantifie les notes sur une grille rythmique et détecte le tempo.
    
    Convertit les notes avec timing absolu (secondes) en notes quantifiées
    alignées sur une grille rythmique (beats), facilitant la notation musicale.
    """
    
    def __init__(
        self,
        bpm: Optional[float] = None,
        time_signature: str = "4/4",
        quantization_grid: str = "1/16",
        debug: bool = False
    ):
        """
        Initialise le MusicalQuantizer.
        
        Args:
            bpm: Tempo fixe en BPM (défaut: None = détection auto).
            time_signature: Signature temporelle (défaut: "4/4").
                Formats supportés: "4/4", "3/4", "6/8", "2/4", etc.
            quantization_grid: Grille de quantification (défaut: "1/16").
                Options: "1/4" (noires), "1/8" (croches), "1/16" (doubles-croches), "1/32".
            debug: Active le traçage debug (défaut: False).
        
        Example:
            >>> # Auto-détection tempo
            >>> quantizer = MusicalQuantizer(quantization_grid="1/16")
            >>> 
            >>> # Tempo fixe 120 BPM
            >>> quantizer = MusicalQuantizer(bpm=120.0, quantization_grid="1/8")
        """
        self.bpm = bpm
        self.time_signature = time_signature
        self.quantization_grid = quantization_grid
        self.tracer = DebugTracer(output_dir="output/debug", enabled=debug)
        
        # Parser time signature
        self._parse_time_signature()
        
        # Parser quantization grid
        self._parse_quantization_grid()
        
        self.tracer.log_step("quantizer_init", {
            "bpm": bpm,
            "time_signature": time_signature,
            "quantization_grid": quantization_grid,
            "beats_per_bar": self.beats_per_bar,
            "beat_unit": self.beat_unit,
            "grid_value": self.grid_value
        })
    
    def _parse_time_signature(self) -> None:
        """Parse la signature temporelle (ex: "4/4" → 4 beats par mesure, noire = beat)."""
        try:
            parts = self.time_signature.split("/")
            self.beats_per_bar = int(parts[0])
            self.beat_unit = int(parts[1])
        except (ValueError, IndexError):
            raise ValueError(f"Signature temporelle invalide: {self.time_signature}. Format attendu: 'X/Y'")
    
    def _parse_quantization_grid(self) -> None:
        """Parse la grille de quantification (ex: "1/16" → 16ème de note)."""
        valid_grids = {
            "1/4": 4,    # Noires
            "1/8": 8,    # Croches
            "1/16": 16,  # Doubles-croches
            "1/32": 32   # Triples-croches
        }
        
        if self.quantization_grid not in valid_grids:
            raise ValueError(f"Grille invalide: {self.quantization_grid}. Options: {list(valid_grids.keys())}")
        
        self.grid_value = valid_grids[self.quantization_grid]
    
    def detect_tempo(self, audio: np.ndarray, sr: int) -> float:
        """
        Détecte le tempo automatiquement à partir de l'audio.
        
        Utilise librosa.beat.tempo() basé sur l'analyse spectrale des onsets.
        
        Args:
            audio: Signal audio mono (numpy array).
            sr: Sample rate en Hz.
        
        Returns:
            Tempo estimé en BPM (Beats Per Minute).
        
        Raises:
            ValueError: Si audio vide ou sr invalide.
        
        Example:
            >>> quantizer = MusicalQuantizer()
            >>> audio, sr = processor.preprocess("song.wav")
            >>> bpm = quantizer.detect_tempo(audio, sr)
            >>> print(f"Tempo détecté: {bpm:.1f} BPM")
        """
        if len(audio) == 0:
            raise ValueError("Audio vide")
        if sr <= 0:
            raise ValueError(f"Sample rate invalide: {sr}")
        
        self.tracer.log_step("tempo_detection_start", {
            "audio_duration": len(audio) / sr,
            "sample_rate": sr
        })
        
        # Détection tempo avec librosa
        tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
        
        # librosa retourne un array, prendre première valeur
        if isinstance(tempo, np.ndarray):
            tempo = float(tempo[0])
        else:
            tempo = float(tempo)
        
        self.tracer.log_step("tempo_detection_complete", {
            "detected_bpm": tempo
        })
        
        return tempo
    
    def seconds_to_beats(self, time_seconds: float, bpm: float) -> float:
        """
        Convertit un temps en secondes vers beats.
        
        Args:
            time_seconds: Temps en secondes.
            bpm: Tempo en BPM.
        
        Returns:
            Position en beats (float).
        
        Example:
            >>> quantizer = MusicalQuantizer()
            >>> # À 120 BPM, 1 beat = 0.5s
            >>> beats = quantizer.seconds_to_beats(1.0, 120.0)
            >>> # beats = 2.0
        """
        seconds_per_beat = 60.0 / bpm
        return time_seconds / seconds_per_beat
    
    def beats_to_seconds(self, beats: float, bpm: float) -> float:
        """
        Convertit des beats vers secondes (inverse de seconds_to_beats).
        
        Args:
            beats: Position en beats.
            bpm: Tempo en BPM.
        
        Returns:
            Temps en secondes.
        """
        seconds_per_beat = 60.0 / bpm
        return beats * seconds_per_beat
    
    def quantize_position(self, position_beats: float) -> float:
        """
        Quantifie une position en beats sur la grille rythmique.
        
        Args:
            position_beats: Position en beats (float).
        
        Returns:
            Position quantifiée (arrondie au grid_value le plus proche).
        
        Example:
            >>> quantizer = MusicalQuantizer(quantization_grid="1/16")
            >>> # Grille 1/16 = divisions de 0.25 beats (en 4/4)
            >>> quantizer.quantize_position(1.37)
            >>> # Retourne 1.25 ou 1.5 selon arrondi
        """
        # Calculer la taille d'un step de grille en beats
        # En 4/4 avec grid 1/16 : 1 beat = 4 x 1/16, donc step = 0.25 beats
        grid_step = 1.0 / (self.grid_value / 4)
        
        # Arrondir à la grille la plus proche
        quantized = round(position_beats / grid_step) * grid_step
        return quantized
    
    def quantize_duration(self, duration_beats: float) -> float:
        """
        Quantifie une durée en beats sur la grille rythmique.
        
        Args:
            duration_beats: Durée en beats.
        
        Returns:
            Durée quantifiée (minimum = 1 grid step).
        """
        grid_step = 1.0 / (self.grid_value / 4)
        
        # Arrondir à la grille, minimum = 1 step
        quantized = max(grid_step, round(duration_beats / grid_step) * grid_step)
        return quantized
    
    def quantize_notes(
        self, 
        notes: List[Note], 
        bpm: Optional[float] = None,
        audio: Optional[np.ndarray] = None,
        sr: Optional[int] = None
    ) -> Tuple[List[QuantizedNote], float]:
        """
        Quantifie une liste de notes sur la grille rythmique.
        
        Args:
            notes: Liste de notes à quantifier.
            bpm: Tempo en BPM (défaut: None = auto-détection ou self.bpm).
            audio: Audio pour détection tempo si bpm=None (optionnel).
            sr: Sample rate pour détection tempo (optionnel).
        
        Returns:
            Tuple (quantized_notes, bpm_used):
                - quantized_notes: Liste de QuantizedNote
                - bpm_used: BPM utilisé pour la quantification
        
        Raises:
            ValueError: Si notes vide ou BPM indéterminable.
        
        Example:
            >>> notes = segmenter.segment_notes(pitch_frames)
            >>> 
            >>> # Avec auto-détection tempo
            >>> quantized, bpm = quantizer.quantize_notes(notes, audio=audio, sr=sr)
            >>> 
            >>> # Avec tempo fixe
            >>> quantized, bpm = quantizer.quantize_notes(notes, bpm=120.0)
        """
        if not notes:
            raise ValueError("Liste de notes vide")
        
        # Déterminer BPM
        if bpm is None:
            bpm = self.bpm  # Utiliser self.bpm si défini
        
        if bpm is None:
            # Auto-détection
            if audio is None or sr is None:
                raise ValueError("BPM non fourni et audio/sr manquants pour auto-détection")
            bpm = self.detect_tempo(audio, sr)
        
        self.tracer.log_step("quantization_start", {
            "input_notes": len(notes),
            "bpm": bpm,
            "quantization_grid": self.quantization_grid
        })
        
        quantized_notes = []
        
        for note in notes:
            # Convertir temps absolu → beats
            start_beats = self.seconds_to_beats(note.start_time, bpm)
            duration_seconds = note.duration
            duration_beats = self.seconds_to_beats(duration_seconds, bpm)
            
            # Quantifier
            quantized_start = self.quantize_position(start_beats)
            quantized_duration = self.quantize_duration(duration_beats)
            
            quantized_notes.append(QuantizedNote(
                midi_note=note.midi_note,
                beat_position=float(quantized_start),
                duration_beats=float(quantized_duration)
            ))
        
        self.tracer.log_step("quantization_complete", {
            "output_notes": len(quantized_notes),
            "bpm_used": bpm
        })
        
        return quantized_notes, bpm
    
    def print_quantization_summary(
        self, 
        notes: List[Note],
        quantized_notes: List[QuantizedNote],
        bpm: float
    ) -> None:
        """
        Affiche un résumé de la quantification.
        
        Args:
            notes: Notes originales.
            quantized_notes: Notes quantifiées.
            bpm: BPM utilisé.
        """
        if not notes or not quantized_notes:
            print("Aucune note à résumer")
            return
        
        print("\nMusical Quantization Summary:")
        print("=" * 70)
        print(f"Tempo: {bpm:.1f} BPM")
        print(f"Time signature: {self.time_signature}")
        print(f"Quantization grid: {self.quantization_grid}")
        print(f"Total notes: {len(quantized_notes)}")
        
        # Calcul timing shift moyen
        timing_errors = []
        for orig, quant in zip(notes, quantized_notes):
            orig_beats = self.seconds_to_beats(orig.start_time, bpm)
            shift = abs(quant.beat_position - orig_beats)
            timing_errors.append(shift)
        
        avg_shift = np.mean(timing_errors)
        max_shift = np.max(timing_errors)
        
        print(f"Average timing shift: {avg_shift:.3f} beats ({self.beats_to_seconds(avg_shift, bpm)*1000:.1f}ms)")
        print(f"Max timing shift: {max_shift:.3f} beats ({self.beats_to_seconds(max_shift, bpm)*1000:.1f}ms)")
        print("=" * 70)
        
        # Afficher premières notes
        print("\nFirst 3 notes (before → after):")
        for i in range(min(3, len(notes))):
            orig = notes[i]
            quant = quantized_notes[i]
            print(f"  {i+1}. MIDI {orig.midi_note}: "
                  f"{orig.start_time:.3f}s → beat {quant.beat_position:.2f}, "
                  f"duration {orig.duration:.3f}s → {quant.duration_beats:.2f} beats")
