# MusePartition Server

**Backend API for Audio to Music Score Transcription**

FastAPI-based server providing REST and WebSocket endpoints for audio transcription services.

## Features

- 🌐 **REST API**: Upload audio files, check job status, download scores
- 🔌 **WebSocket**: Real-time audio streaming (future)
- 📦 **Batch Processing**: Process uploaded files asynchronously
- 💾 **File Storage**: Manage uploads and generated scores
- 🎵 **Core Integration**: Uses `musepartition-core` for transcription

## Architecture

```
musepartition-server/
├── musepartition_server/
│   ├── main.py              # FastAPI app
│   ├── api/
│   │   ├── routes.py        # REST endpoints
│   │   └── websocket.py     # WebSocket endpoints
│   ├── services/
│   │   ├── transcription.py # Transcription service
│   │   └── storage.py       # File storage
│   ├── models/
│   │   └── job.py           # Pydantic models
│   └── config.py            # Configuration
├── storage/
│   ├── uploads/             # Uploaded audio files
│   └── outputs/             # Generated scores
└── tests/
```

## Installation

### Development

```bash
# 1. Install musepartition-core
cd ../musepartition-core
pip install -e .

# 2. Install server
cd ../musepartition-server
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### Run Server

```bash
uvicorn musepartition_server.main:app --reload --port 8000
```

### API Documentation

Open browser: http://localhost:8000/docs

## API Endpoints

### Upload Audio File

```http
POST /api/v1/transcribe/upload
Content-Type: multipart/form-data

Parameters:
  - file: audio file (required)
  - title: string (optional)
  - composer: string (optional)
  - bpm: float (optional)
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "created_at": "2025-11-10T15:30:00Z"
}
```

### Get Job Status

```http
GET /api/v1/jobs/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "result": {
    "bpm": 120.0,
    "num_notes": 42,
    "processing_time": 5.2
  },
  "scores": {
    "musicxml": "/api/v1/scores/{job_id}/musicxml",
    "midi": "/api/v1/scores/{job_id}/midi",
    "pdf": "/api/v1/scores/{job_id}/pdf"
  }
}
```

### Download Score

```http
GET /api/v1/scores/{job_id}/musicxml
GET /api/v1/scores/{job_id}/midi
GET /api/v1/scores/{job_id}/pdf
```

## Configuration

Create `.env` file:

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Storage
STORAGE_PATH=./storage
MAX_FILE_SIZE=50_000_000  # 50 MB

# Transcription defaults
DEFAULT_CONFIDENCE_THRESHOLD=0.6
DEFAULT_QUANTIZATION_GRID=1/16
```

## Testing

```bash
pytest tests/ -v
```

## Development Status

**Phase 2.0 - Batch Mode**
- ✅ REST API `/upload`
- ✅ File storage
- ✅ Job status tracking
- ✅ Score downloads
- ⏳ WebSocket streaming (future)
- ⏳ Job queue (RQ) (future)

## License

MIT License

## Version

2.0.0 (Phase 2 - Initial)
