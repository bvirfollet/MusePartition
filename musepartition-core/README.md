# MusePartition Core

**Audio to Music Score Transcription Engine**

Core package providing the complete transcription pipeline from audio files to musical notation.

## Features

- 🎵 **Audio Processing**: Load, normalize, preprocess audio files
- 🎼 **Pitch Detection**: High-precision fundamental frequency detection (CREPE)
- 🎹 **Note Segmentation**: Convert pitch data to discrete musical notes
- ⏱️ **Musical Quantization**: Rhythm quantization and tempo detection
- 📄 **Score Generation**: Export to MusicXML, MIDI, and PDF

## Installation

```bash
pip install musepartition-core
```

### Development Installation

```bash
git clone https://github.com/bertrand/musepartition
cd musepartition-core
pip install -e .[dev]
```

## Quick Start

```python
from musepartition_core import TranscriptionPipeline

# Create pipeline with default configuration
pipeline = TranscriptionPipeline()

# Transcribe audio file
result = pipeline.transcribe("flute_recording.wav", "output/")

# Access results
print(f"MusicXML: {result.musicxml_path}")
print(f"MIDI: {result.midi_path}")
print(f"PDF: {result.pdf_path}")
print(f"Tempo: {result.bpm:.1f} BPM")
print(f"Notes: {result.num_notes}")
```

## Configuration

```python
config = {
    "pitch_detection": {
        "model_capacity": "medium",
        "confidence_threshold": 0.6
    },
    "quantization": {
        "bpm": 120.0,  # Force tempo (None for auto-detection)
        "time_signature": "4/4",
        "quantization_grid": "1/16"
    },
    "score_generation": {
        "title": "My Song",
        "composer": "Composer Name",
        "key_signature": "C",
        "clef": "treble"
    }
}

pipeline = TranscriptionPipeline(config)
result = pipeline.transcribe("audio.wav", "output/")
```

## Modules

### AudioProcessor
- Load audio files (WAV, MP3, FLAC, M4A)
- Preprocessing (normalization, mono conversion)
- Resampling

### PitchDetector
- CREPE-based pitch detection
- Configurable model size and confidence threshold
- High temporal resolution

### NoteSegmenter
- Frequency to MIDI conversion
- Note onset/offset detection
- Adjustable reference frequency (A4 = 440Hz, 442Hz, 415Hz)

### MusicalQuantizer
- Automatic tempo detection
- Rhythm quantization (1/4, 1/8, 1/16, 1/32, triplets)
- Multiple time signatures support

### ScoreGenerator
- music21-based score generation
- Export to MusicXML, MIDI, PDF
- Automatic rest insertion
- Configurable metadata

## Testing

```bash
pytest tests/ -v
```

## License

MIT License

## Version

1.0.0 (Phase 1 Complete)
