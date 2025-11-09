# Synthèse des API - MusePartition

**Version**: 0.0.0  
**Phase**: Phase 1 - PoC Python  
**Dernière mise à jour**: [À REMPLIR]

---

## Instructions

Ce fichier documente **uniquement** les signatures et comportements essentiels des API implémentées.  
Objectif : Permettre à une IA de reprendre le projet en comprenant rapidement les interfaces disponibles.

**Format par module**:
- Signature fonction/classe
- Description concise (1-2 phrases)
- Types input/output
- Exceptions levées
- Exemple usage minimal

---

## Module 1 : AudioProcessor

**Fichier**: `src/audio_processor.py`  
**Statut**: ✗ Non implémenté  
**Tests**: `tests/test_audio_processor.py`

### Classe `AudioProcessor`

#### `load_audio(file_path: str) -> Tuple[np.ndarray, int]`
Charge un fichier audio et retourne les données normalisées.

**Paramètres**:
- `file_path` (str): Chemin vers fichier audio (WAV/MP3/FLAC)

**Retourne**:
- `Tuple[np.ndarray, int]`: (audio_data, sample_rate)
  - `audio_data`: Array numpy shape (n_samples,) ou (n_channels, n_samples)
  - `sample_rate`: Fréquence échantillonnage (Hz)

**Exceptions**:
- `AudioLoadError`: Si fichier invalide ou non trouvé
- `ValueError`: Si format non supporté

**Exemple**:
```python
from src.audio_processor import AudioProcessor

processor = AudioProcessor()
audio, sr = processor.load_audio("input.wav")
print(f"Loaded {len(audio)} samples at {sr} Hz")
```

---

#### `normalize(audio: np.ndarray, method: str = "peak") -> np.ndarray`
Normalise l'amplitude audio.

**Paramètres**:
- `audio` (np.ndarray): Audio data
- `method` (str): Méthode normalisation ("peak" ou "rms")

**Retourne**:
- `np.ndarray`: Audio normalisé, amplitude dans [-1, 1]

**Exceptions**:
- `ValueError`: Si method invalide

**Exemple**:
```python
normalized = processor.normalize(audio, method="peak")
```

---

#### `to_mono(audio: np.ndarray) -> np.ndarray`
Convertit audio stéréo/multicanal en mono.

**Paramètres**:
- `audio` (np.ndarray): Audio data (1D ou 2D)

**Retourne**:
- `np.ndarray`: Audio mono (1D array)

**Exemple**:
```python
mono_audio = processor.to_mono(stereo_audio)
```

---

## Module 2 : PitchDetector

**Fichier**: `src/pitch_detector.py`  
**Statut**: ✗ Non implémenté  
**Tests**: `tests/test_pitch_detector.py`

### Classe `PitchDetector`

#### `__init__(model_size: str = "medium", confidence_threshold: float = 0.85)`
Initialise détecteur de pitch avec modèle CREPE.

**Paramètres**:
- `model_size` (str): Taille modèle ("tiny"|"small"|"medium"|"large"|"full")
- `confidence_threshold` (float): Seuil confiance [0, 1]

**Exemple**:
```python
from src.pitch_detector import PitchDetector

detector = PitchDetector(model_size="medium", confidence_threshold=0.85)
```

---

#### `detect_pitch(audio: np.ndarray, sr: int) -> List[PitchFrame]`
Détecte fréquences fondamentales dans audio.

**Paramètres**:
- `audio` (np.ndarray): Audio mono
- `sr` (int): Sample rate

**Retourne**:
- `List[PitchFrame]`: Liste frames pitch
  - `PitchFrame`: NamedTuple(time: float, frequency: float, confidence: float)

**Exemple**:
```python
pitch_data = detector.detect_pitch(audio, sr=22050)
for frame in pitch_data:
    print(f"t={frame.time:.2f}s: {frame.frequency:.2f}Hz (conf={frame.confidence:.2f})")
```

---

## Module 3 : NoteSegmenter

**Fichier**: `src/note_segmenter.py`  
**Statut**: ✗ Non implémenté  
**Tests**: `tests/test_note_segmenter.py`

### Classe `NoteSegmenter`

#### `__init__(min_note_duration: float = 0.05)`
Initialise segmenteur de notes.

**Paramètres**:
- `min_note_duration` (float): Durée minimale note (secondes)

---

#### `frequency_to_midi(frequency: float) -> int`
Convertit fréquence Hz en numéro MIDI.

**Paramètres**:
- `frequency` (float): Fréquence en Hz

**Retourne**:
- `int`: Numéro MIDI [0, 127] (60 = C4 = 261.63 Hz)

**Exemple**:
```python
from src.note_segmenter import NoteSegmenter

segmenter = NoteSegmenter()
midi_note = segmenter.frequency_to_midi(440.0)  # A4 = 69
```

---

#### `segment_notes(pitch_data: List[PitchFrame]) -> List[Note]`
Segmente données pitch en notes discrètes.

**Paramètres**:
- `pitch_data` (List[PitchFrame]): Sortie de PitchDetector

**Retourne**:
- `List[Note]`: Notes segmentées
  - `Note`: NamedTuple(midi_note: int, start_time: float, duration: float)

**Exemple**:
```python
notes = segmenter.segment_notes(pitch_data)
for note in notes:
    print(f"Note {note.midi_note} at {note.start_time:.2f}s, dur={note.duration:.2f}s")
```

---

## Module 4 : MusicalQuantizer

**Fichier**: `src/quantizer.py`  
**Statut**: ✗ Non implémenté  
**Tests**: `tests/test_quantizer.py`

### Classe `MusicalQuantizer`

#### `__init__(bpm: Optional[float] = None, quantization_grid: str = "1/16")`
Initialise quantizer musical.

**Paramètres**:
- `bpm` (Optional[float]): Tempo fixe ou None (auto-détection)
- `quantization_grid` (str): Grille rhythmique ("1/4"|"1/8"|"1/16"|"1/32")

---

#### `detect_tempo(audio: np.ndarray, sr: int) -> float`
Détecte tempo automatiquement.

**Paramètres**:
- `audio` (np.ndarray): Audio mono
- `sr` (int): Sample rate

**Retourne**:
- `float`: BPM détecté

**Exemple**:
```python
from src.quantizer import MusicalQuantizer

quantizer = MusicalQuantizer()
bpm = quantizer.detect_tempo(audio, sr=22050)
print(f"Tempo: {bpm:.1f} BPM")
```

---

#### `quantize_notes(notes: List[Note], bpm: float) -> List[QuantizedNote]`
Quantifie notes sur grille rythmique.

**Paramètres**:
- `notes` (List[Note]): Notes brutes
- `bpm` (float): Tempo cible

**Retourne**:
- `List[QuantizedNote]`: Notes quantifiées
  - `QuantizedNote`: NamedTuple(midi_note: int, beat_position: float, duration_beats: float)

**Exemple**:
```python
quantizer = MusicalQuantizer(bpm=120, quantization_grid="1/16")
quantized = quantizer.quantize_notes(notes, bpm=120)
```

---

## Module 5 : ScoreGenerator

**Fichier**: `src/score_generator.py`  
**Statut**: ✗ Non implémenté  
**Tests**: `tests/test_score_generator.py`

### Classe `ScoreGenerator`

#### `__init__(time_signature: str = "4/4", key_signature: str = "C")`
Initialise générateur de partition.

**Paramètres**:
- `time_signature` (str): Signature temporelle (ex: "4/4", "3/4")
- `key_signature` (str): Tonalité (ex: "C", "G", "F#m")

---

#### `notes_to_music21(notes: List[QuantizedNote], bpm: float) -> music21.stream.Stream`
Convertit notes en objet music21.

**Paramètres**:
- `notes` (List[QuantizedNote]): Notes quantifiées
- `bpm` (float): Tempo

**Retourne**:
- `music21.stream.Stream`: Partition music21

**Exemple**:
```python
from src.score_generator import ScoreGenerator

generator = ScoreGenerator(time_signature="4/4", key_signature="C")
stream = generator.notes_to_music21(quantized_notes, bpm=120)
```

---

#### `export_musicxml(stream: music21.stream.Stream, output_path: str) -> None`
Exporte partition en MusicXML.

**Paramètres**:
- `stream` (music21.stream.Stream): Partition
- `output_path` (str): Chemin fichier sortie (.xml ou .mxl)

**Exemple**:
```python
generator.export_musicxml(stream, "output/score.musicxml")
```

---

#### `export_pdf(stream: music21.stream.Stream, output_path: str) -> None`
Génère partition PDF via MuseScore/Lilypond.

**Paramètres**:
- `stream` (music21.stream.Stream): Partition
- `output_path` (str): Chemin fichier sortie (.pdf)

**Exceptions**:
- `RuntimeError`: Si MuseScore/Lilypond non installé

**Exemple**:
```python
generator.export_pdf(stream, "output/score.pdf")
```

---

#### `export_midi(stream: music21.stream.Stream, output_path: str) -> None`
Exporte partition en MIDI.

**Paramètres**:
- `stream` (music21.stream.Stream): Partition
- `output_path` (str): Chemin fichier sortie (.mid)

**Exemple**:
```python
generator.export_midi(stream, "output/score.mid")
```

---

## Pipeline : TranscriptionPipeline

**Fichier**: `src/transcription_pipeline.py`  
**Statut**: ✗ Non implémenté  
**Tests**: `tests/test_e2e.py`

### Classe `TranscriptionPipeline`

#### `__init__(config: dict)`
Initialise pipeline complet.

**Paramètres**:
- `config` (dict): Configuration (voir `config.example.json`)

**Exemple config**:
```json
{
  "audio": {
    "sample_rate": 22050,
    "normalization": "peak"
  },
  "pitch_detector": {
    "model": "medium",
    "confidence_threshold": 0.85
  },
  "quantizer": {
    "bpm": null,
    "quantization_grid": "1/16"
  },
  "score": {
    "time_signature": "4/4",
    "key_signature": "C"
  }
}
```

---

#### `transcribe(audio_file: str, output_dir: str) -> TranscriptionResult`
Lance transcription complète audio → partition.

**Paramètres**:
- `audio_file` (str): Chemin fichier audio
- `output_dir` (str): Répertoire sorties

**Retourne**:
- `TranscriptionResult`: Objet résultats
  - Attributs: `pdf_path`, `musicxml_path`, `midi_path`, `bpm`, `num_notes`, `processing_time`

**Exemple**:
```python
from src.transcription_pipeline import TranscriptionPipeline
import json

with open("config.json") as f:
    config = json.load(f)

pipeline = TranscriptionPipeline(config)
result = pipeline.transcribe("input/flute.wav", "output/")

print(f"Transcription terminée en {result.processing_time:.2f}s")
print(f"PDF: {result.pdf_path}")
print(f"MusicXML: {result.musicxml_path}")
print(f"MIDI: {result.midi_path}")
print(f"Tempo détecté: {result.bpm:.1f} BPM")
print(f"Notes détectées: {result.num_notes}")
```

---

## CLI : Interface Ligne de Commande

**Fichier**: `src/cli.py`  
**Statut**: ✗ Non implémenté

### Commande Principale

```bash
python -m src.cli transcribe INPUT_FILE [OPTIONS]
```

**Arguments**:
- `INPUT_FILE` (str): Fichier audio à transcrire

**Options**:
- `--output DIR`, `-o DIR`: Répertoire sortie (défaut: `./output`)
- `--config FILE`, `-c FILE`: Fichier config JSON (défaut: paramètres par défaut)
- `--bpm FLOAT`: Forcer tempo (override auto-détection)
- `--time-signature STR`: Signature temporelle (ex: "3/4")
- `--key STR`: Tonalité (ex: "Am")
- `--verbose`, `-v`: Mode verbeux

**Exemples**:
```bash
# Basique
python -m src.cli transcribe recording.wav

# Avec config custom
python -m src.cli transcribe recording.wav --config my_config.json --output ./results

# Override tempo
python -m src.cli transcribe recording.wav --bpm 120 --time-signature 3/4

# Mode verbeux
python -m src.cli transcribe recording.wav -v
```

---

## Types Personnalisés (src/types.py)

**Statut**: ✗ À créer

```python
from typing import NamedTuple

class PitchFrame(NamedTuple):
    time: float          # Timestamp (secondes)
    frequency: float     # Fréquence Hz
    confidence: float    # Confiance [0, 1]

class Note(NamedTuple):
    midi_note: int       # Numéro MIDI [0, 127]
    start_time: float    # Début (secondes)
    duration: float      # Durée (secondes)

class QuantizedNote(NamedTuple):
    midi_note: int       # Numéro MIDI
    beat_position: float # Position en beats
    duration_beats: float # Durée en beats

class TranscriptionResult(NamedTuple):
    pdf_path: str
    musicxml_path: str
    midi_path: str
    bpm: float
    num_notes: int
    processing_time: float
```

---

## Dépendances Python

**Fichier**: `requirements.txt`  
**Statut**: ✗ À créer

```
# Audio processing
librosa>=0.10.0
soundfile>=0.12.0
audioread>=3.0.0

# Pitch detection
crepe>=0.0.13
tensorflow>=2.13.0

# Music notation
music21>=9.1.0

# CLI & utilities
rich>=13.0.0
numpy>=1.24.0
scipy>=1.10.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
```

---

## Notes de Compatibilité

### Dépendances Système
- **MuseScore 3+** ou **Lilypond**: Requis pour export PDF
- **ffmpeg**: Requis pour support MP3/autres formats via audioread

### Limitations Connues
*Aucune - projet non démarré*

---

## Changelog API

### v0.0.0 (2025-11-09)
- Documentation initiale API
- Définition interfaces modules 1-5
- Définition pipeline et CLI

---

**Instructions**:
- Mettre à jour après chaque implémentation de fonction
- Ajouter exemples réels après tests validés
- Documenter exceptions réellement levées
- Marquer statut ✓ quand module complet et testé
