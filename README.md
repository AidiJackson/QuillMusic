# QuillMusic

![QuillMusic Logo](https://via.placeholder.com/150x150.png?text=QuillMusic)

**AI Music Studio – Full songs, vocals, mastering & DAW-style creation.**

QuillMusic is a next-generation music production platform that combines the power of AI with professional DAW features. Create complete songs from simple text prompts, or dive deep with manual editing tools for full creative control.

## 🎵 Features

### Current (Phase 1: Scaffold)
- ✅ **AI Song Blueprint Generator**: Generate song structures, lyrics, and styles from text prompts
- ✅ **Fake Render Engine**: Development-ready system with mock audio generation
- ✅ **Modern React Frontend**: Clean, professional UI with dark theme
- ✅ **FastAPI Backend**: Modular, typed, and ready for real AI models
- ✅ **Job Queue System**: Redis + RQ for asynchronous processing
- ✅ **Comprehensive Tests**: Backend tests with pytest

### Coming Soon (Phases 2-7)
- 🔜 **Real Instrumental Generation**: Stable Audio 2.0 or MusicGen integration
- 🔜 **Vocal Synthesis**: AI-powered singing and speech
- 🔜 **Professional Mastering**: Automated mixing and mastering
- 🔜 **Manual Creator / DAW**: Full timeline editor with MIDI, mixing, effects
- 🔜 **Collaboration Tools**: Share and work on projects together
- 🔜 **Stem Exports**: Download individual tracks (drums, bass, vocals, etc.)

## 📁 Project Structure

```
QuillMusic/
├── quillmusic/
│   ├── backend/          # FastAPI backend
│   │   ├── app/
│   │   │   ├── api/      # API routes
│   │   │   ├── core/     # Config and dependencies
│   │   │   ├── models/   # Database models (future)
│   │   │   ├── schemas/  # Pydantic schemas
│   │   │   ├── services/ # Business logic and AI engines
│   │   │   └── workers/  # Background job workers
│   │   ├── tests/        # Pytest tests
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── pytest.ini
│   └── frontend/         # React frontend
│       ├── src/
│       │   ├── components/ # React components
│       │   ├── lib/        # Utilities and API client
│       │   ├── pages/      # Page components
│       │   └── types/      # TypeScript types
│       ├── package.json
│       ├── vite.config.ts
│       └── tailwind.config.js
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md   # System architecture
│   ├── UI_FIGMA_BRIEF.md # Design system
│   ├── ROADMAP.md        # Development roadmap
│   ├── MUSIC_MODELS.md   # AI model research
│   └── PRICING.md        # Pricing strategy
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)

### Unified Dev Experience

**One command runs everything!**

#### On Replit (Easiest!)

Just click the **Run** button!

The `.replit` configuration automatically:
- Starts Redis in daemon mode
- Starts the FastAPI backend on port 8000
- Starts the Vite frontend dev server on port 5000
- The Replit preview shows the React UI

**Development branch:** `claude/unified-dev-runner-013TKA1cg1SCS1zm96jZrfGm`

#### Local Development

**One command to run everything:**

```bash
# Clone the repository
git clone https://github.com/AidiJackson/QuillMusic.git
cd QuillMusic

# Checkout the development branch
git checkout claude/unified-dev-runner-013TKA1cg1SCS1zm96jZrfGm

# Install dependencies (first time only)
npm install                                      # Root dev runner (concurrently)
cd quillmusic/backend && pip install -r requirements.txt && cd ../..
cd quillmusic/frontend && npm install && cd ../..

# Start everything together
npm run dev

# That's it! 🎉
# Backend: http://localhost:8000 (API docs: http://localhost:8000/docs)
# Frontend: http://localhost:5000
```

The unified `npm run dev` command automatically:
- ✅ Starts Redis server in daemon mode
- ✅ Starts FastAPI backend on port 8000 with auto-reload
- ✅ Starts Vite frontend dev server on port 5000
- ✅ Colored output (blue for backend, green for frontend)
- ✅ Vite proxy forwards `/api` requests to the backend seamlessly

### Alternative: Manual Setup (Legacy)

<details>
<summary>Click to expand manual setup instructions</summary>

#### Backend

```bash
# Navigate to backend
cd quillmusic/backend

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn app.main:app --reload --port 8000

# Run tests
python -m pytest
```

#### Frontend

```bash
# Navigate to frontend
cd quillmusic/frontend

# Install dependencies
npm install

# Start development server
npm run dev

# The frontend will be available at http://localhost:5173
```

</details>

### Using Docker Compose

```bash
# Start services (Redis + Backend)
docker-compose up -d

# The API will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

## 🎨 Usage

### 1. Generate a Song Blueprint

1. Navigate to **AI Song Builder**
2. Enter a prompt describing your song (e.g., "A dreamy synthwave track about late night drives")
3. Select genre and mood
4. Adjust optional parameters (BPM, key, duration)
5. Click **Generate Blueprint**

The system will create:
- Complete song structure (intro, verses, chorus, etc.)
- Generated lyrics for each section
- Vocal style configuration
- Production notes

### 2. Render a Song

1. After generating a blueprint, click **Send to Render Engine**
2. Navigate to **Render Queue**
3. Check job status by entering the job ID
4. Download the audio when ready

**Note**: Current version uses fake engines. Phase 2+ will integrate real AI models.

### 3. Manual Creator (Coming Soon)

The Manual Creator will provide a full DAW interface for:
- Multi-track timeline editing
- MIDI piano roll
- Audio effects and mixing
- Automation
- Collaboration

## 🧪 Testing

### Backend Tests

```bash
cd quillmusic/backend
python -m pytest

# With coverage
python -m pytest --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_song_blueprints.py
```

**Or run from root:**
```bash
npm run test:backend
```

### Frontend Build

```bash
cd quillmusic/frontend
npm run build

# Preview production build
npm run preview
```

**Or build from root:**
```bash
npm run build:frontend
```

### Available Root Scripts

From the project root, you can run:
- `npm run dev` - Start both backend and frontend (unified dev experience)
- `npm run test:backend` - Run backend tests
- `npm run test:frontend` - Build frontend (validates TypeScript)
- `npm run build:frontend` - Build frontend for production
- `npm run install:all` - Install all dependencies (backend + frontend)

## 📚 Documentation

- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)**: System architecture and design decisions
- **[UI_FIGMA_BRIEF.md](./docs/UI_FIGMA_BRIEF.md)**: UI design system and Figma guide
- **[ROADMAP.md](./docs/ROADMAP.md)**: Development phases and timeline
- **[MUSIC_MODELS.md](./docs/MUSIC_MODELS.md)**: AI music model research and comparison
- **[PRICING.md](./docs/PRICING.md)**: Pricing tiers and monetization strategy

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and settings
- **Redis + RQ**: Job queue for async processing
- **pytest**: Testing framework
- **Docker**: Containerization

### Frontend
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Beautiful component library
- **React Router**: Client-side routing
- **Sonner**: Toast notifications

### AI Models (Planned)
- **Stable Audio 2.0**: Instrumental generation
- **MusicGen**: Alternative instrumental model
- **Bark + RVC**: Vocal synthesis
- **Matchering**: Automated mastering

## 🗺️ Roadmap

### Phase 1: Scaffold ✅ **CURRENT**
Complete skeleton with fake engines, clean architecture, and comprehensive docs.

### Phase 2: Real Instrumental Generation (4-6 weeks)
Integrate Stable Audio 2.0 or MusicGen for real music generation.

### Phase 3: Vocal Synthesis (6-8 weeks)
Add Bark + RVC for AI-generated vocals.

### Phase 4: Mastering & Polish (3-4 weeks)
Professional audio quality with automated mastering.

### Phase 5: Manual Creator / DAW (12-16 weeks)
Full DAW interface with timeline, MIDI editor, mixer, effects.

### Phase 6: Commercialization (8-12 weeks)
Launch with pricing tiers, user management, and scaling infrastructure.

### Phase 7: Advanced Features (Ongoing)
Collaboration, marketplace, integrations, mobile apps, and more.

See [ROADMAP.md](./docs/ROADMAP.md) for detailed plans.

## 💰 Pricing (Planned)

QuillMusic will follow a freemium model:

- **Free**: 3 blueprints, 2 renders/month, 60s max, watermarked
- **Creator ($9.99/mo)**: 25 blueprints, 15 renders, 5min max, commercial rights
- **Pro Studio ($29.99/mo)**: Unlimited blueprints, 100 renders, DAW access, stems
- **Pro+ ($99/mo)**: Unlimited everything, custom voices, API access
- **Enterprise**: Custom pricing for businesses

See [PRICING.md](./docs/PRICING.md) for full details.

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report Bugs**: Open an issue with details and reproduction steps
2. **Suggest Features**: Share your ideas in the discussions
3. **Submit PRs**: Fork, create a feature branch, and submit a pull request
4. **Improve Docs**: Help us make documentation clearer
5. **Test**: Try the platform and provide feedback

### Development Workflow

```bash
# Fork and clone
git clone https://github.com/your-username/QuillMusic.git
cd QuillMusic

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
# ... code, test, commit ...

# Push and create PR
git push origin feature/your-feature-name
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

- **Stability AI** for Stable Audio research
- **Meta AI** for MusicGen and AudioCraft
- **Suno AI** for Bark TTS
- **shadcn** for the amazing UI component library
- The open-source AI music community

## 📞 Contact & Support

- **Email**: support@quillmusic.ai (planned)
- **Discord**: [Join our community](https://discord.gg/quillmusic) (planned)
- **Twitter**: [@QuillMusicAI](https://twitter.com/QuillMusicAI) (planned)
- **GitHub Issues**: [Report bugs](https://github.com/AidiJackson/QuillMusic/issues)

## 🎯 Current Status

**Phase 1 Complete**: QuillMusic is now a fully functional scaffold with:
- Clean, typed backend ready for AI model integration
- Modern, responsive frontend with professional UI
- Job queue system for async processing
- Comprehensive documentation
- Testing infrastructure

**Next Steps**:
- Integrate real instrumental AI model (Stable Audio 2.0 or MusicGen)
- Set up GPU infrastructure for inference
- Add audio file storage and delivery
- Begin beta testing with early users

---

Built with ❤️ by the QuillMusic team

**Status**: Phase 1 Complete | **Version**: 0.1.0 | **Last Updated**: 2025
