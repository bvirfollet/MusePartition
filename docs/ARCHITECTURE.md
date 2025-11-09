# MusePartition - Architecture du Projet

## Vue d'ensemble

**Objectif**: Système de transcription audio → partition musicale  
**Approche progressive**: Client/Serveur → Client lourd Android  
**Cibles musicales**: Flûte (monophonie) → Piano (polyphonie)

---

## Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE FINALE (Android)                    │
│  ┌────────────────┐                   ┌──────────────────┐  │
│  │  Client Lourd  │                   │  Client Léger    │  │
│  │   Android      │◄─────────────────►│  Android         │  │
│  │  (traitement   │                   │  + Backend PC    │  │
│  │   embarqué)    │                   │                  │  │
│  └────────────────┘                   └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
                    ┌───────┴────────┐
                    │  PHASE 1 (PoC) │
                    │  Python CLI    │
                    │  Fichier audio │
                    └────────────────┘
```

---

## PHASE 1 : PoC Python (Fichier Audio → Partition)

### Objectifs
- Valider la chaîne de traitement complète
- Entrée : Fichier audio WAV/MP3 (flûte monophonique)
- Sortie : Partition PDF + MusicXML + MIDI
- Environnement : CLI Python sur PC

### Architecture Technique

```
Input Audio File
       ↓
┌──────────────────────────────────────────┐
│  Module 1 : Audio Processing             │
│  - Chargement audio (librosa)            │
│  - Preprocessing (normalisation, mono)   │
│  - Segmentation en chunks                │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│  Module 2 : Pitch Detection              │
│  - Détection fréquence fondamentale      │
│  - Algorithme : CREPE (model="medium")   │
│  - Filtrage par confidence (threshold)   │
│  - Sortie : (timestamp, frequency, conf) │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│  Module 3 : Note Segmentation            │
│  - Conversion Hz → note MIDI             │
│  - Détection onset/offset                │
│  - Filtrage silences                     │
│  - Sortie : (note, start, duration)      │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│  Module 4 : Musical Quantization         │
│  - Détection tempo (BPM)                 │
│  - Quantization rythmique                │
│  - Gestion mesures/temps                 │
│  - Sortie : notes quantifiées            │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│  Module 5 : Score Generation             │
│  - Conversion vers Music21 Stream        │
│  - Export MusicXML                       │
│  - Rendu PDF (via MuseScore/Lilypond)   │
│  - Export MIDI                           │
└──────────────────────────────────────────┘
       ↓
Output: PDF, MusicXML, MIDI

┌─────────────────────────────────────────────────┐
│  Module Utils (Support - transversal)           │
│  ──────────────────────────────────────────────  │
│  • DebugTracer : Logging structuré (.log/.json) │
│  • IntermediateStorage : Sauvegarde étapes      │
│  • Fonctions utilitaires (format, stats)        │
│  ──────────────────────────────────────────────  │
│  Utilisé par tous les modules pour debug/trace  │
└─────────────────────────────────────────────────┘
```

### Stack Technologique (Phase 1)

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| Langage | Python 3.10+ | Écosystème riche pour traitement audio |
| Audio I/O | librosa, soundfile | Standard industrie, bien documenté |
| Pitch Detection | CREPE (TensorFlow) | Précision >98% sur instruments mélodiques |
| Music Notation | music21 | API complète, export multi-formats |
| Tempo Detection | librosa.beat | Robuste pour musique occidentale |
| CLI | argparse + rich | Interface utilisateur claire |

### API Principales (Phase 1)

```python
# Module 1: audio_processor.py
class AudioProcessor:
    def load_audio(file_path: str) -> Tuple[np.ndarray, int]
    def normalize(audio: np.ndarray) -> np.ndarray
    def to_mono(audio: np.ndarray) -> np.ndarray

# Module 2: pitch_detector.py
class PitchDetector:
    def __init__(model: str = "crepe")
    def detect_pitch(audio: np.ndarray, sr: int) -> List[PitchFrame]
        # PitchFrame = (time: float, frequency: float, confidence: float)

# Module 3: note_segmenter.py
class NoteSegmenter:
    def frequency_to_midi(frequency: float) -> int
    def segment_notes(pitch_data: List[PitchFrame]) -> List[Note]
        # Note = (midi_note: int, start_time: float, duration: float)

# Module 4: quantizer.py
class MusicalQuantizer:
    def __init__(bpm: Optional[float] = None)
    def detect_tempo(audio: np.ndarray, sr: int) -> float
    def quantize_notes(notes: List[Note], bpm: float) -> List[QuantizedNote]
        # QuantizedNote = (midi_note: int, beat_position: float, duration_beats: float)

# Module 5: score_generator.py
class ScoreGenerator:
    def notes_to_music21(notes: List[QuantizedNote]) -> music21.stream.Stream
    def export_musicxml(stream: music21.stream.Stream, output_path: str)
    def export_pdf(stream: music21.stream.Stream, output_path: str)
    def export_midi(stream: music21.stream.Stream, output_path: str)

# Module Utils: utils.py (Support)
class DebugTracer:
    def __init__(output_dir: str = "output/debug", enabled: bool = True)
    def log_step(step_name: str, metadata: Dict[str, Any]) -> None
    def get_log_path() -> Optional[Path]

class IntermediateStorage:
    def __init__(output_dir: str = "output/intermediate")
    def save_audio(audio: Any, sample_rate: int, filename: str) -> Path
    def save_pitch_data(pitch_frames: List[PitchFrame], filename: str) -> Path
    def save_notes(notes: List[Note], filename: str) -> Path
    def save_quantized_notes(quantized_notes: List[QuantizedNote], bpm: float, filename: str) -> Path
    def load_audio(filename: str) -> Dict[str, Any]
    def load_pitch_data(filename: str) -> Dict[str, Any]
    def list_saved_files() -> List[Path]

# Fonctions utilitaires
def format_duration(seconds: float) -> str  # "2m 34s"
def format_frequency(frequency: float) -> str  # "440.0 Hz (A4)"
def print_summary_stats(pitch_frames: List[PitchFrame]) -> None

# Main Pipeline
class TranscriptionPipeline:
    def __init__(config: dict)
    def transcribe(audio_file: str, output_dir: str) -> TranscriptionResult
```

### Étapes de Développement (Phase 1)

#### **SESSION 1 : Setup & Module 1 (Audio Processing)**
- Environnement : `requirements.txt`, structure projet
- Tests : chargement fichiers audio variés
- **Livrables** : 
  - `audio_processor.py`
  - `tests/test_audio_processor.py`
  - Documentation API Module 1

#### **SESSION 2 : Module 2 (Pitch Detection) + Utils**
- Intégration CREPE avec optimisations (model_capacity="medium", confidence filtering)
- Benchmark précision sur enregistrements flûte
- **Module Utils ajouté** :
  - DebugTracer : Traçage et logging structuré
  - IntermediateStorage : Sauvegarde résultats intermédiaires
  - Fonctions utilitaires (format_duration, format_frequency, stats)
- **Livrables** :
  - `pitch_detector.py` (amélioré avec filtrage confidence)
  - `utils.py` (nouveau module support)
  - `tests/test_pitch_detector.py` (avec 5 benchmarks performance)
  - `tests/test_utils.py` (25+ tests)
  - Dataset test (3 fichiers flûte - optionnel)
  - Documentation API Module 2 + Utils

#### **SESSION 3 : Module 3 (Note Segmentation)**
- Algorithme onset/offset detection
- Conversion fréquence → MIDI
- **Livrables** :
  - `note_segmenter.py`
  - `tests/test_note_segmenter.py`
  - Documentation API Module 3

#### **SESSION 4 : Module 4 (Musical Quantization)**
- Détection tempo
- Quantization rythmique configurable
- **Livrables** :
  - `quantizer.py`
  - `tests/test_quantizer.py`
  - Documentation API Module 4

#### **SESSION 5 : Module 5 (Score Generation)**
- Intégration music21
- Export multi-formats
- Configuration MuseScore/Lilypond
- **Livrables** :
  - `score_generator.py`
  - `tests/test_score_generator.py`
  - Documentation API Module 5

#### **SESSION 6 : Pipeline & CLI**
- Orchestration complète
- Interface CLI avec rich
- Configuration JSON
- **Livrables** :
  - `transcription_pipeline.py`
  - `cli.py`
  - `config.example.json`
  - Documentation utilisateur

#### **SESSION 7 : Tests End-to-End & Optimisation**
- Tests intégration complète
- Tuning paramètres (seuils, quantization)
- Benchmarks qualité/performance
- **Livrables** :
  - `tests/test_e2e.py`
  - Rapport benchmarks
  - Guide de tuning

#### **SESSION 8 : Documentation & Package**
- README complet
- Guide contribution
- Exemples d'utilisation
- Package PyPI (optionnel)
- **Livrables** :
  - `README.md`
  - `CONTRIBUTING.md`
  - `docs/` (Sphinx ou MkDocs)
  - Release v0.1.0

---

## Estimation Sessions PoC (Phase 1)

| Étape | Sessions | Durée estimée | Complexité |
|-------|----------|---------------|------------|
| Setup & Audio Processing | 1 | 2h | Faible |
| Pitch Detection | 1 | 3h | Moyenne |
| Note Segmentation | 1 | 3h | Moyenne |
| Quantization | 1 | 3h | Élevée |
| Score Generation | 1 | 2h | Faible |
| Pipeline & CLI | 1 | 2h | Faible |
| Tests E2E & Tuning | 1 | 4h | Élevée |
| Documentation | 1 | 2h | Faible |
| **TOTAL** | **8 sessions** | **~21h** | - |

**Note**: Ces estimations supposent des sessions de travail focalisées. Ajuster selon disponibilité et complexité rencontrée.

---

## Protocole de Reprise de Session

### Fichiers Essentiels de Contexte
1. **`ARCHITECTURE.md`** (ce fichier) : Vision globale
2. **`SESSION_LOG.md`** : Journal des sessions (créé en Session 1)
3. **`CURRENT_STATUS.md`** : État actuel du développement
4. **`API_SUMMARY.md`** : Synthèse des API implémentées

### Démarrage dans Nouveau Contexte
```bash
# 1. Cloner/récupérer le projet
git clone <repo> && cd MusePartition

# 2. Lire les fichiers de contexte
cat CURRENT_STATUS.md  # État actuel
cat SESSION_LOG.md     # Historique

# 3. Vérifier les fichiers disponibles
ls -R src/ tests/

# 4. Installer dépendances
pip install -r requirements.txt

# 5. Lancer tests pour valider état
pytest tests/
```

### Format `CURRENT_STATUS.md`
```markdown
# État Actuel du Projet

**Date**: YYYY-MM-DD
**Session complétée**: N/8
**Prochaine étape**: [Description]

## Modules Implémentés
- [x] Module 1 : Audio Processing
- [ ] Module 2 : Pitch Detection
- [ ] ...

## Fichiers Créés
- src/audio_processor.py (v1.0)
- tests/test_audio_processor.py

## Tests Passants
- ✓ test_load_wav
- ✓ test_normalize
- ✗ test_stereo_to_mono (bug connu)

## Décisions Techniques
- Choix CREPE over pYIN (meilleure précision flûte)
- Sample rate standardisé : 22050 Hz

## Prochaines Actions
1. Implémenter PitchDetector.detect_pitch()
2. Créer dataset test (3 fichiers flûte)
```

### Format `API_SUMMARY.md`
```markdown
# Synthèse des API Implémentées

## Module 1: AudioProcessor
**Fichier**: `src/audio_processor.py`

### `load_audio(file_path: str) -> Tuple[np.ndarray, int]`
Charge un fichier audio.
- **Input**: Chemin fichier (WAV/MP3/FLAC)
- **Output**: (audio_data, sample_rate)
- **Exceptions**: `AudioLoadError` si fichier invalide

### `normalize(audio: np.ndarray) -> np.ndarray`
Normalise amplitude [-1, 1].
- **Input**: Audio numpy array
- **Output**: Audio normalisé

[...]
```

---

## PHASE 2 : Backend + Client Léger Android

### Architecture
```
┌─────────────────┐          REST/WebSocket         ┌──────────────┐
│  Android Client │◄────────────────────────────────►│  Backend PC  │
│  (UI + Capture) │          (JSON)                 │  (Python)    │
└─────────────────┘                                  └──────────────┘
       │                                                     │
       │ Audio Stream                                       │ Processing
       │ (base64/chunks)                                    │ Pipeline
       │                                                     │
       └─────────────► Microphone                          Storage
```

### Stack Technique
- **Backend**: FastAPI + WebSocket
- **Android**: Kotlin + Jetpack Compose
- **Communication**: JSON over WebSocket
- **Audio**: Android AudioRecord → PCM chunks

### API REST/WebSocket (haut niveau)
```
POST   /api/transcribe/upload     # Upload fichier
POST   /api/transcribe/stream     # Stream temps réel
GET    /api/transcribe/{id}       # État transcription
GET    /api/score/{id}/pdf        # Télécharger PDF
GET    /api/score/{id}/musicxml   # Télécharger MusicXML
WS     /ws/live                   # WebSocket live
```

*Détails Phase 2 à documenter après Phase 1 validée.*

---

## PHASE 3 : Client Lourd Android

### Architecture
```
┌──────────────────────────────────────────┐
│        Application Android               │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Audio Capture                     │ │
│  └──────────┬─────────────────────────┘ │
│             ↓                            │
│  ┌────────────────────────────────────┐ │
│  │  Native Processing (C++)           │ │
│  │  - CREPE (TensorFlow Lite)         │ │
│  │  - Note Segmentation               │ │
│  └──────────┬─────────────────────────┘ │
│             ↓                            │
│  ┌────────────────────────────────────┐ │
│  │  Score Rendering                   │ │
│  │  - VexFlow Android / Custom View   │ │
│  └────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

### Défis Techniques
- Port CREPE → TensorFlow Lite
- Optimisation CPU/mémoire mobile
- Rendu partition performant
- Gestion permissions audio

*Détails Phase 3 à documenter après Phase 2 validée.*

---

## Gestion des Dépendances entre Phases

| Phase | Prérequis | Validation |
|-------|-----------|------------|
| Phase 1 (PoC) | Aucun | Tests E2E passants, qualité acceptable sur flûte |
| Phase 2 (Client/Serveur) | Phase 1 validée | Latence <2s, interface Android fonctionnelle |
| Phase 3 (Client Lourd) | Phase 2 validée | Traitement <500ms sur device, autonome |

---

## Métriques de Succès

### Phase 1 (PoC)
- ✓ Détection notes correctes >90% (flûte simple)
- ✓ Rythme reconnaissable (erreur <10% sur durées)
- ✓ Export PDF lisible musicalement
- ✓ Temps traitement <10s pour 30s audio

### Phases 2 & 3
*À définir après Phase 1.*

---

## Conventions de Code

### Python
- **Style**: PEP 8 + Black formatter
- **Type hints**: Obligatoires
- **Docstrings**: Google style
- **Tests**: pytest, coverage >80%

### Structure Projet (Phase 1)
```
MusePartition/
├── ARCHITECTURE.md          # Ce fichier
├── README.md
├── requirements.txt
├── setup.py
├── config.example.json
├── src/
│   ├── __init__.py
│   ├── audio_processor.py
│   ├── pitch_detector.py
│   ├── note_segmenter.py
│   ├── quantizer.py
│   ├── score_generator.py
│   ├── transcription_pipeline.py
│   └── cli.py
├── tests/
│   ├── __init__.py
│   ├── test_audio_processor.py
│   ├── test_pitch_detector.py
│   ├── test_note_segmenter.py
│   ├── test_quantizer.py
│   ├── test_score_generator.py
│   └── test_e2e.py
├── data/
│   ├── samples/             # Fichiers test
│   └── models/              # Modèles CREPE
├── docs/
│   ├── SESSION_LOG.md
│   ├── CURRENT_STATUS.md
│   └── API_SUMMARY.md
└── output/                  # Résultats transcriptions
```

---

## Notes Importantes

1. **Documentation Continue**: Chaque session doit mettre à jour `SESSION_LOG.md` et `CURRENT_STATUS.md`
2. **Tests First**: TDD encouragé, surtout pour modules critiques (pitch, quantization)
3. **Modularité**: Chaque module doit être testable indépendamment
4. **Configuration**: Paramètres exposés via JSON (seuils, BPM, etc.)
5. **Réversibilité**: Possibilité de fournir fichiers intermédiaires (pitch data, notes pré-quantization)

---

## Roadmap Visuelle

```
Phase 1 (8 sessions)
├─ S1: Audio Processing ────────────┐
├─ S2: Pitch Detection              │
├─ S3: Note Segmentation            │── PoC Fonctionnel
├─ S4: Quantization                 │
├─ S5: Score Generation             │
├─ S6: Pipeline & CLI               │
├─ S7: Tests & Tuning ──────────────┘
└─ S8: Documentation
                    ↓
Phase 2 (≈10 sessions)
├─ Backend FastAPI
├─ Android Client Léger
└─ Intégration Temps Réel
                    ↓
Phase 3 (≈15 sessions)
├─ Port TensorFlow Lite
├─ Client Lourd Android
└─ Optimisations Mobile
```

---

**Version**: 1.0  
**Date**: 2025-11-09  
**Auteur**: Architecture collaborative Claude + Bertrand
