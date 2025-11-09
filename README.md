# MusePartition 🎵

**Transcription audio → partition musicale avec approche progressive**

![Status](https://img.shields.io/badge/Status-En%20Développement-yellow)
![Phase](https://img.shields.io/badge/Phase-1%20(PoC)-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)

---

## 🎯 Vision du Projet

MusePartition est un système de transcription musicale permettant de convertir des enregistrements audio en partitions lisibles. Le projet suit une approche progressive :

1. **Phase 1 (Actuelle)** : PoC Python - Fichier audio → Partition (monophonie/flûte)
2. **Phase 2** : Backend + Client léger Android
3. **Phase 3** : Client lourd Android avec traitement embarqué

### Cibles Musicales
- **Phase 1** : Flûte (monophonie) ✓
- **Future** : Piano (polyphonie)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Architecture complète, phases, stack technique, estimations |
| **[CURRENT_STATUS.md](CURRENT_STATUS.md)** | État actuel du développement, modules complétés |
| **[SESSION_LOG.md](SESSION_LOG.md)** | Journal détaillé des sessions de développement |
| **[API_SUMMARY.md](API_SUMMARY.md)** | Synthèse concise des API implémentées |

---

## 🚀 Quick Start

### Statut Actuel
```
Phase 1 : PoC Python
[░░░░░░░░░░░░░░░░░░░░] 0% (Session 0/8)

⏳ Prochaine étape : Session 1 - Setup & Audio Processing
```

### Installation (À venir)

**⚠️ Important : Utiliser un environnement virtuel (venv) est fortement recommandé**

#### Installation Automatique (Recommandé)

**Linux / macOS** :
```bash
# Cloner le repo
git clone https://github.com/bvirfollet/MusePartition.git
cd MusePartition

# Lancer script d'installation (crée venv + installe dépendances + lance tests)
chmod +x setup.sh
./setup.sh
```

**Windows** :
```cmd
REM Cloner le repo
git clone https://github.com/bvirfollet/MusePartition.git
cd MusePartition

REM Lancer script d'installation
setup.bat
```

#### Installation Manuelle

```bash
# Cloner le repo
git clone https://github.com/bvirfollet/MusePartition.git
cd MusePartition

# Créer environnement virtuel
python3 -m venv venv

# Activer venv
source venv/bin/activate  # Linux/macOS
# OU
venv\Scripts\activate.bat  # Windows

# Installer dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Lancer tests
pytest tests/ -v
```

**📚 Guide détaillé** : Voir [INSTALL_GUIDE.md](INSTALL_GUIDE.md)

### Utilisation Prévue (Phase 1)

```bash
# Transcription basique
python -m src.cli transcribe recording.wav

# Avec options
python -m src.cli transcribe recording.wav \
  --output ./results \
  --bpm 120 \
  --time-signature 3/4 \
  --verbose
```

**Sorties générées** :
- `output/score.pdf` - Partition visuelle
- `output/score.musicxml` - Format échange
- `output/score.mid` - Playback MIDI

---

## 🏗️ Architecture (Phase 1 - PoC)

```
Input Audio File (WAV/MP3)
       ↓
┌──────────────────────────────────────────┐
│  Module 1 : Audio Processing             │
│  (librosa, soundfile)                    │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│  Module 2 : Pitch Detection              │
│  (CREPE - TensorFlow)                    │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│  Module 3 : Note Segmentation            │
│  (Hz → MIDI, onset/offset)               │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│  Module 4 : Musical Quantization         │
│  (Tempo, grille rythmique)               │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│  Module 5 : Score Generation             │
│  (music21 → PDF/MusicXML/MIDI)           │
└──────────────────────────────────────────┘
       ↓
Output: PDF, MusicXML, MIDI
```

**Détails** : Voir [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 📋 Roadmap Phase 1 (8 Sessions)

| # | Session | Statut | Modules |
|---|---------|--------|---------|
| 1 | Setup & Audio Processing | ⏳ À faire | AudioProcessor |
| 2 | Pitch Detection | ⏳ À faire | PitchDetector (CREPE) |
| 3 | Note Segmentation | ⏳ À faire | NoteSegmenter |
| 4 | Musical Quantization | ⏳ À faire | MusicalQuantizer |
| 5 | Score Generation | ⏳ À faire | ScoreGenerator |
| 6 | Pipeline & CLI | ⏳ À faire | TranscriptionPipeline, CLI |
| 7 | Tests E2E & Tuning | ⏳ À faire | Optimisation paramètres |
| 8 | Documentation & Release | ⏳ À faire | Release v0.1.0 |

**Estimation totale** : ~21h sur 8 sessions

---

## 🎯 Métriques de Succès (Phase 1)

| Métrique | Cible |
|----------|-------|
| Précision notes (flûte simple) | >90% |
| Erreur rythmique | <10% |
| Qualité partition PDF | Lisible musicalement |
| Temps traitement (30s audio) | <10s |

---

## 🛠️ Stack Technique

### Phase 1 (PoC Python)
- **Langage** : Python 3.10+
- **Audio I/O** : librosa, soundfile
- **Pitch Detection** : CREPE (TensorFlow)
- **Music Notation** : music21
- **CLI** : argparse + rich
- **Tests** : pytest

### Phases Futures
- **Backend** : FastAPI + WebSocket
- **Android** : Kotlin + Jetpack Compose
- **Native Processing** : C++ + TensorFlow Lite

---

## 📖 Guide de Reprise dans Nouveau Contexte

Si tu changes d'IA, de machine, ou reprends après une pause :

### 1. Fichiers Essentiels à Fournir
```
MusePartition/
├── ARCHITECTURE.md          # Vision globale, phases, API
├── CURRENT_STATUS.md        # État actuel, modules complétés
├── SESSION_LOG.md           # Historique détaillé sessions
├── API_SUMMARY.md           # Synthèse API (signatures/exemples)
├── src/                     # Code source (si existant)
└── tests/                   # Tests (si existants)
```

### 2. Commandes de Validation État
```bash
# Vérifier structure
ls -la

# Lire état actuel
cat CURRENT_STATUS.md

# Historique sessions
cat SESSION_LOG.md

# Installer & tester
pip install -r requirements.txt
pytest tests/ -v
```

### 3. Questions à Poser
- "Quelle est la dernière session complétée ?"
- "Y a-t-il des tests cassés ?"
- "Quelles décisions techniques sont en suspens ?"

---

## 🔧 Développement

### Structure Projet (Prévue)
```
MusePartition/
├── ARCHITECTURE.md          # Doc architecture
├── README.md                # Ce fichier
├── requirements.txt         # Dépendances Python
├── setup.py                 # Package setup
├── config.example.json      # Config template
├── src/                     # Code source
│   ├── audio_processor.py
│   ├── pitch_detector.py
│   ├── note_segmenter.py
│   ├── quantizer.py
│   ├── score_generator.py
│   ├── transcription_pipeline.py
│   └── cli.py
├── tests/                   # Tests unitaires
├── data/
│   ├── samples/             # Fichiers audio test
│   └── models/              # Modèles ML (CREPE)
├── docs/                    # Documentation
│   ├── SESSION_LOG.md
│   ├── CURRENT_STATUS.md
│   └── API_SUMMARY.md
└── output/                  # Résultats transcriptions
```

### Conventions Code
- **Style** : PEP 8 + Black formatter
- **Type hints** : Obligatoires
- **Docstrings** : Google style
- **Tests** : pytest, coverage >80%

---

## 🤝 Contribution

Ce projet suit une approche documentée pour permettre les reprises contextuelles :

1. **Avant chaque session** : Lire `CURRENT_STATUS.md`
2. **Pendant la session** : Coder, tester, documenter
3. **Après chaque session** : Mettre à jour `SESSION_LOG.md` et `CURRENT_STATUS.md`

### Workflow Session Type
```bash
# 1. Contexte
cat CURRENT_STATUS.md

# 2. Développement
# ... coder ...

# 3. Tests
pytest tests/test_new_module.py -v

# 4. Documentation
# Mettre à jour SESSION_LOG.md, CURRENT_STATUS.md, API_SUMMARY.md

# 5. Commit
git add .
git commit -m "Session X: [Description]"
```

---

## 📝 Licence

*À définir (MIT/Apache 2.0/GPL suggéré)*

---

## 📞 Contact

**Bertrand** - Développeur principal  
Repository: [github.com/bvirfollet/MusePartition](https://github.com/bvirfollet/MusePartition)

---

## 🎵 Pourquoi MusePartition ?

Ce projet vise à démocratiser la transcription musicale pour :
- Musiciens souhaitant noter leurs improvisations
- Professeurs créant du matériel pédagogique
- Chercheurs analysant des enregistrements
- Développeurs explorant la MIR (Music Information Retrieval)

**Progression** : Monophonie (flûte) → Polyphonie (piano) → Temps réel → Mobile

---

**Version** : 0.0.0 (Initialisation)  
**Dernière MAJ** : 2025-11-09
