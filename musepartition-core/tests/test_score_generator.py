"""
Tests pour ScoreGenerator
Génération de partitions musicales
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil
from typing import List

from src.types import QuantizedNote
from src.score_generator import ScoreGenerator

# Vérifier si music21 est disponible
try:
    import music21
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False


@pytest.fixture
def temp_output_dir():
    """Crée un répertoire temporaire pour les tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def simple_quantized_notes() -> List[QuantizedNote]:
    """Notes quantifiées simples pour tests."""
    return [
        QuantizedNote(midi_note=60, beat_position=0.0, duration_beats=1.0),   # C4, 1 beat
        QuantizedNote(midi_note=62, beat_position=1.0, duration_beats=1.0),   # D4, 1 beat
        QuantizedNote(midi_note=64, beat_position=2.0, duration_beats=1.0),   # E4, 1 beat
        QuantizedNote(midi_note=65, beat_position=3.0, duration_beats=1.0),   # F4, 1 beat
    ]


@pytest.fixture
def notes_with_gaps() -> List[QuantizedNote]:
    """Notes avec silences entre elles."""
    return [
        QuantizedNote(midi_note=60, beat_position=0.0, duration_beats=0.5),   # C4
        # Gap de 1.5 beats
        QuantizedNote(midi_note=64, beat_position=2.0, duration_beats=1.0),   # E4
        # Gap de 1.0 beat
        QuantizedNote(midi_note=67, beat_position=4.0, duration_beats=0.5),   # G4
    ]


@pytest.fixture
def scale_c_major() -> List[QuantizedNote]:
    """Gamme de Do majeur (C D E F G A B C)."""
    midi_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C4 à C5
    return [
        QuantizedNote(midi_note=midi, beat_position=i*1.0, duration_beats=1.0)
        for i, midi in enumerate(midi_notes)
    ]


class TestScoreGeneratorInit:
    """Tests d'initialisation."""
    
    def test_init_default(self):
        """Test initialisation avec paramètres par défaut."""
        generator = ScoreGenerator()
        
        assert generator.time_signature == "4/4"
        assert generator.key_signature == "C"
        assert generator.clef == "treble"
        assert generator.instrument_name == "Flute"
    
    def test_init_custom_time_signature(self):
        """Test signature temporelle personnalisée."""
        generator = ScoreGenerator(time_signature="3/4")
        assert generator.time_signature == "3/4"
    
    def test_init_custom_key(self):
        """Test tonalité personnalisée."""
        generator = ScoreGenerator(key_signature="D")
        assert generator.key_signature == "D"
        
        generator = ScoreGenerator(key_signature="Am")
        assert generator.key_signature == "Am"
    
    def test_init_custom_clef(self):
        """Test clefs différentes."""
        for clef in ["treble", "bass", "alto", "tenor"]:
            generator = ScoreGenerator(clef=clef)
            assert generator.clef == clef
    
    def test_init_custom_instrument(self):
        """Test instrument personnalisé."""
        generator = ScoreGenerator(instrument_name="Piano")
        assert generator.instrument_name == "Piano"


@pytest.mark.skipif(not MUSIC21_AVAILABLE, reason="music21 non installé")
class TestNotesToMusic21:
    """Tests de conversion notes → music21."""
    
    def test_empty_notes_raises_error(self):
        """Test avec liste vide."""
        generator = ScoreGenerator()
        
        with pytest.raises(ValueError, match="Liste de notes vide"):
            generator.notes_to_music21([], bpm=120.0)
    
    def test_simple_conversion(self, simple_quantized_notes):
        """Test conversion simple 4 notes."""
        generator = ScoreGenerator()
        score = generator.notes_to_music21(simple_quantized_notes, bpm=120.0)
        
        assert isinstance(score, music21.stream.Score)
        assert len(score.parts) == 1
        
        part = score.parts[0]
        assert part.partName == "Flute"
        
        # Vérifier notes (excluant clef, armure, tempo)
        notes = list(part.flatten().notes)
        assert len(notes) == 4
        assert notes[0].pitch.midi == 60  # C4
        assert notes[1].pitch.midi == 62  # D4
    
    def test_conversion_with_rests(self, notes_with_gaps):
        """Test insertion automatique des silences."""
        generator = ScoreGenerator()
        score = generator.notes_to_music21(notes_with_gaps, bpm=120.0, rest_threshold=0.25)
        
        part = score.parts[0]
        elements = list(part.flatten().notesAndRests)
        
        # Devrait avoir : note, rest, note, rest, note
        assert len(elements) == 5
        assert isinstance(elements[0], music21.note.Note)
        assert isinstance(elements[1], music21.note.Rest)
        assert isinstance(elements[2], music21.note.Note)
    
    def test_conversion_scale(self, scale_c_major):
        """Test gamme complète."""
        generator = ScoreGenerator()
        score = generator.notes_to_music21(scale_c_major, bpm=120.0)
        
        part = score.parts[0]
        notes = list(part.flatten().notes)
        
        assert len(notes) == 8
        assert notes[0].pitch.midi == 60  # C4
        assert notes[7].pitch.midi == 72  # C5
    
    def test_conversion_3_4_time(self, simple_quantized_notes):
        """Test en 3/4."""
        generator = ScoreGenerator(time_signature="3/4")
        
        # Adapter notes pour 3/4 (3 beats par mesure)
        notes_3_4 = [
            QuantizedNote(midi_note=60, beat_position=0.0, duration_beats=1.0),
            QuantizedNote(midi_note=62, beat_position=1.0, duration_beats=1.0),
            QuantizedNote(midi_note=64, beat_position=2.0, duration_beats=1.0),
        ]
        
        score = generator.notes_to_music21(notes_3_4, bpm=120.0)
        
        part = score.parts[0]
        measures = list(part.getElementsByClass(music21.stream.Measure))
        
        # 3 notes de 1 beat = 1 mesure de 3/4
        assert len(measures) >= 1
    
    def test_conversion_with_clef(self):
        """Test avec différentes clefs."""
        notes = [QuantizedNote(midi_note=48, beat_position=0.0, duration_beats=1.0)]  # C3
        
        # Clef de fa
        generator_bass = ScoreGenerator(clef="bass")
        score = generator_bass.notes_to_music21(notes, bpm=120.0)
        
        part = score.parts[0]
        clef = part.flatten().getElementsByClass(music21.clef.Clef)[0]
        assert isinstance(clef, music21.clef.BassClef)
    
    def test_conversion_with_key_signature(self):
        """Test avec armure."""
        notes = [QuantizedNote(midi_note=60, beat_position=0.0, duration_beats=1.0)]
        
        generator = ScoreGenerator(key_signature="D")
        score = generator.notes_to_music21(notes, bpm=120.0)
        
        part = score.parts[0]
        key = part.flatten().getElementsByClass(music21.key.Key)[0]
        assert key.sharps == 2  # D majeur = 2 dièses


@pytest.mark.skipif(not MUSIC21_AVAILABLE, reason="music21 non installé")
class TestExports:
    """Tests des exports."""
    
    def test_export_musicxml(self, simple_quantized_notes, temp_output_dir):
        """Test export MusicXML."""
        generator = ScoreGenerator()
        score = generator.notes_to_music21(simple_quantized_notes, bpm=120.0)
        
        output_path = Path(temp_output_dir) / "test.musicxml"
        result_path = generator.export_musicxml(score, str(output_path))
        
        assert result_path.exists()
        assert result_path.suffix == ".musicxml"
        assert result_path.stat().st_size > 0
    
    def test_export_midi(self, simple_quantized_notes, temp_output_dir):
        """Test export MIDI."""
        generator = ScoreGenerator()
        score = generator.notes_to_music21(simple_quantized_notes, bpm=120.0)
        
        output_path = Path(temp_output_dir) / "test.mid"
        result_path = generator.export_midi(score, str(output_path))
        
        assert result_path.exists()
        assert result_path.suffix == ".mid"
        assert result_path.stat().st_size > 0
    
    def test_export_pdf_without_musescore(self, simple_quantized_notes, temp_output_dir):
        """Test export PDF (peut échouer si MuseScore absent)."""
        generator = ScoreGenerator()
        score = generator.notes_to_music21(simple_quantized_notes, bpm=120.0)
        
        output_path = Path(temp_output_dir) / "test.pdf"
        
        try:
            result_path = generator.export_pdf(score, str(output_path))
            # Si succès, vérifier fichier
            assert result_path.exists()
            assert result_path.suffix == ".pdf"
        except RuntimeError as e:
            # Attendu si MuseScore non installé
            assert "MuseScore" in str(e)
    
    def test_export_creates_directory(self, simple_quantized_notes, temp_output_dir):
        """Test création automatique répertoire."""
        generator = ScoreGenerator()
        score = generator.notes_to_music21(simple_quantized_notes, bpm=120.0)
        
        nested_path = Path(temp_output_dir) / "subdir" / "test.musicxml"
        result_path = generator.export_musicxml(score, str(nested_path))
        
        assert result_path.exists()
        assert result_path.parent.name == "subdir"


@pytest.mark.skipif(not MUSIC21_AVAILABLE, reason="music21 non installé")
class TestGenerateScore:
    """Tests de génération complète."""
    
    def test_generate_score_basic(self, simple_quantized_notes, temp_output_dir):
        """Test génération partition complète."""
        generator = ScoreGenerator()
        
        paths = generator.generate_score(
            simple_quantized_notes,
            bpm=120.0,
            output_dir=temp_output_dir,
            base_filename="test_score"
        )
        
        # Vérifier retour
        assert 'musicxml' in paths
        assert 'midi' in paths
        assert 'pdf' in paths
        
        # Vérifier fichiers MusicXML et MIDI (toujours créés)
        assert paths['musicxml'].exists()
        assert paths['midi'].exists()
        
        # PDF peut être None si MuseScore absent
        if paths['pdf'] is not None:
            assert paths['pdf'].exists()
    
    def test_generate_score_with_metadata(self, simple_quantized_notes, temp_output_dir):
        """Test avec titre et compositeur personnalisés."""
        generator = ScoreGenerator()
        
        paths = generator.generate_score(
            simple_quantized_notes,
            bpm=120.0,
            output_dir=temp_output_dir,
            base_filename="my_song",
            title="My Beautiful Song",
            composer="John Doe"
        )
        
        # Vérifier que fichiers ont le bon nom de base
        assert paths['musicxml'].stem == "my_song"
        assert paths['midi'].stem == "my_song"
        
        # Vérifier metadata dans le score
        # (On pourrait recharger le MusicXML pour vérifier, mais complexe)
    
    def test_generate_score_scale(self, scale_c_major, temp_output_dir):
        """Test génération avec gamme complète."""
        generator = ScoreGenerator()
        
        paths = generator.generate_score(
            scale_c_major,
            bpm=120.0,
            output_dir=temp_output_dir,
            base_filename="c_major_scale",
            title="C Major Scale",
            composer="MusePartition"
        )
        
        assert paths['musicxml'].exists()
        assert paths['midi'].exists()


@pytest.mark.skipif(not MUSIC21_AVAILABLE, reason="music21 non installé")
class TestIntegration:
    """Tests d'intégration avec pipeline complet."""
    
    def test_full_pipeline_mock(self, temp_output_dir):
        """Test pipeline complet avec notes mockées simulant vraie sortie."""
        # Simuler sortie d'un quantizer réel
        # Tempo 120 BPM, mélodie simple
        quantized_notes = [
            # Mesure 1 (4 beats)
            QuantizedNote(midi_note=60, beat_position=0.0, duration_beats=1.0),   # C4
            QuantizedNote(midi_note=62, beat_position=1.0, duration_beats=1.0),   # D4
            QuantizedNote(midi_note=64, beat_position=2.0, duration_beats=1.0),   # E4
            QuantizedNote(midi_note=65, beat_position=3.0, duration_beats=1.0),   # F4
            # Mesure 2
            QuantizedNote(midi_note=67, beat_position=4.0, duration_beats=2.0),   # G4 (2 beats)
            QuantizedNote(midi_note=65, beat_position=6.0, duration_beats=1.0),   # F4
            QuantizedNote(midi_note=64, beat_position=7.0, duration_beats=1.0),   # E4
            # Mesure 3
            QuantizedNote(midi_note=62, beat_position=8.0, duration_beats=2.0),   # D4 (2 beats)
            QuantizedNote(midi_note=60, beat_position=10.0, duration_beats=2.0),  # C4 (2 beats)
        ]
        
        generator = ScoreGenerator(
            time_signature="4/4",
            key_signature="C",
            clef="treble",
            instrument_name="Flute"
        )
        
        paths = generator.generate_score(
            quantized_notes,
            bpm=120.0,
            output_dir=temp_output_dir,
            base_filename="integration_test",
            title="Integration Test Melody",
            composer="Test Suite"
        )
        
        # Vérifications
        assert paths['musicxml'].exists()
        assert paths['midi'].exists()
        
        # Vérifier contenu MusicXML (parsing basique)
        with open(paths['musicxml'], 'r') as f:
            xml_content = f.read()
            assert "Integration Test Melody" in xml_content
            assert "Test Suite" in xml_content
    
    def test_different_time_signatures(self, temp_output_dir):
        """Test avec différentes signatures temporelles."""
        test_cases = [
            ("4/4", 4),
            ("3/4", 3),
            ("6/8", 6),
            ("2/2", 2),
        ]
        
        for time_sig, beats_per_measure in test_cases:
            notes = [
                QuantizedNote(midi_note=60, beat_position=i*1.0, duration_beats=1.0)
                for i in range(beats_per_measure)
            ]
            
            generator = ScoreGenerator(time_signature=time_sig)
            
            paths = generator.generate_score(
                notes,
                bpm=120.0,
                output_dir=temp_output_dir,
                base_filename=f"test_{time_sig.replace('/', '_')}"
            )
            
            assert paths['musicxml'].exists()


# Benchmark (optionnel)
@pytest.mark.skipif(not MUSIC21_AVAILABLE, reason="music21 non installé")
class TestBenchmarks:
    """Tests de performance."""
    
    def test_benchmark_conversion_100_notes(self, temp_output_dir):
        """Benchmark conversion 100 notes."""
        import time
        
        # Créer 100 notes
        notes = [
            QuantizedNote(midi_note=60 + (i % 12), beat_position=i*0.5, duration_beats=0.5)
            for i in range(100)
        ]
        
        generator = ScoreGenerator()
        
        start = time.time()
        score = generator.notes_to_music21(notes, bpm=120.0)
        elapsed = time.time() - start
        
        print(f"\n[BENCHMARK] Conversion 100 notes: {elapsed:.3f}s")
        
        assert elapsed < 1.0  # Doit être rapide
    
    def test_benchmark_full_generation(self, temp_output_dir):
        """Benchmark génération complète (MusicXML + MIDI)."""
        import time
        
        notes = [
            QuantizedNote(midi_note=60 + (i % 12), beat_position=i*0.5, duration_beats=0.5)
            for i in range(50)
        ]
        
        generator = ScoreGenerator()
        
        start = time.time()
        paths = generator.generate_score(
            notes,
            bpm=120.0,
            output_dir=temp_output_dir,
            base_filename="benchmark"
        )
        elapsed = time.time() - start
        
        print(f"\n[BENCHMARK] Génération complète (50 notes): {elapsed:.3f}s")
        
        assert elapsed < 5.0  # Acceptable


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
