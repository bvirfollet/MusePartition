"""
MusePartition - Note Segmenter Tests
Unit tests for the note_segmenter module
"""

import pytest
import numpy as np
from src.note_segmenter import NoteSegmenter
from src.types import PitchFrame, Note


class TestNoteSegmenter:
    """Test suite for NoteSegmenter class."""
    
    @pytest.fixture
    def segmenter(self):
        """Crée un NoteSegmenter standard."""
        return NoteSegmenter(
            min_note_duration=0.05,
            reference_frequency=440.0,
            pitch_tolerance=0.5
        )
    
    @pytest.fixture
    def segmenter_french(self):
        """Crée un NoteSegmenter avec diapason français (442 Hz)."""
        return NoteSegmenter(
            min_note_duration=0.05,
            reference_frequency=442.0,
            pitch_tolerance=0.5
        )
    
    @pytest.fixture
    def segmenter_baroque(self):
        """Crée un NoteSegmenter avec diapason baroque (415 Hz)."""
        return NoteSegmenter(
            min_note_duration=0.05,
            reference_frequency=415.0,
            pitch_tolerance=0.5
        )
    
    # --- Tests Initialisation ---
    
    def test_init_default(self):
        """Test initialisation avec paramètres par défaut."""
        segmenter = NoteSegmenter()
        
        assert segmenter.min_note_duration == 0.05
        assert segmenter.reference_frequency == 440.0
        assert segmenter.pitch_tolerance == 0.5
    
    def test_init_custom_reference(self):
        """Test initialisation avec référence personnalisée."""
        segmenter = NoteSegmenter(reference_frequency=442.0)
        
        assert segmenter.reference_frequency == 442.0
    
    def test_init_baroque(self):
        """Test initialisation avec référence baroque."""
        segmenter = NoteSegmenter(reference_frequency=415.0)
        
        assert segmenter.reference_frequency == 415.0
    
    # --- Tests Conversion Fréquence → MIDI ---
    
    def test_frequency_to_midi_a4(self, segmenter):
        """Test conversion A4 (440 Hz) → MIDI 69."""
        midi = segmenter.frequency_to_midi(440.0)
        assert midi == 69
    
    def test_frequency_to_midi_c4(self, segmenter):
        """Test conversion C4 (261.63 Hz) → MIDI 60."""
        midi = segmenter.frequency_to_midi(261.63)
        assert midi == 60
    
    def test_frequency_to_midi_a5(self, segmenter):
        """Test conversion A5 (880 Hz) → MIDI 81."""
        midi = segmenter.frequency_to_midi(880.0)
        assert midi == 81
    
    def test_frequency_to_midi_a3(self, segmenter):
        """Test conversion A3 (220 Hz) → MIDI 57."""
        midi = segmenter.frequency_to_midi(220.0)
        assert midi == 57
    
    def test_frequency_to_midi_with_french_reference(self, segmenter_french):
        """Test conversion avec référence française (442 Hz)."""
        # 442 Hz doit donner MIDI 69 avec référence 442
        midi = segmenter_french.frequency_to_midi(442.0)
        assert midi == 69
        
        # 440 Hz avec référence 442 doit donner légèrement moins que 69
        midi_440 = segmenter_french.frequency_to_midi(440.0)
        assert midi_440 == 69  # Arrondi à 69 car différence < 0.5 demi-ton
    
    def test_frequency_to_midi_with_baroque_reference(self, segmenter_baroque):
        """Test conversion avec référence baroque (415 Hz)."""
        # 415 Hz doit donner MIDI 69 avec référence 415
        midi = segmenter_baroque.frequency_to_midi(415.0)
        assert midi == 69
        
        # 440 Hz avec référence 415 est environ +1 demi-ton
        midi_440 = segmenter_baroque.frequency_to_midi(440.0)
        assert midi_440 == 70  # A#4 en baroque
    
    def test_frequency_to_midi_invalid_zero(self, segmenter):
        """Test conversion avec fréquence nulle (invalide)."""
        with pytest.raises(ValueError, match="Fréquence doit être > 0"):
            segmenter.frequency_to_midi(0.0)
    
    def test_frequency_to_midi_invalid_negative(self, segmenter):
        """Test conversion avec fréquence négative (invalide)."""
        with pytest.raises(ValueError, match="Fréquence doit être > 0"):
            segmenter.frequency_to_midi(-100.0)
    
    def test_frequency_to_midi_clamping_low(self, segmenter):
        """Test clamping pour fréquences très basses."""
        # 8 Hz est théoriquement MIDI ~-1, doit être clampé à 0
        midi = segmenter.frequency_to_midi(8.0)
        assert midi >= 0
    
    def test_frequency_to_midi_clamping_high(self, segmenter):
        """Test clamping pour fréquences très hautes."""
        # 20000 Hz est au-delà de MIDI 127, doit être clampé
        midi = segmenter.frequency_to_midi(20000.0)
        assert midi <= 127
    
    # --- Tests MIDI → Fréquence (inverse) ---
    
    def test_midi_to_frequency_a4(self, segmenter):
        """Test conversion MIDI 69 → 440 Hz."""
        freq = segmenter.midi_to_frequency(69)
        assert abs(freq - 440.0) < 0.01
    
    def test_midi_to_frequency_c4(self, segmenter):
        """Test conversion MIDI 60 → 261.63 Hz."""
        freq = segmenter.midi_to_frequency(60)
        assert abs(freq - 261.63) < 0.1
    
    def test_midi_to_frequency_roundtrip(self, segmenter):
        """Test aller-retour fréquence → MIDI → fréquence."""
        original_freq = 523.25  # C5
        midi = segmenter.frequency_to_midi(original_freq)
        reconstructed_freq = segmenter.midi_to_frequency(midi)
        
        # Doit être proche (pas exactement égal à cause de l'arrondi MIDI)
        assert abs(reconstructed_freq - original_freq) < 5.0  # < 5 Hz erreur
    
    # --- Tests Get Note Name ---
    
    def test_get_note_name_c4(self, segmenter):
        """Test conversion MIDI 60 → 'C4'."""
        assert segmenter.get_note_name(60) == "C4"
    
    def test_get_note_name_a4(self, segmenter):
        """Test conversion MIDI 69 → 'A4'."""
        assert segmenter.get_note_name(69) == "A4"
    
    def test_get_note_name_sharp(self, segmenter):
        """Test conversion MIDI 61 → 'C#4'."""
        assert segmenter.get_note_name(61) == "C#4"
    
    def test_get_note_name_low_octave(self, segmenter):
        """Test conversion notes octave basse."""
        assert segmenter.get_note_name(48) == "C3"
        assert segmenter.get_note_name(36) == "C2"
    
    def test_get_note_name_high_octave(self, segmenter):
        """Test conversion notes octave haute."""
        assert segmenter.get_note_name(84) == "C6"
        assert segmenter.get_note_name(96) == "C7"
    
    # --- Tests Segmentation Notes ---
    
    def test_segment_notes_single_note(self, segmenter):
        """Test segmentation d'une seule note soutenue."""
        # Créer 10 frames de A4 (440 Hz) sur 1 seconde
        pitch_frames = [
            PitchFrame(time=i * 0.1, frequency=440.0, confidence=0.9)
            for i in range(10)
        ]
        
        notes = segmenter.segment_notes(pitch_frames)
        
        assert len(notes) == 1
        assert notes[0].midi_note == 69  # A4
        assert notes[0].start_time == 0.0
        assert abs(notes[0].duration - 0.9) < 0.01
    
    def test_segment_notes_two_notes(self, segmenter):
        """Test segmentation de deux notes distinctes."""
        pitch_frames = [
            # Note 1: C4 (261.63 Hz) pendant 0.5s
            PitchFrame(time=0.0, frequency=261.63, confidence=0.9),
            PitchFrame(time=0.1, frequency=261.63, confidence=0.9),
            PitchFrame(time=0.2, frequency=261.63, confidence=0.9),
            PitchFrame(time=0.3, frequency=261.63, confidence=0.9),
            PitchFrame(time=0.4, frequency=261.63, confidence=0.9),
            # Note 2: E4 (329.63 Hz) pendant 0.5s
            PitchFrame(time=0.5, frequency=329.63, confidence=0.9),
            PitchFrame(time=0.6, frequency=329.63, confidence=0.9),
            PitchFrame(time=0.7, frequency=329.63, confidence=0.9),
            PitchFrame(time=0.8, frequency=329.63, confidence=0.9),
            PitchFrame(time=0.9, frequency=329.63, confidence=0.9),
        ]
        
        notes = segmenter.segment_notes(pitch_frames)
        
        assert len(notes) == 2
        assert notes[0].midi_note == 60  # C4
        assert notes[1].midi_note == 64  # E4
        assert abs(notes[0].duration - 0.4) < 0.01
        assert abs(notes[1].duration - 0.4) < 0.01
    
    def test_segment_notes_filter_short(self, segmenter):
        """Test filtrage des notes trop courtes."""
        pitch_frames = [
            # Note courte (30ms) - doit être filtrée (< 50ms min)
            PitchFrame(time=0.0, frequency=440.0, confidence=0.9),
            PitchFrame(time=0.01, frequency=440.0, confidence=0.9),
            PitchFrame(time=0.02, frequency=440.0, confidence=0.9),
            PitchFrame(time=0.03, frequency=440.0, confidence=0.9),
            # Note longue (200ms) - doit être gardée
            PitchFrame(time=0.1, frequency=523.25, confidence=0.9),
            PitchFrame(time=0.15, frequency=523.25, confidence=0.9),
            PitchFrame(time=0.2, frequency=523.25, confidence=0.9),
            PitchFrame(time=0.25, frequency=523.25, confidence=0.9),
            PitchFrame(time=0.3, frequency=523.25, confidence=0.9),
        ]
        
        notes = segmenter.segment_notes(pitch_frames)
        
        # Seule la note longue doit être présente
        assert len(notes) == 1
        assert notes[0].midi_note == 72  # C5
        assert notes[0].duration >= 0.05
    
    def test_segment_notes_pitch_tolerance(self, segmenter):
        """Test tolérance pitch (variations micro-tonales groupées)."""
        # Variations autour de 440 Hz (±2 Hz) doivent être groupées
        pitch_frames = [
            PitchFrame(time=0.0, frequency=439.0, confidence=0.9),
            PitchFrame(time=0.1, frequency=440.0, confidence=0.9),
            PitchFrame(time=0.2, frequency=441.0, confidence=0.9),
            PitchFrame(time=0.3, frequency=440.5, confidence=0.9),
            PitchFrame(time=0.4, frequency=439.5, confidence=0.9),
        ]
        
        notes = segmenter.segment_notes(pitch_frames)
        
        # Toutes ces fréquences → MIDI 69, donc 1 seule note
        assert len(notes) == 1
        assert notes[0].midi_note == 69
    
    def test_segment_notes_empty(self, segmenter):
        """Test segmentation avec liste vide (erreur)."""
        with pytest.raises(ValueError, match="ne peut pas être vide"):
            segmenter.segment_notes([])
    
    def test_segment_notes_ascending_scale(self, segmenter):
        """Test segmentation d'une gamme ascendante."""
        # C4, D4, E4, F4, G4 (chacune 100ms avec 2 frames)
        frequencies = [261.63, 293.66, 329.63, 349.23, 392.00]
        pitch_frames = []
        
        for i, freq in enumerate(frequencies):
            # Chaque note : 2 frames espacées de 50ms = 100ms total (> 50ms min)
            pitch_frames.append(PitchFrame(time=i * 0.15, frequency=freq, confidence=0.9))
            pitch_frames.append(PitchFrame(time=i * 0.15 + 0.05, frequency=freq, confidence=0.9))
            pitch_frames.append(PitchFrame(time=i * 0.15 + 0.10, frequency=freq, confidence=0.9))
        
        notes = segmenter.segment_notes(pitch_frames)
        
        assert len(notes) == 5
        assert notes[0].midi_note == 60  # C4
        assert notes[1].midi_note == 62  # D4
        assert notes[2].midi_note == 64  # E4
        assert notes[3].midi_note == 65  # F4
        assert notes[4].midi_note == 67  # G4
    
    # --- Tests Benchmarks Performance ---
    
    def test_benchmark_segmentation_1000_frames(self, segmenter):
        """Benchmark segmentation sur 1000 frames."""
        import time
        
        # Générer 1000 frames avec notes variées
        # Chaque note dure au moins 3 frames (3 * 0.01s = 30ms mais la durée est end-start)
        # Pour avoir > 50ms, il faut plus d'espacement
        pitch_frames = []
        for i in range(1000):
            # Alterner entre quelques notes, chaque note durant ~100ms (10 frames)
            freq = [261.63, 329.63, 392.00, 523.25][i // 10 % 4]
            pitch_frames.append(PitchFrame(
                time=i * 0.01,
                frequency=freq,
                confidence=0.9
            ))
        
        start = time.time()
        notes = segmenter.segment_notes(pitch_frames)
        elapsed = time.time() - start
        
        print(f"\n[BENCHMARK] Segmentation 1000 frames: {elapsed:.3f}s")
        print(f"            Output: {len(notes)} notes")
        print(f"            Performance: {1000/elapsed:.0f} frames/sec")
        
        assert len(notes) > 0
        assert elapsed < 1.0  # Doit être rapide (< 1s pour 1000 frames)
    
    def test_benchmark_frequency_to_midi(self, segmenter):
        """Benchmark conversion fréquence → MIDI."""
        import time
        
        frequencies = np.random.uniform(100, 2000, 10000)
        
        start = time.time()
        for freq in frequencies:
            segmenter.frequency_to_midi(freq)
        elapsed = time.time() - start
        
        print(f"\n[BENCHMARK] 10000 conversions freq→MIDI: {elapsed:.3f}s")
        print(f"            Performance: {10000/elapsed:.0f} conversions/sec")
        
        assert elapsed < 0.5  # Doit être très rapide
    
    def test_benchmark_reference_frequency_impact(self):
        """Compare performance avec différentes références."""
        import time
        
        pitch_frames = [
            PitchFrame(time=i * 0.01, frequency=440.0 + i % 10, confidence=0.9)
            for i in range(500)
        ]
        
        results = []
        
        for ref_freq in [415.0, 440.0, 442.0]:
            segmenter = NoteSegmenter(reference_frequency=ref_freq)
            
            start = time.time()
            notes = segmenter.segment_notes(pitch_frames)
            elapsed = time.time() - start
            
            results.append({
                "ref_freq": ref_freq,
                "time": elapsed,
                "notes": len(notes)
            })
            
            print(f"\n[BENCHMARK] ref={ref_freq}Hz: {elapsed:.3f}s, {len(notes)} notes")
        
        # Performances doivent être similaires quelle que soit la référence
        times = [r["time"] for r in results]
        assert max(times) / min(times) < 1.5  # Pas plus de 50% différence


class TestIntegration:
    """Tests d'intégration NoteSegmenter avec autres modules."""
    
    def test_integration_with_pitch_detector(self):
        """Test intégration avec PitchDetector sur signal synthétique."""
        from src.pitch_detector import PitchDetector
        import numpy as np
        
        # Générer signal A4 (440 Hz) pendant 0.5s
        sr = 22050
        duration = 0.5
        t = np.linspace(0, duration, int(sr * duration))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)
        
        # Pitch detection
        detector = PitchDetector(model_capacity="tiny", confidence_threshold=0.5)
        pitch_frames = detector.detect_pitch(audio, sr)
        
        # Note segmentation
        segmenter = NoteSegmenter(min_note_duration=0.05)
        notes = segmenter.segment_notes(pitch_frames)
        
        # Vérifications
        assert len(notes) >= 1
        # La note dominante doit être A4 (MIDI 69) ou proche
        midi_notes = [n.midi_note for n in notes]
        assert 69 in midi_notes or 68 in midi_notes or 70 in midi_notes
    
    def test_print_notes_summary_empty(self, capsys):
        """Test affichage résumé avec liste vide."""
        segmenter = NoteSegmenter()
        segmenter.print_notes_summary([])
        
        captured = capsys.readouterr()
        assert "Aucune note" in captured.out
    
    def test_print_notes_summary_valid(self, capsys):
        """Test affichage résumé avec notes valides."""
        segmenter = NoteSegmenter()
        notes = [
            Note(midi_note=60, start_time=0.0, duration=0.5),
            Note(midi_note=64, start_time=0.5, duration=0.5),
            Note(midi_note=67, start_time=1.0, duration=0.5),
        ]
        
        segmenter.print_notes_summary(notes)
        
        captured = capsys.readouterr()
        assert "Total notes: 3" in captured.out
        assert "MIDI range" in captured.out
        assert "C4" in captured.out  # Note name pour MIDI 60
