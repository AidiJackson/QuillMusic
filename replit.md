# QuillMusic - Replit Project Documentation

## Overview

QuillMusic is an AI Music Studio that enables users to create full songs with vocals, mastering, and DAW-style creation. This is a full-stack application featuring:

- **Frontend**: React + TypeScript + Vite with Tailwind CSS
- **Backend**: FastAPI (Python) with async job processing
- **Database**: Redis for job queue management
- **AI Features**: Song blueprint generation and render engine (currently with mock implementations, ready for real AI model integration)

## Project Status

✅ **Phase 1 Complete**: Fully functional scaffold with:
- Modern React frontend with professional dark theme UI
- FastAPI backend with modular, typed architecture
- Redis + RQ job queue system for asynchronous processing
- Comprehensive testing infrastructure
- Ready for AI model integration in Phase 2

## Project Structure

```
QuillMusic/
├── quillmusic/
│   ├── backend/          # FastAPI backend (Python 3.11)
│   │   ├── app/
│   │   │   ├── api/      # API routes
│   │   │   ├── core/     # Config and dependencies
│   │   │   ├── models/   # Database models (future)
│   │   │   ├── schemas/  # Pydantic schemas
│   │   │   ├── services/ # Business logic and AI engines
│   │   │   └── workers/  # Background job workers
│   │   └── tests/        # Pytest tests
│   └── frontend/         # React frontend (Node.js 20)
│       └── src/
│           ├── components/ # React components
│           ├── lib/        # Utilities and API client
│           ├── pages/      # Page components
│           └── types/      # TypeScript types
├── docs/                 # Documentation
├── start-backend.sh      # Backend startup script (dev)
├── start-production.sh   # Production startup script
└── README.md
```

## Architecture

### Frontend (Port 5000)
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + shadcn/ui components
- **Routing**: React Router
- **API Communication**: Custom API client with fetch

### Backend (Port 8000 in dev, 5000 in production)
- **Framework**: FastAPI
- **Language**: Python 3.11
- **Job Queue**: Redis + RQ
- **API Design**: RESTful with automatic OpenAPI documentation

### Key Features
1. **AI Song Builder**: Generate song structures, lyrics, and styles from text prompts
2. **Render Engine**: Asynchronous audio generation system (currently mock, ready for real AI)
3. **Render Queue**: Track and manage rendering jobs
4. **Manual Creator**: DAW-style interface (coming in Phase 5)

## Development Setup

### Running Locally

The project has two workflows configured:

1. **Backend** (port 8000): Runs Redis and FastAPI backend
2. **Frontend** (port 5000): Runs Vite dev server with HMR

Both workflows start automatically. The frontend proxies API requests to the backend at `/api`.

### Environment Configuration

- **Frontend**: Configured to run on `0.0.0.0:5000` with Replit domain allowlist
- **Backend**: Configured with CORS to allow Replit domains and localhost
- **Redis**: Runs as a background daemon process

## Deployment

The project is configured for VM deployment:

- **Build Step**: Builds the React frontend (`npm run build`)
- **Run Step**: Starts Redis and serves the backend on port 5000
- **Static Files**: Backend serves the built frontend from `/quillmusic/frontend/dist`

## API Documentation

When the backend is running, visit:
- API Docs: `http://localhost:8000/docs` (Swagger UI)
- API Schema: `http://localhost:8000/redoc` (ReDoc)

### Main Endpoints

- `GET /api/health` - Health check
- `POST /api/song-blueprints/` - Create song blueprint from prompt
- `POST /api/renders/` - Create render job
- `GET /api/renders/{job_id}` - Get render job status

## Tech Stack

### Frontend Dependencies
- React 18
- TypeScript 5
- Vite 5
- Tailwind CSS 3
- React Router 6
- Radix UI components
- Lucide React icons

### Backend Dependencies
- FastAPI 0.104
- Uvicorn 0.24
- Pydantic 2.5
- Redis 5.0
- RQ 1.15
- Pytest 7.4
- httpx 0.25

### System Dependencies
- Redis server
- Python 3.11
- Node.js 20

## Recent Changes

**2025-11-15**: Replit Import Setup
- Installed Python 3.11 and Node.js 20 modules
- Created missing `lib/apiClient.ts` and `lib/utils.ts` files
- Configured Vite to run on port 5000 with Replit host allowlist
- Updated backend CORS to allow Replit domains
- Installed all Python and Node.js dependencies
- Set up Redis system service
- Configured development and production workflows
- Added static file serving for production deployment
- Created startup scripts for development and production

## User Preferences

None recorded yet.

## Next Steps (Roadmap)

### Phase 2: Real Instrumental Generation (4-6 weeks)
- Integrate Stable Audio 2.0 or MusicGen
- Set up GPU infrastructure
- Add audio file storage and delivery

### Phase 3: Vocal Synthesis (6-8 weeks)
- Add Bark + RVC for AI vocals

### Phase 4: Mastering & Polish (3-4 weeks)
- Professional audio quality with automated mastering

### Phase 5: Manual Creator / DAW (12-16 weeks)
- Full DAW interface with timeline, MIDI editor, mixer

### Phase 6: Commercialization (8-12 weeks)
- User management and pricing tiers
- Payment integration

## Troubleshooting

### Frontend not loading
- Ensure port 5000 is not blocked
- Check that frontend workflow is running
- Verify Vite config has correct host settings

### Backend API errors
- Check Redis is running: `redis-cli ping`
- Verify backend workflow is running
- Check CORS settings if cross-origin issues

### Build failures
- Clear node_modules and reinstall: `cd quillmusic/frontend && rm -rf node_modules && npm install`
- Clear Python cache: `cd quillmusic/backend && find . -type d -name __pycache__ -exec rm -rf {} +`

## Testing

### Backend Tests
```bash
cd quillmusic/backend
pytest
```

### Frontend Build
```bash
cd quillmusic/frontend
npm run build
```

## Contributing

See the main [README.md](./README.md) for contribution guidelines and development workflow.

---

**Last Updated**: November 15, 2025
**Version**: 0.1.0
**Status**: Phase 1 Complete - Ready for Phase 2 development
