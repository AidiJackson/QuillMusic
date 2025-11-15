# QuillMusic Architecture

## Overview

QuillMusic is an AI-powered music production platform that enables users to create complete songs from simple text prompts, with the flexibility to manually edit and refine every aspect of the production. The platform is designed as a modular system where AI engines can be easily swapped, upgraded, or replaced without affecting the overall architecture.

## High-Level Concept

```
┌─────────────────────────────────────────────────────────────┐
│                         User Input                           │
│              (Prompt, Genre, Mood, Parameters)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Song Blueprint Engine                     │
│        (Generates structure, lyrics, vocal style)            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Render Engine                           │
│            (Orchestrates sub-engines via jobs)               │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Instrumental │  │    Vocal     │  │  Mastering   │
    │   Engine     │  │   Engine     │  │   Engine     │
    └──────────────┘  └──────────────┘  └──────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Final Audio    │
                    │  (MP3/WAV/FLAC)  │
                    └──────────────────┘
```

## System Components

### 1. Frontend (React + Vite + TypeScript)

The frontend provides three main interfaces:

#### Dashboard
- Overview of user's projects and recent activity
- Quick access to AI Song Builder and Manual Creator
- Statistics and usage metrics

#### AI Song Builder
- **Input Form**: Collects user prompt, genre, mood, and parameters
- **Blueprint Display**: Shows generated song structure, sections, and lyrics
- **Render Controls**: Buttons to trigger render jobs

#### Manual Creator
- **Project Management**: Create and manage manual music projects
- **Track Grid**: Timeline-based pattern arrangement (16 bars)
- **Pattern Editor**: Grid-based note editor with pitch/step layout
- **Track Types**: Drums, Bass, Chords, Lead, FX, Vocal
- **Data Persistence**: SQLite database for projects, tracks, patterns, notes
- **Note**: Audio rendering to be added in future phase

#### Instrumental Studio
- **Source Selection**: Choose between AI blueprints or manual projects
- **Source Browsing**: Live-updated dropdowns showing available sources
- **Source Summary**: Display key musical parameters (BPM, key, genre, etc.)
- **Render Settings**: Configure engine type, duration, style hints, quality
- **Job Status**: Real-time job tracking with color-coded status badges
- **Audio Playback**: Integrated HTML5 audio player for rendered instrumentals
- **Dual Input Support**: Renders from both blueprint engine and manual creator

#### Render Queue
- **Job Tracking**: Monitor status of render jobs
- **Audio Preview**: Play completed renders
- **Download**: Export final audio files

**Technology Stack:**
- React 18 with TypeScript
- Vite for fast builds
- Tailwind CSS for styling
- shadcn/ui for components
- React Router for navigation
- Sonner for toast notifications

### 2. Backend (FastAPI + Python)

The backend is built on FastAPI and follows a clean, modular architecture.

#### Core Components

**Config (`app/core/config.py`):**
- Environment-based settings using Pydantic
- Redis connection strings
- CORS configuration
- Debug flags
- **Song Engine Configuration:**
  - `SONG_ENGINE_MODE`: `"fake"` (default) or `"llm"`
  - `LLM_API_KEY`: API key for LLM provider
  - `LLM_API_BASE`: Optional custom API endpoint
  - `LLM_MODEL_NAME`: Model to use (e.g., `"gpt-4.1-mini"`)
  - `LLM_PROVIDER`: Provider type (`"openai-compatible"`)

**Dependencies (`app/core/dependencies.py`):**
- Redis connection pool
- RQ queue instances
- Shared services

#### API Layer (`app/api/routes/`)

**Health Endpoint:**
- `GET /api/health` - Service status check

**Song Blueprint Endpoints:**
- `POST /api/song/blueprint` - Generate song structure from prompt
- `GET /api/song/blueprints` - List all blueprints (with limit)
- `GET /api/song/blueprints/{id}` - Get specific blueprint

**Instrumental Render Endpoints:**
- `POST /api/instrumental/render` - Create instrumental render job
- `GET /api/instrumental/jobs/{job_id}` - Get job status and audio URL

**Render Endpoints (Legacy):**
- `POST /api/renders` - Create a render job
- `GET /api/renders/{job_id}` - Get render job status

**Manual Creator Endpoints:**
- `POST /api/manual/projects` - Create new project
- `GET /api/manual/projects` - List all projects
- `GET /api/manual/projects/{id}` - Get project with tracks/patterns/notes
- `DELETE /api/manual/projects/{id}` - Delete project
- `POST /api/manual/projects/{id}/tracks` - Add track
- `PATCH /api/manual/tracks/{id}` - Update track
- `DELETE /api/manual/tracks/{id}` - Delete track
- `POST /api/manual/tracks/{id}/patterns` - Create pattern
- `PATCH /api/manual/patterns/{id}` - Update pattern
- `DELETE /api/manual/patterns/{id}` - Delete pattern
- `GET /api/manual/patterns/{id}/notes` - Get pattern notes
- `POST /api/manual/patterns/{id}/notes/bulk` - Bulk update notes

#### Services Layer (`app/services/`)

**Song Blueprint Service:**

The song blueprint service uses a pluggable engine architecture that allows switching between different generation backends:

```python
class SongBlueprintEngine(ABC):
    @abstractmethod
    def generate_blueprint(req: SongBlueprintRequest) -> SongBlueprintResponse:
        pass
```

**Available Engines:**

1. **FakeSongBlueprintEngine** (Default)
   - Deterministic mock data generation
   - No external API calls required
   - Perfect for development and testing
   - Always available as fallback

2. **LLMSongBlueprintEngine** (Optional)
   - Uses Large Language Models (OpenAI, Claude, etc.)
   - Generates creative, coherent lyrics and song structures
   - Configurable via environment variables
   - Automatically falls back to FakeSongBlueprintEngine on errors

**Switching Between Engines:**

The engine is selected automatically based on configuration:

```bash
# Default: Use fake engine (no API calls)
QUILLMUSIC_SONG_ENGINE_MODE=fake

# Enable LLM engine
QUILLMUSIC_SONG_ENGINE_MODE=llm
QUILLMUSIC_LLM_API_KEY=your-api-key
QUILLMUSIC_LLM_MODEL_NAME=gpt-4.1-mini
QUILLMUSIC_LLM_API_BASE=https://api.openai.com/v1  # optional
QUILLMUSIC_LLM_PROVIDER=openai-compatible
```

The factory function `get_song_blueprint_engine()` in `app/core/dependencies.py` handles engine selection with proper error handling and fallbacks.

**Instrumental Render Service:**

The instrumental render service orchestrates the creation of instrumental audio from either AI-generated blueprints or Manual Creator projects. It provides a clean abstraction layer between the API and the rendering engines.

```python
class BaseInstrumentalEngine(ABC):
    @abstractmethod
    def render_from_blueprint(blueprint: SongBlueprintResponse) -> Tuple[str, int]:
        """Returns (audio_url, duration_seconds)"""
        pass

    @abstractmethod
    def render_from_manual_project(project, tracks, patterns) -> Tuple[str, int]:
        """Returns (audio_url, duration_seconds)"""
        pass
```

**Available Engines:**

1. **FakeInstrumentalEngine** (Default)
   - Calculates duration based on musical structure (bars, BPM, time signature)
   - Returns deterministic demo URLs
   - No external dependencies
   - Perfect for development and testing

2. **HttpInstrumentalEngine** (Future)
   - Placeholder for external HTTP-based AI services
   - Currently delegates to FakeInstrumentalEngine
   - Prepared for integration with Stable Audio, MusicGen, etc.

**Duration Calculation:**
The engine intelligently calculates audio duration based on musical parameters:
- For blueprints: `total_bars = sum(section.bars for all sections)`
- For manual projects: `last_bar = max(pattern.start_bar + pattern.length_bars)`
- Conversion: `duration_seconds = (bars * 60 / bpm * 4)` for 4/4 time
- Clamped to 8-600 seconds for safety

**Database Persistence:**
- `InstrumentalJobModel`: Stores render jobs with status tracking
- `SongBlueprintModel`: Persists blueprints for reuse in instrumental rendering
- Supports both "blueprint" and "manual_project" source types

**API Endpoints:**
- `POST /api/instrumental/render` - Create instrumental render job
- `GET /api/instrumental/jobs/{job_id}` - Get job status and audio URL

**Render Engine (Legacy):**
```python
class RenderEngine(ABC):
    @abstractmethod
    def submit(song_id: str, render_type: RenderType) -> str:
        pass

    @abstractmethod
    def status(job_id: str) -> RenderJobStatus:
        pass
```

Currently implemented with `FakeRenderEngine` for development. Production will use GPU-based models.

#### Data Models (`app/schemas/`)

**Song Blueprint:**
- `SongBlueprintRequest`: User input
- `SongBlueprintResponse`: Complete song structure
- `SectionSchema`: Individual section (verse, chorus, etc.)
- `VocalStyleSchema`: Vocal characteristics

**Render Jobs:**
- `RenderJobCreate`: Job submission
- `RenderJobStatus`: Job tracking and results
- `RenderType`: instrumental | vocals | full_mix
- `RenderStatus`: queued | processing | ready | failed

**Instrumental Rendering:**
- `InstrumentalRenderRequest`: Render request with source type and settings
- `InstrumentalRenderStatus`: Job tracking with audio URL and metadata
- `InstrumentalEngineType`: fake | external_http
- `InstrumentalSourceType`: blueprint | manual_project
- `InstrumentalQuality`: draft | standard | high

**Manual Creator:**
- `ManualProject`: Project metadata (tempo, key, time signature)
- `Track`: Instrument channels with mixer controls
- `Pattern`: Musical patterns with bar position and length
- `Note`: Individual MIDI notes with pitch, step, velocity

### 3. Job Queue System (Redis + RQ)

**Purpose:**
Audio rendering is computationally intensive and can take minutes to hours. A job queue system allows:
- Asynchronous processing
- Horizontal scaling (multiple workers)
- Priority management
- Failure handling and retries

**Queues:**
1. **blueprints** - For heavy LLM-based blueprint generation (future)
2. **renders** - For audio rendering tasks

**Workers:**
Located in `app/workers/worker.py`, workers pull jobs from Redis queues and process them. In production, these would run on GPU-enabled machines.

### 4. ML Engines

#### Instrumental Engine (Implemented)

**Current Status:** Phase 3 Complete - Clean abstraction with fake engine

The instrumental engine is fully implemented with a pluggable architecture ready for real AI models:

**Architecture:**
- `BaseInstrumentalEngine`: Abstract base class defining the interface
- `FakeInstrumentalEngine`: Production-ready fake engine with realistic duration calculations
- `HttpInstrumentalEngine`: Stub for future external API integration

**Supported Input Sources:**
- AI-generated song blueprints (from LLM or fake engine)
- Manual Creator projects (user-composed MIDI patterns)

**Current Capabilities:**
- Duration calculation based on musical structure (bars, BPM, time signature)
- Deterministic demo URL generation
- Source type abstraction (blueprint vs manual project)
- Quality tier support (draft, standard, high)
- Style hints for future AI guidance

**Future Real Models to Integrate:**
- Stable Audio 2.0 (Stability AI)
- MusicGen (Meta)
- Riffusion XL
- Custom fine-tuned models

**Integration Points:**
- Implement `BaseInstrumentalEngine` interface
- Return `(audio_url, duration_seconds)` tuple
- Handle blueprint and manual project sources
- Apply genre, BPM, key constraints

#### Vocal Engine
**Models to integrate:**
- OpenVPI for synthesis
- DiffSinger for quality
- RVC for voice conversion
- Bark for diverse voices

**Responsibilities:**
- Text-to-speech for lyrics
- Apply vocal style (gender, tone, energy)
- Sync with instrumental timing

#### Mastering Engine
**Techniques:**
- Loudness normalization (LUFS targeting)
- EQ balancing
- Stereo widening
- Compression and limiting
- Reference matching (optional)

### 5. Manual Creator (DAW Lite)

The Manual Creator provides a pattern-based music creation interface inspired by PlayStation's Music 2000.

**Current Implementation (Phase 2):**

**Data Model:**
- `ManualProject`: Contains tempo, key, time signature
- `Track`: Represents an instrument channel with volume, pan, mute, solo
- `Pattern`: A musical pattern at a specific bar position with a defined length
- `Note`: Individual notes with step index, pitch (MIDI), and velocity

**Backend API (`/api/manual/`):**
- `POST /manual/projects` - Create new project
- `GET /manual/projects` - List all projects
- `GET /manual/projects/{id}` - Get project detail with all tracks/patterns/notes
- `DELETE /manual/projects/{id}` - Delete project (cascade)
- `POST /manual/projects/{id}/tracks` - Add track
- `PATCH /manual/tracks/{id}` - Update track properties
- `POST /manual/tracks/{id}/patterns` - Create pattern
- `PATCH /manual/patterns/{id}` - Update pattern
- `POST /manual/patterns/{id}/notes/bulk` - Replace all notes in pattern
- `GET /manual/patterns/{id}/notes` - Get pattern notes

**Database:**
- SQLite with SQLAlchemy ORM
- Cascade deletion for hierarchical data
- Proper foreign key relationships

**Frontend Components:**
- **Project Selector**: Dropdown to choose or create projects
- **Track Grid**: 16-bar timeline grid with color-coded instruments
- **Pattern Creation**: Click cells to create/select patterns
- **Note Editor**: Grid-based MIDI note editor (7 pitches × 16 steps)
- **Pattern Highlighting**: Visual feedback for selected patterns

**Future Enhancements (Phase 6):**
- Web Audio API integration for playback
- Actual audio rendering from manual projects
- Mixer controls with visual feedback
- Waveform display
- Drag-and-drop pattern arrangement
- AI-assisted pattern generation

## Data Flow

### Creating a Song

1. **User Input** → Frontend form
2. **API Call** → `POST /api/song/blueprint`
3. **Blueprint Generation** → `SongBlueprintEngine.generate_blueprint()`
4. **Response** → Frontend displays structure and lyrics
5. **User Review** → Can edit or regenerate
6. **Render Submission** → `POST /api/renders`
7. **Job Queue** → Redis stores job, worker picks it up
8. **Processing** → Worker calls instrumental, vocal, mastering engines
9. **Storage** → Upload to S3/GCS
10. **Status Update** → Job marked as "ready" with audio URL
11. **User Download** → Frontend fetches and plays audio

## Technology Choices

### Why FastAPI?
- Native async support for high concurrency
- Automatic OpenAPI documentation
- Excellent type safety with Pydantic
- Fast performance (comparable to Node.js, Go)

### Why Redis + RQ?
- Simple, reliable job queue
- Easy to scale workers horizontally
- Good monitoring tools
- Native Python support

### Why React + Vite?
- Modern, fast development experience
- Rich ecosystem for UI components
- TypeScript for type safety
- Easy to build complex UIs (DAW interface)

### Why Separate Engines?
- **Modularity**: Swap models without changing architecture
- **Versioning**: Run multiple model versions simultaneously
- **A/B Testing**: Compare outputs from different engines
- **Cost Optimization**: Use cheaper models for previews

## Deployment Architecture (Future)

```
┌─────────────────────────────────────────────────────────────┐
│                         Cloudflare                           │
│                    (CDN + DDoS Protection)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer                           │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   API Pod 1  │  │   API Pod 2  │  │   API Pod N  │
    │  (FastAPI)   │  │  (FastAPI)   │  │  (FastAPI)   │
    └──────────────┘  └──────────────┘  └──────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Redis Cluster  │
                    │   (Job Queue)    │
                    └──────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ GPU Worker 1 │  │ GPU Worker 2 │  │ GPU Worker N │
    │ (A100/H100)  │  │ (A100/H100)  │  │ (A100/H100)  │
    └──────────────┘  └──────────────┘  └──────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Object Storage │
                    │   (S3 / GCS)     │
                    └──────────────────┘
```

**Scaling Strategy:**
- **API**: Horizontal scaling with Kubernetes
- **Workers**: Auto-scaling based on queue depth
- **Storage**: CDN for audio delivery
- **Database**: PostgreSQL with read replicas (when needed)

## Security Considerations

1. **API Rate Limiting**: Prevent abuse
2. **Authentication**: JWT tokens for users
3. **CORS**: Restricted origins
4. **Input Validation**: Pydantic schemas
5. **Secrets Management**: Environment variables, Vault
6. **Audio Watermarking**: For free tier tracks

## Performance Optimization

1. **Caching**: Redis for blueprint results
2. **CDN**: CloudFlare for static assets and audio
3. **Lazy Loading**: Frontend code splitting
4. **Batch Processing**: Combine multiple render requests
5. **Model Optimization**: Quantization, TensorRT for inference

## Monitoring & Observability

1. **Metrics**: Prometheus + Grafana
2. **Logs**: Structured logging with ELK stack
3. **Tracing**: OpenTelemetry for request tracing
4. **Alerts**: PagerDuty for critical issues
5. **Analytics**: PostHog for user behavior

## Future Enhancements

1. **Collaborative Editing**: Real-time multi-user DAW
2. **Stem Separation**: Extract vocals, drums, etc. from audio
3. **Sample Library**: User-uploaded and AI-generated samples
4. **MIDI Import/Export**: Compatibility with other DAWs
5. **Plugin Support**: VST/AU effects and instruments
6. **Mobile Apps**: iOS and Android clients
7. **Marketplace**: User-created presets and templates

## Conclusion

This architecture provides a solid foundation for QuillMusic while remaining flexible enough to integrate cutting-edge AI models as they emerge. The separation of concerns between frontend, API, and workers allows each component to scale independently and evolve at its own pace.
