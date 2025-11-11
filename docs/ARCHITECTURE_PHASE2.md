# 🎵 MusePartition - PHASE 2 : Architecture Client/Serveur

**Date** : 2025-11-10  
**Objectif** : Transformer le CLI en système client/serveur avec streaming audio  
**Statut** : 📋 PLANIFICATION

---

## Vue d'ensemble Phase 2

```
┌─────────────────────────────────────────────────────────────────┐
│                         ARCHITECTURE                             │
│                                                                  │
│  ┌──────────────────┐                    ┌──────────────────┐  │
│  │  Smartphone      │                    │  Backend Server  │  │
│  │  Android         │◄──────────────────►│  Python          │  │
│  │                  │    WebSocket/REST  │  FastAPI         │  │
│  │  - Enregistrement│                    │  - Pipeline      │  │
│  │  - UI Partition  │                    │  - Processing    │  │
│  │  - Streaming     │                    │  - Storage       │  │
│  └──────────────────┘                    └──────────────────┘  │
│         │                                          │            │
│         │ Audio Chunks (streaming)                 │            │
│         │ Base64 / Binary WebSocket                │            │
│         └──────────────────────────────────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Objectifs Phase 2

### Fonctionnels
1. ✅ **Enregistrement streaming** depuis smartphone
2. ✅ **Transcription asynchrone** sur serveur
3. ✅ **Notification** quand partition prête
4. ✅ **Téléchargement** MusicXML/MIDI/PDF
5. ✅ **UI mobile** pour visualiser partition

### Non-Fonctionnels
- **Latence** : < 2s après fin enregistrement
- **Streaming** : Chunks 1-2s audio
- **Scalabilité** : 10+ clients simultanés
- **Robustesse** : Reprise après déconnexion

---

## 📦 Structure Projet (2 Packages Python)

```
MusePartition/
│
├── musepartition-core/           # Package 1 : Moteur transcription
│   ├── setup.py
│   ├── pyproject.toml
│   ├── README.md
│   ├── musepartition_core/
│   │   ├── __init__.py
│   │   ├── audio_processor.py
│   │   ├── pitch_detector.py
│   │   ├── note_segmenter.py
│   │   ├── quantizer.py
│   │   ├── score_generator.py
│   │   ├── pipeline.py           # TranscriptionPipeline
│   │   ├── utils.py
│   │   └── types.py
│   └── tests/
│
├── musepartition-server/         # Package 2 : Backend API
│   ├── setup.py
│   ├── requirements.txt
│   ├── README.md
│   ├── musepartition_server/
│   │   ├── main.py               # FastAPI app
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── routes.py         # REST endpoints
│   │   │   └── websocket.py      # WebSocket (future)
│   │   ├── services/
│   │   │   ├── transcription.py
│   │   │   └── storage.py
│   │   └── models/
│   │       └── job.py
│   ├── storage/
│   │   ├── uploads/
│   │   └── outputs/
│   └── tests/
│
└── musepartition-android/        # Package 3 (Phase 3)
```

### Installation Développement

```bash
# 1. Package core
cd musepartition-core
pip install -e .

# 2. Package server
cd ../musepartition-server
pip install -e .
```

### Imports Propres ✅

```python
# Dans musepartition-server
from musepartition_core import TranscriptionPipeline
from musepartition_core.types import TranscriptionResult

# Pas de sys.path.append() !
```

---

## 📐 Architecture 3-Tiers

### **Tier 1 : Client Android (Présentation)**
```
┌───────────────────────────────────────┐
│        Application Android             │
├───────────────────────────────────────┤
│  UI Layer (Jetpack Compose)           │
│  - RecordButton                        │
│  - ProgressIndicator                   │
│  - ScoreViewer (VexFlow/WebView)       │
│  - DownloadButtons                     │
├───────────────────────────────────────┤
│  Business Logic (ViewModels)          │
│  - RecordingViewModel                  │
│  - TranscriptionViewModel              │
│  - StateManagement                     │
├───────────────────────────────────────┤
│  Data Layer (Repositories)             │
│  - AudioRepository                     │
│  - TranscriptionRepository             │
│  - WebSocketClient                     │
└───────────────────────────────────────┘
```

### **Tier 2 : Backend Server (Métier)**
```
┌───────────────────────────────────────┐
│        Backend Python (FastAPI)        │
├───────────────────────────────────────┤
│  API Layer (Routes)                    │
│  - /transcribe/upload   (POST)         │
│  - /transcribe/stream   (WS)           │
│  - /jobs/{id}           (GET)          │
│  - /scores/{id}/*       (GET)          │
├───────────────────────────────────────┤
│  Business Logic (Services)             │
│  - TranscriptionService                │
│  - AudioProcessingService              │
│  - JobQueue (Celery/RQ)                │
├───────────────────────────────────────┤
│  Core (Pipeline Phase 1)               │
│  - TranscriptionPipeline               │
│  - Tous modules existants              │
└───────────────────────────────────────┘
```

### **Tier 3 : Persistance (Données)**
```
┌───────────────────────────────────────┐
│        Storage Layer                   │
├───────────────────────────────────────┤
│  Database (SQLite/PostgreSQL)          │
│  - jobs (id, status, metadata)         │
│  - users (optionnel)                   │
├───────────────────────────────────────┤
│  File Storage                          │
│  - uploads/  (audio reçus)             │
│  - outputs/  (partitions générées)     │
│  - temp/     (fichiers intermédiaires) │
└───────────────────────────────────────┘
```

---

## 🔄 Flux de Données : Mode Streaming

### **Scénario 1 : Enregistrement → Transcription**

```
[Smartphone]                  [Backend Server]
     │                              │
     │ 1. Start Recording           │
     ├──────── WS Connect ─────────►│
     │                              │ Create Job (status=receiving)
     │                              │
     │ 2. Stream Audio Chunks       │
     ├──── Chunk 1 (1s, base64) ──►│ Save to buffer
     ├──── Chunk 2 (1s, base64) ──►│ Accumulate
     ├──── Chunk 3 (1s, base64) ──►│ Accumulate
     │         ...                  │
     │                              │
     │ 3. Stop Recording            │
     ├────── WS Close/Signal ──────►│
     │                              │ Job status = processing
     │                              │ ├─► Assemble chunks
     │                              │ ├─► TranscriptionPipeline
     │                              │ └─► Generate scores
     │                              │
     │ 4. Notification (optional)   │
     │◄──── WebSocket/Push ─────────┤ Job status = completed
     │                              │
     │ 5. Download Partition        │
     ├──── GET /scores/{id}/pdf ──►│
     │◄──────── PDF File ───────────┤
     │                              │
```

### **Scénario 2 : Upload Fichier Complet**

```
[Smartphone]                  [Backend Server]
     │                              │
     │ 1. Upload Audio File         │
     ├──── POST /transcribe/upload ►│
     │      (multipart/form-data)   │ Create Job (status=processing)
     │                              │ ├─► Save file
     │                              │ ├─► TranscriptionPipeline (async)
     │                              │ └─► Generate scores
     │                              │
     │ 2. Poll Status (or wait WS)  │
     ├──── GET /jobs/{id} ─────────►│
     │◄──── {status: "processing"}──┤
     │                              │
     │ ... wait ...                 │
     │                              │
     ├──── GET /jobs/{id} ─────────►│
     │◄──── {status: "completed"}───┤
     │                              │
     │ 3. Download                  │
     ├──── GET /scores/{id}/midi ──►│
     │◄──────── MIDI File ──────────┤
     │                              │
```

---

## 🛠️ Stack Technique Détaillé

### **Backend (Serveur)**

#### Framework Web
```python
# FastAPI (async, moderne, rapide)
- WebSocket natif
- Validation Pydantic
- OpenAPI auto
- CORS configuré
```

#### Queue Jobs Asynchrones
```python
# Option 1: Celery + Redis
- Scalable
- Monitoring
- Retry automatique

# Option 2: RQ (Redis Queue)
- Plus simple
- Suffisant pour début
```

#### Base de Données
```python
# Option 1: SQLite (simple, 1 serveur)
# Option 2: PostgreSQL (production, multi-serveurs)

# Schema
jobs:
  - id (UUID)
  - status (receiving|processing|completed|failed)
  - audio_path
  - output_paths (JSON: {musicxml, midi, pdf})
  - metadata (JSON: bpm, notes_count, etc.)
  - created_at, updated_at
```

#### Storage
```python
# Structure fichiers
/storage
  /uploads/{job_id}/
    audio.m4a
  /outputs/{job_id}/
    score.musicxml
    score.mid
    score.pdf
  /temp/{job_id}/
    chunks/
      chunk_001.wav
      chunk_002.wav
```

### **Client Android**

#### Framework UI
```kotlin
// Jetpack Compose (moderne, déclaratif)
- Material 3 Design
- ViewModel + StateFlow
- Navigation Component
```

#### Audio Capture
```kotlin
// MediaRecorder ou AudioRecord
- Format: PCM 16-bit, 22050 Hz
- Chunks: 1-2s
- Encoding: Base64 pour WebSocket
```

#### Networking
```kotlin
// OkHttp + Retrofit + WebSocket
- REST API (Retrofit)
- WebSocket (OkHttp)
- Coroutines pour async
```

#### Partition Display
```kotlin
// Option 1: WebView + VexFlow.js
// Option 2: Custom Canvas rendering
// Option 3: Bibliothèque tierce (si existe)
```

---

## 📡 API REST/WebSocket Détaillée

### **REST Endpoints**

#### 1. Upload Fichier Complet
```http
POST /api/v1/transcribe/upload
Content-Type: multipart/form-data

Parameters:
  - file: audio file (required)
  - title: string (optional)
  - composer: string (optional)
  - bpm: float (optional, override auto-detect)
  - time_signature: string (optional)
  - key_signature: string (optional)

Response 201:
{
  "job_id": "uuid",
  "status": "processing",
  "created_at": "ISO8601"
}
```

#### 2. Status Job
```http
GET /api/v1/jobs/{job_id}

Response 200:
{
  "job_id": "uuid",
  "status": "completed",  // receiving|processing|completed|failed
  "progress": 100,        // 0-100
  "result": {
    "bpm": 120.0,
    "num_notes": 42,
    "processing_time": 5.2
  },
  "scores": {
    "musicxml": "/api/v1/scores/{job_id}/musicxml",
    "midi": "/api/v1/scores/{job_id}/midi",
    "pdf": "/api/v1/scores/{job_id}/pdf"
  },
  "error": null
}
```

#### 3. Télécharger Partition
```http
GET /api/v1/scores/{job_id}/musicxml
GET /api/v1/scores/{job_id}/midi
GET /api/v1/scores/{job_id}/pdf

Response 200:
Content-Type: application/vnd.recordare.musicxml+xml  (or audio/midi, application/pdf)
Content-Disposition: attachment; filename="score.musicxml"

[binary content]
```

#### 4. Lister Jobs (optionnel)
```http
GET /api/v1/jobs?limit=10&offset=0

Response 200:
{
  "jobs": [...],
  "total": 42,
  "limit": 10,
  "offset": 0
}
```

### **WebSocket Protocol**

#### Endpoint
```
WS /api/v1/transcribe/stream
```

#### Messages Client → Serveur
```json
// 1. Initialisation
{
  "type": "init",
  "metadata": {
    "title": "My Song",
    "composer": "John Doe",
    "sample_rate": 22050,
    "channels": 1
  }
}

// 2. Chunk audio
{
  "type": "audio_chunk",
  "data": "base64_encoded_audio",
  "sequence": 1,
  "timestamp": 1234567890.123
}

// 3. Fin enregistrement
{
  "type": "end"
}
```

#### Messages Serveur → Client
```json
// 1. Job créé
{
  "type": "job_created",
  "job_id": "uuid",
  "status": "receiving"
}

// 2. Progression
{
  "type": "progress",
  "job_id": "uuid",
  "status": "processing",
  "progress": 45
}

// 3. Terminé
{
  "type": "completed",
  "job_id": "uuid",
  "result": {...},
  "scores": {...}
}

// 4. Erreur
{
  "type": "error",
  "message": "Failed to process audio",
  "code": "PROCESSING_ERROR"
}
```

---

## 🔐 Sécurité

### **Authentification** (Phase 2.2+)
```python
# Option 1: JWT Tokens
# Option 2: API Keys
# Option 3: OAuth2 (si multi-users)

# Pour début : IP whitelist ou pas d'auth (réseau local)
```

### **Validation**
```python
# FastAPI Pydantic models
- Max file size: 50 MB
- Audio formats: WAV, MP3, M4A, FLAC
- Rate limiting: 10 requêtes/min/IP
```

### **CORS**
```python
# Autoriser Android app
origins = [
    "http://localhost:*",
    "https://your-app-domain.com"
]
```

---

## 📊 Gestion d'État

### **États Job**
```
receiving     → Réception chunks audio (streaming)
processing    → Pipeline transcription en cours
completed     → Partition prête
failed        → Erreur durant traitement
expired       → Job expiré (cleanup après X jours)
```

### **Transitions**
```
receiving → processing  (end signal reçu)
processing → completed  (pipeline succès)
processing → failed     (pipeline erreur)
completed → expired     (après 7 jours)
```

---

## 🗂️ Sessions de Développement Phase 2

### **SESSION 1 : Backend Foundation** (~3h)
**Objectifs** :
- Setup FastAPI + structure projet
- Modèles Pydantic (Job, TranscriptionRequest)
- Base de données (SQLite + SQLAlchemy)
- Endpoint `/upload` basique

**Livrables** :
- `backend/app/main.py`
- `backend/app/models.py`
- `backend/app/database.py`
- Tests API basiques

---

### **SESSION 2 : Pipeline Integration** (~2h)
**Objectifs** :
- Intégrer TranscriptionPipeline Phase 1
- Service TranscriptionService
- Queue jobs async (RQ ou Celery)
- Gestion fichiers (upload/storage)

**Livrables** :
- `backend/app/services/transcription.py`
- `backend/app/workers.py`
- Tests intégration pipeline

---

### **SESSION 3 : WebSocket Streaming** (~3h)
**Objectifs** :
- Endpoint WebSocket `/stream`
- Réception chunks audio
- Assemblage fichier final
- Protocol messages

**Livrables** :
- `backend/app/websocket.py`
- `backend/app/services/audio_assembler.py`
- Tests WebSocket

---

### **SESSION 4 : API Complète** (~2h)
**Objectifs** :
- Endpoint `/jobs/{id}`
- Endpoints `/scores/{id}/*`
- Gestion erreurs robuste
- Logging structuré

**Livrables** :
- `backend/app/routes/` (complet)
- Documentation OpenAPI
- Tests E2E API

---

### **SESSION 5 : Android Client - Setup** (~3h)
**Objectifs** :
- Projet Android + Jetpack Compose
- Architecture MVVM
- Navigation
- Permissions audio

**Livrables** :
- `android/app/` (structure)
- `android/app/ui/screens/`
- `android/app/viewmodels/`

---

### **SESSION 6 : Android Client - Recording** (~3h)
**Objectifs** :
- AudioRecord implémentation
- Streaming chunks WebSocket
- UI Recording (bouton, timer)
- Gestion états

**Livrables** :
- `android/app/audio/AudioRecorder.kt`
- `android/app/network/WebSocketClient.kt`
- `android/app/ui/RecordingScreen.kt`

---

### **SESSION 7 : Android Client - Partition Display** (~3h)
**Objectifs** :
- WebView + VexFlow.js
- Affichage MusicXML
- Zoom/scroll partition
- Download buttons

**Livrables** :
- `android/app/ui/ScoreViewer.kt`
- `android/assets/vexflow/`
- Tests UI

---

### **SESSION 8 : Tests E2E & Déploiement** (~4h)
**Objectifs** :
- Tests intégration Android ↔ Backend
- Tests charge (10+ clients)
- Docker backend
- Documentation déploiement

**Livrables** :
- Tests E2E complets
- `backend/Dockerfile`
- `docker-compose.yml`
- `DEPLOYMENT.md`

---

## 📈 Estimation Totale Phase 2

| Partie | Sessions | Durée | Complexité |
|--------|----------|-------|------------|
| Backend (S1-S4) | 4 | ~10h | Moyenne |
| Android (S5-S7) | 3 | ~9h | Moyenne |
| Tests & Deploy (S8) | 1 | ~4h | Élevée |
| **TOTAL** | **8 sessions** | **~23h** | - |

---

## 🎯 Métriques de Succès Phase 2

### Performance
- ✅ Latence < 2s (fin enregistrement → début traitement)
- ✅ Throughput : 10 transcriptions simultanées
- ✅ Taille chunks : 1-2s audio
- ✅ Débit streaming : ~44 KB/s (22050 Hz PCM)

### Fonctionnel
- ✅ Streaming audio robuste (reconnexion auto)
- ✅ Notification temps réel (progression)
- ✅ Download MusicXML/MIDI/PDF
- ✅ UI intuitive (enregistrer → voir partition)

### Qualité
- ✅ Gestion erreurs gracieuse
- ✅ Logs structurés (debugging)
- ✅ Tests E2E passants
- ✅ Documentation complète (API + déploiement)

---

## 📝 Décisions Techniques Validées

### 1. Architecture Packages
- ✅ **2 packages Python séparés** : `musepartition-core` + `musepartition-server`
- ✅ **Imports propres** : Via `pip install -e .`, pas de `sys.path.append()`
- ✅ **Séparation responsabilités** : Core = moteur, Server = API

### 2. Base de Données
- ✅ **Pas de DB** pour Phase 2.0 Minimal
- ✅ **Dict en mémoire** + **filesystem** pour jobs
- ✅ **Migration SQLite** facile si besoin

### 3. Mode Processing
- ✅ **Batch mode** (Phase 2.0) : Réception complète → Processing
- ⏳ **Streaming progressif** (Phase 2.1) : Processing parallèle réception

### 4. Stack Backend
- ✅ **FastAPI** : API moderne, async
- ✅ **Pas de RQ** pour début (processing synchrone)
- ✅ **Storage filesystem** : uploads/ + outputs/

### 5. Plan Développement
- ✅ **Session 1** : API `/upload` + storage + imports core
- ✅ **Progressif** : Batch d'abord, streaming ensuite

---

### **Réutilisation Maximale**
```python
# Phase 1 (CLI)
TranscriptionPipeline.transcribe(audio_file, output_dir)

# Phase 2 (Backend)
# Même code ! Juste wrappé dans service async
async def transcribe_job(job_id, audio_path):
    pipeline = TranscriptionPipeline(config)
    result = await asyncio.to_thread(
        pipeline.transcribe, audio_path, output_dir
    )
    # Save result to DB
```

**Changements mineurs** :
- Async wrappers
- Storage paths adaptés
- Config depuis DB/env vars

---

## 📝 Prochaines Étapes Immédiates

### **1. Validation Architecture** ✅
Tu valides cette archi ?

### **2. Choix Stack**
- Backend : **FastAPI** + **RQ** (simple) ou **Celery** (prod) ?
- Android : **Jetpack Compose** OK ?
- DB : **SQLite** (simple) ou **PostgreSQL** (prod) ?

### **3. Session 1 Backend**
Je code le backend foundation ?
- FastAPI setup
- `/upload` endpoint
- Pipeline integration
- Tests

**Prêt à démarrer Phase 2 ?** 🚀
