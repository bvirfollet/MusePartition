"""
MusePartition - Note Segmenter Module
Conversion de pitch frames en notes MIDI discrètes avec détection onset/offset
"""

import numpy as np
from typing import List, Optional
from src.types import PitchFrame, Note
from src.utils import DebugTracer


class NoteSegmenter:
    """
    Segmente les données de pitch en notes musicales discrètes.
    
    Convertit les frames de détection pitch (timestamp, fréquence, confiance)
    en notes MIDI avec début et durée, en détectant les transitions entre notes.
    """
    
    def __init__(
        self,
        min_note_duration: float = 0.05,
        reference_frequency: float = 440.0,
        pitch_tolerance: float = 0.5,
        debug: bool = False
    ):
        """
        Initialise le NoteSegmenter.
        
        Args:
            min_note_duration: Durée minimale d'une note en secondes (défaut: 0.05s = 50ms).
                Les notes plus courtes sont filtrées comme bruit/transitoires.
            reference_frequency: Fréquence de référence pour A4 en Hz (défaut: 440.0).
                Permet d'ajuster pour orchestres baroques (415 Hz) ou modernes (442-443 Hz).
            pitch_tolerance: Tolérance en demi-tons pour grouper notes (défaut: 0.5).
                Frames dans ±tolerance du même MIDI sont groupées ensemble.
            debug: Active le traçage debug (défaut: False).
        
        Note:
            La référence 440 Hz correspond au standard ISO 16 (1975).
            Orchestres français utilisent souvent 442 Hz.
            Musique baroque utilise souvent 415 Hz (≈ -1 demi-ton).
        
        Example:
            >>> # Configuration standard
            >>> segmenter = NoteSegmenter()
            >>> 
            >>> # Orchestre français (diapason élevé)
            >>> segmenter = NoteSegmenter(reference_frequency=442.0)
            >>> 
            >>> # Musique baroque
            >>> segmenter = NoteSegmenter(reference_frequency=415.0)
        """
        self.min_note_duration = min_note_duration
        self.reference_frequency = reference_frequency
        self.pitch_tolerance = pitch_tolerance
        self.tracer = DebugTracer(output_dir="output/debug", enabled=debug)
        
        self.tracer.log_step("note_segmenter_init", {
            "min_note_duration": min_note_duration,
            "reference_frequency": reference_frequency,
            "pitch_tolerance": pitch_tolerance
        })
    
    def frequency_to_midi(self, frequency: float) -> int:
        """
        Convertit une fréquence Hz en numéro MIDI.
        
        Utilise la formule standard : MIDI = 69 + 12 * log2(freq / ref_freq)
        où ref_freq est la fréquence de référence (A4, défaut 440 Hz).
        
        Args:
            frequency: Fréquence en Hz (doit être > 0).
        
        Returns:
            Numéro MIDI arrondi [0, 127].
            - 0 = C-1 (8.18 Hz)
            - 60 = C4 (261.63 Hz, Do médium)
            - 69 = A4 (référence)
            - 127 = G9 (12543.85 Hz)
        
        Raises:
            ValueError: Si frequency <= 0.
        
        Example:
            >>> segmenter = NoteSegmenter()
            >>> segmenter.frequency_to_midi(440.0)  # A4
            69
            >>> segmenter.frequency_to_midi(261.63)  # C4
            60
            >>> segmenter.frequency_to_midi(880.0)  # A5
            81
            
            >>> # Avec référence différente (orchestre français 442 Hz)
            >>> segmenter_fr = NoteSegmenter(reference_frequency=442.0)
            >>> segmenter_fr.frequency_to_midi(442.0)  # A4 français
            69
        """
        if frequency <= 0:
            raise ValueError(f"Fréquence doit être > 0, reçu: {frequency}")
        
        # Formule MIDI standard avec référence ajustable
        midi_float = 69 + 12 * np.log2(frequency / self.reference_frequency)
        midi_note = int(round(midi_float))
        
        # Clamp dans la plage MIDI valide [0, 127]
        return max(0, min(127, midi_note))
    
    def midi_to_frequency(self, midi_note: int) -> float:
        """
        Convertit un numéro MIDI en fréquence Hz (inverse de frequency_to_midi).
        
        Args:
            midi_note: Numéro MIDI [0, 127].
        
        Returns:
            Fréquence en Hz.
        
        Example:
            >>> segmenter = NoteSegmenter()
            >>> segmenter.midi_to_frequency(69)  # A4
            440.0
            >>> segmenter.midi_to_frequency(60)  # C4
            261.63
        """
        return self.reference_frequency * (2 ** ((midi_note - 69) / 12))
    
    def _is_same_note(self, midi1: int, midi2: int) -> bool:
        """
        Détermine si deux MIDI notes sont considérées identiques (tolérance).
        
        Args:
            midi1, midi2: Numéros MIDI à comparer.
        
        Returns:
            True si différence <= pitch_tolerance.
        """
        return abs(midi1 - midi2) <= self.pitch_tolerance
    
    def segment_notes(self, pitch_frames: List[PitchFrame]) -> List[Note]:
        """
        Segmente les pitch frames en notes discrètes.
        
        Algorithme:
        1. Convertir chaque frame en MIDI
        2. Grouper frames consécutives de même MIDI (± tolérance)
        3. Créer Note pour chaque groupe (onset = premier frame, offset = dernier)
        4. Filtrer notes < min_note_duration
        
        Args:
            pitch_frames: Liste de PitchFrame triée chronologiquement.
        
        Returns:
            Liste de Note triée chronologiquement.
            Notes trop courtes (< min_note_duration) sont filtrées.
        
        Raises:
            ValueError: Si pitch_frames est vide.
        
        Example:
            >>> from src.pitch_detector import PitchDetector
            >>> from src.audio_processor import AudioProcessor
            >>> 
            >>> processor = AudioProcessor()
            >>> detector = PitchDetector()
            >>> segmenter = NoteSegmenter(min_note_duration=0.05)
            >>> 
            >>> audio, sr = processor.preprocess("flute.wav")
            >>> pitch_data = detector.detect_pitch(audio, sr)
            >>> notes = segmenter.segment_notes(pitch_data)
            >>> 
            >>> print(f"Détecté {len(notes)} notes")
            >>> for note in notes[:5]:
            ...     print(f"MIDI {note.midi_note} à {note.start_time:.2f}s, durée {note.duration:.2f}s")
        """
        if not pitch_frames:
            raise ValueError("pitch_frames ne peut pas être vide")
        
        self.tracer.log_step("segmentation_start", {
            "input_frames": len(pitch_frames),
            "time_span": f"{pitch_frames[0].time:.2f}s - {pitch_frames[-1].time:.2f}s"
        })
        
        notes = []
        
        # État pour note en cours de construction
        current_midi = None
        current_start_time = None
        current_end_time = None
        current_frequencies = []  # Pour calculer fréquence moyenne
        
        for frame in pitch_frames:
            midi_note = self.frequency_to_midi(frame.frequency)
            
            # Première frame
            if current_midi is None:
                current_midi = midi_note
                current_start_time = frame.time
                current_end_time = frame.time
                current_frequencies = [frame.frequency]
                continue
            
            # Même note (avec tolérance) → étendre
            if self._is_same_note(midi_note, current_midi):
                current_end_time = frame.time
                current_frequencies.append(frame.frequency)
            else:
                # Note différente → créer note précédente et démarrer nouvelle
                duration = current_end_time - current_start_time
                
                # Filtrer notes trop courtes
                if duration >= self.min_note_duration:
                    notes.append(Note(
                        midi_note=int(current_midi),
                        start_time=float(current_start_time),
                        duration=float(duration)
                    ))
                
                # Démarrer nouvelle note
                current_midi = midi_note
                current_start_time = frame.time
                current_end_time = frame.time
                current_frequencies = [frame.frequency]
        
        # Traiter dernière note
        if current_midi is not None:
            duration = current_end_time - current_start_time
            if duration >= self.min_note_duration:
                notes.append(Note(
                    midi_note=int(current_midi),
                    start_time=float(current_start_time),
                    duration=float(duration)
                ))
        
        self.tracer.log_step("segmentation_complete", {
            "output_notes": len(notes),
            "filtered_count": len(pitch_frames) - len(notes),
            "avg_duration": float(np.mean([n.duration for n in notes])) if notes else 0,
            "midi_range": f"{min(n.midi_note for n in notes)} - {max(n.midi_note for n in notes)}" if notes else "N/A"
        })
        
        return notes
    
    def get_note_name(self, midi_note: int) -> str:
        """
        Convertit un numéro MIDI en nom de note (ex: "C4", "A#3").
        
        Args:
            midi_note: Numéro MIDI [0, 127].
        
        Returns:
            Nom de note avec octave (notation scientifique).
        
        Example:
            >>> segmenter = NoteSegmenter()
            >>> segmenter.get_note_name(60)
            'C4'
            >>> segmenter.get_note_name(69)
            'A4'
            >>> segmenter.get_note_name(61)
            'C#4'
        """
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (midi_note // 12) - 1
        note = note_names[midi_note % 12]
        return f"{note}{octave}"
    
    def print_notes_summary(self, notes: List[Note]) -> None:
        """
        Affiche un résumé des notes segmentées.
        
        Args:
            notes: Liste de notes à résumer.
        """
        if not notes:
            print("Aucune note détectée")
            return
        
        print("\nNote Segmentation Summary:")
        print("=" * 70)
        print(f"Total notes: {len(notes)}")
        print(f"MIDI range: {min(n.midi_note for n in notes)} ({self.get_note_name(min(n.midi_note for n in notes))}) - "
              f"{max(n.midi_note for n in notes)} ({self.get_note_name(max(n.midi_note for n in notes))})")
        print(f"Duration range: {min(n.duration for n in notes):.3f}s - {max(n.duration for n in notes):.3f}s")
        print(f"Average duration: {np.mean([n.duration for n in notes]):.3f}s")
        print(f"Total music duration: {notes[-1].start_time + notes[-1].duration - notes[0].start_time:.2f}s")
        print(f"Reference frequency: {self.reference_frequency} Hz")
        print("=" * 70)
        
        # Afficher premières notes
        print("\nFirst 5 notes:")
        for i, note in enumerate(notes[:5]):
            note_name = self.get_note_name(note.midi_note)
            freq = self.midi_to_frequency(note.midi_note)
            print(f"  {i+1}. {note_name} (MIDI {note.midi_note}, {freq:.2f} Hz) "
                  f"at {note.start_time:.2f}s, duration {note.duration:.3f}s")
