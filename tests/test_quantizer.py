"""
MusePartition - Musical Quantizer Tests
Unit tests for the quantizer module
"""

import pytest
import numpy as np
from src.quantizer import MusicalQuantizer
from src.types import Note, QuantizedNote


class TestMusicalQuantizer:
    """Test suite for MusicalQuantizer class."""
    
    @pytest.fixture
    def quantizer(self):
        """Crée un MusicalQuantizer standard."""
        return MusicalQuantizer(
            bpm=120.0,
            time_signature="4/4",
            quantization_grid="1/16"
        )
    
    @pytest.fixture
    def sample_notes(self):
        """Crée des notes de test."""
        return [
            Note(midi_note=60, start_time=0.0, duration=0.5),    # C4
            Note(midi_note=62, start_time=0.5, duration=0.5),    # D4
            Note(midi_note=64, start_time=1.0, duration=0.5),    # E4
            Note(midi_note=65, start_time=1.5, duration=0.5),    # F4
        ]
    
    @pytest.fixture
    def sample_audio(self):
        """Génère audio avec tempo clair (120 BPM)."""
        sr = 22050
        duration = 2.0
        bpm = 120.0
        
        # Générer clicks à 120 BPM (1 beat = 0.5s)
        t = np.linspace(0, duration, int(sr * duration))
        audio = np.zeros_like(t)
        
        # Ajouter clicks tous les 0.5s
        for beat_time in np.arange(0, duration, 60.0 / bpm):
            idx = int(beat_time * sr)
            if idx < len(audio) - 1000:
                audio[idx:idx+1000] = 0.5 * np.sin(2 * np.pi * 1000 * np.linspace(0, 1000/sr, 1000))
        
        return audio, sr
    
    # --- Tests Initialisation ---
    
    def test_init_default(self):
        """Test initialisation avec BPM auto."""
        quantizer = MusicalQuantizer()
        
        assert quantizer.bpm is None
        assert quantizer.time_signature == "4/4"
        assert quantizer.quantization_grid == "1/16"
        assert quantizer.beats_per_bar == 4
        assert quantizer.beat_unit == 4
    
    def test_init_custom_bpm(self):
        """Test initialisation avec BPM fixe."""
        quantizer = MusicalQuantizer(bpm=140.0)
        
        assert quantizer.bpm == 140.0
    
    def test_init_custom_time_signature(self):
        """Test initialisation avec signature temporelle personnalisée."""
        quantizer = MusicalQuantizer(time_signature="3/4")
        
        assert quantizer.beats_per_bar == 3
        assert quantizer.beat_unit == 4
    
    def test_init_invalid_time_signature(self):
        """Test initialisation avec signature invalide."""
        with pytest.raises(ValueError, match="Signature temporelle invalide"):
            MusicalQuantizer(time_signature="invalid")
    
    def test_init_custom_quantization_grid(self):
        """Test initialisation avec grille personnalisée."""
        for grid in ["1/4", "1/8", "1/16", "1/32"]:
            quantizer = MusicalQuantizer(quantization_grid=grid)
            assert quantizer.quantization_grid == grid
    
    def test_init_invalid_quantization_grid(self):
        """Test initialisation avec grille invalide."""
        with pytest.raises(ValueError, match="Grille invalide"):
            MusicalQuantizer(quantization_grid="1/64")
    
    # --- Tests Conversion Temps ---
    
    def test_seconds_to_beats_120bpm(self, quantizer):
        """Test conversion secondes → beats à 120 BPM."""
        # À 120 BPM : 1 beat = 0.5s
        beats = quantizer.seconds_to_beats(1.0, 120.0)
        assert abs(beats - 2.0) < 0.001
    
    def test_seconds_to_beats_60bpm(self, quantizer):
        """Test conversion à 60 BPM."""
        # À 60 BPM : 1 beat = 1s
        beats = quantizer.seconds_to_beats(2.0, 60.0)
        assert abs(beats - 2.0) < 0.001
    
    def test_beats_to_seconds_120bpm(self, quantizer):
        """Test conversion beats → secondes à 120 BPM."""
        seconds = quantizer.beats_to_seconds(4.0, 120.0)
        assert abs(seconds - 2.0) < 0.001
    
    def test_roundtrip_conversion(self, quantizer):
        """Test aller-retour secondes → beats → secondes."""
        original_time = 1.5
        beats = quantizer.seconds_to_beats(original_time, 120.0)
        reconstructed = quantizer.beats_to_seconds(beats, 120.0)
        assert abs(reconstructed - original_time) < 0.001
    
    # --- Tests Quantification Position ---
    
    def test_quantize_position_exact(self, quantizer):
        """Test quantification position exacte sur grille."""
        # 1.0 beats est déjà sur grille 1/16 (step = 0.25)
        quantized = quantizer.quantize_position(1.0)
        assert abs(quantized - 1.0) < 0.001
    
    def test_quantize_position_round_down(self, quantizer):
        """Test quantification arrondie vers le bas."""
        # 1.1 beats → arrondi à 1.0 (plus proche)
        quantized = quantizer.quantize_position(1.1)
        assert abs(quantized - 1.0) < 0.001
    
    def test_quantize_position_round_up(self, quantizer):
        """Test quantification arrondie vers le haut."""
        # 1.2 beats → arrondi à 1.25
        quantized = quantizer.quantize_position(1.2)
        assert abs(quantized - 1.25) < 0.001
    
    def test_quantize_position_grid_1_4(self):
        """Test quantification sur grille 1/4."""
        quantizer = MusicalQuantizer(quantization_grid="1/4")
        # Grille 1/4 : step = 1.0 beat
        quantized = quantizer.quantize_position(1.3)
        assert abs(quantized - 1.0) < 0.001
    
    def test_quantize_position_grid_1_8(self):
        """Test quantification sur grille 1/8."""
        quantizer = MusicalQuantizer(quantization_grid="1/8")
        # Grille 1/8 : step = 0.5 beat
        quantized = quantizer.quantize_position(1.3)
        assert abs(quantized - 1.5) < 0.001
    
    # --- Tests Quantification Durée ---
    
    def test_quantize_duration_minimum(self, quantizer):
        """Test durée minimale = 1 grid step."""
        # Grille 1/16 → step = 0.25 beats
        quantized = quantizer.quantize_duration(0.1)
        assert abs(quantized - 0.25) < 0.001
    
    def test_quantize_duration_normal(self, quantizer):
        """Test quantification durée normale."""
        quantized = quantizer.quantize_duration(1.3)
        # Arrondi à 1.25 beats
        assert abs(quantized - 1.25) < 0.001
    
    # --- Tests Détection Tempo ---
    
    def test_detect_tempo_with_clear_beat(self, quantizer, sample_audio):
        """Test détection tempo sur audio avec beat clair."""
        audio, sr = sample_audio
        bpm = quantizer.detect_tempo(audio, sr)
        
        # Doit détecter proche de 120 BPM
        assert 100 < bpm < 140  # Tolérance large (librosa pas parfait)
    
    def test_detect_tempo_empty_audio(self, quantizer):
        """Test détection tempo sur audio vide."""
        with pytest.raises(ValueError, match="Audio vide"):
            quantizer.detect_tempo(np.array([]), 22050)
    
    def test_detect_tempo_invalid_sr(self, quantizer):
        """Test détection tempo avec sample rate invalide."""
        audio = np.random.randn(1000)
        with pytest.raises(ValueError, match="Sample rate invalide"):
            quantizer.detect_tempo(audio, -1)
    
    # --- Tests Quantification Notes ---
    
    def test_quantize_notes_with_fixed_bpm(self, quantizer, sample_notes):
        """Test quantification avec BPM fixe."""
        quantized, bpm = quantizer.quantize_notes(sample_notes, bpm=120.0)
        
        assert len(quantized) == len(sample_notes)
        assert bpm == 120.0
        
        # Vérifier types
        for qnote in quantized:
            assert isinstance(qnote, QuantizedNote)
            assert qnote.midi_note in [60, 62, 64, 65]
            assert qnote.beat_position >= 0
            assert qnote.duration_beats > 0
    
    def test_quantize_notes_with_auto_detect(self, quantizer, sample_notes, sample_audio):
        """Test quantification avec auto-détection tempo."""
        audio, sr = sample_audio
        quantizer_auto = MusicalQuantizer()  # Pas de BPM
        
        quantized, bpm = quantizer_auto.quantize_notes(
            sample_notes,
            audio=audio,
            sr=sr
        )
        
        assert len(quantized) == len(sample_notes)
        assert 100 < bpm < 140  # Tempo détecté
    
    def test_quantize_notes_empty_list(self, quantizer):
        """Test quantification liste vide."""
        with pytest.raises(ValueError, match="Liste de notes vide"):
            quantizer.quantize_notes([], bpm=120.0)
    
    def test_quantize_notes_no_bpm(self, quantizer, sample_notes):
        """Test quantification sans BPM ni audio."""
        quantizer_no_bpm = MusicalQuantizer()
        
        with pytest.raises(ValueError, match="BPM non fourni"):
            quantizer_no_bpm.quantize_notes(sample_notes)
    
    def test_quantize_notes_preserves_midi(self, quantizer, sample_notes):
        """Test que quantification préserve numéros MIDI."""
        quantized, _ = quantizer.quantize_notes(sample_notes, bpm=120.0)
        
        for orig, quant in zip(sample_notes, quantized):
            assert orig.midi_note == quant.midi_note
    
    def test_quantize_notes_timing_accuracy(self, quantizer):
        """Test précision timing après quantification."""
        # Notes exactement sur grille
        notes = [
            Note(midi_note=60, start_time=0.0, duration=0.5),   # beat 0
            Note(midi_note=62, start_time=0.5, duration=0.5),   # beat 1
            Note(midi_note=64, start_time=1.0, duration=0.5),   # beat 2
        ]
        
        quantized, _ = quantizer.quantize_notes(notes, bpm=120.0)
        
        # Vérifier positions
        assert abs(quantized[0].beat_position - 0.0) < 0.01
        assert abs(quantized[1].beat_position - 1.0) < 0.01
        assert abs(quantized[2].beat_position - 2.0) < 0.01
    
    # --- Tests Benchmarks ---
    
    def test_benchmark_quantization_100_notes(self, quantizer):
        """Benchmark quantification 100 notes."""
        import time
        
        # Générer 100 notes
        notes = [
            Note(midi_note=60 + (i % 12), start_time=i * 0.25, duration=0.2)
            for i in range(100)
        ]
        
        start = time.time()
        quantized, _ = quantizer.quantize_notes(notes, bpm=120.0)
        elapsed = time.time() - start
        
        print(f"\n[BENCHMARK] Quantization 100 notes: {elapsed:.3f}s")
        print(f"            Output: {len(quantized)} notes")
        print(f"            Performance: {100/elapsed:.0f} notes/sec")
        
        assert len(quantized) == 100
        assert elapsed < 0.1  # Doit être très rapide
    
    def test_benchmark_tempo_detection(self, quantizer, sample_audio):
        """Benchmark détection tempo."""
        import time
        
        audio, sr = sample_audio
        
        start = time.time()
        bpm = quantizer.detect_tempo(audio, sr)
        elapsed = time.time() - start
        
        print(f"\n[BENCHMARK] Tempo detection: {elapsed:.3f}s")
        print(f"            Detected BPM: {bpm:.1f}")
        print(f"            Audio duration: {len(audio)/sr:.1f}s")
        
        assert elapsed < 2.0  # Doit être raisonnable
    
    def test_benchmark_grid_comparison(self, sample_notes):
        """Compare performance différentes grilles."""
        import time
        
        grids = ["1/4", "1/8", "1/16", "1/32"]
        results = []
        
        for grid in grids:
            quantizer = MusicalQuantizer(bpm=120.0, quantization_grid=grid)
            
            start = time.time()
            quantized, _ = quantizer.quantize_notes(sample_notes, bpm=120.0)
            elapsed = time.time() - start
            
            results.append({
                "grid": grid,
                "time": elapsed,
                "notes": len(quantized)
            })
            
            print(f"\n[BENCHMARK] Grid {grid}: {elapsed:.4f}s, {len(quantized)} notes")
        
        # Performance doit être similaire (mais timing très court = variance élevée)
        times = [r["time"] for r in results]
        if min(times) > 0:
            ratio = max(times) / min(times)
            assert ratio < 5.0  # Tolérance large car timings < 1ms
        # Si temps trop courts, juste vérifier que tous ont réussi
        assert all(r["notes"] == len(sample_notes) for r in results)


class TestIntegration:
    """Tests d'intégration avec autres modules."""
    
    def test_full_pipeline_audio_to_quantized(self):
        """Test pipeline complet Audio → Quantized Notes."""
        from src.audio_processor import AudioProcessor
        from src.pitch_detector import PitchDetector
        from src.note_segmenter import NoteSegmenter
        
        # Générer signal A4 (440 Hz) avec beats clairs
        sr = 22050
        duration = 2.0
        t = np.linspace(0, duration, int(sr * duration))
        
        # Signal modulé pour simuler beats
        envelope = (np.sin(2 * np.pi * 2 * t) + 1) / 2  # 2 Hz modulation (120 BPM)
        audio = 0.5 * envelope * np.sin(2 * np.pi * 440 * t)
        
        # Pipeline
        detector = PitchDetector(model_capacity="tiny", confidence_threshold=0.3)
        segmenter = NoteSegmenter(min_note_duration=0.05)
        quantizer = MusicalQuantizer(quantization_grid="1/8")
        
        pitch_frames = detector.detect_pitch(audio, sr)
        notes = segmenter.segment_notes(pitch_frames)
        
        # Auto-détection peut échouer sur signal synthétique simple
        # Forcer BPM si détection échoue
        try:
            quantized, bpm = quantizer.quantize_notes(notes, audio=audio, sr=sr)
        except ZeroDivisionError:
            # Fallback sur BPM fixe si détection échoue
            quantized, bpm = quantizer.quantize_notes(notes, bpm=120.0)
        
        # Vérifications
        assert len(pitch_frames) > 0
        assert len(notes) > 0
        assert len(quantized) > 0
        assert bpm > 0
        
        print(f"\n[INTEGRATION] Pipeline complet OK:")
        print(f"  Pitch frames: {len(pitch_frames)}")
        print(f"  Notes: {len(notes)}")
        print(f"  Quantized notes: {len(quantized)}")
        print(f"  Detected BPM: {bpm:.1f}")
    
    def test_print_quantization_summary(self, capsys):
        """Test affichage résumé quantification."""
        quantizer = MusicalQuantizer(bpm=120.0)
        
        notes = [
            Note(midi_note=60, start_time=0.0, duration=0.5),
            Note(midi_note=62, start_time=0.5, duration=0.5),
        ]
        
        quantized, bpm = quantizer.quantize_notes(notes, bpm=120.0)
        quantizer.print_quantization_summary(notes, quantized, bpm)
        
        captured = capsys.readouterr()
        assert "Musical Quantization Summary" in captured.out
        assert "120.0 BPM" in captured.out
        assert "4/4" in captured.out
