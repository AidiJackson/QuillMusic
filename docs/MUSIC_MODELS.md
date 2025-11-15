# Music AI Models Research

## Overview

This document catalogs AI models suitable for QuillMusic's various components: instrumental generation, vocal synthesis, and mastering. Each model is evaluated on quality, speed, licensing, and compute requirements.

---

## Instrumental Generation Models

### 1. Stable Audio 2.0 (Stability AI)

**Description**: Text-to-music model that generates high-quality instrumentals up to 3 minutes at 44.1kHz.

**Pros**:
- High audio quality (44.1kHz stereo)
- Long-form generation (up to 3 minutes)
- Good style and genre control
- Active development and support

**Cons**:
- Requires significant GPU memory (16GB+ VRAM)
- Can be slow (30-60s for 30s of audio)
- License may restrict commercial use

**Technical Specs**:
- Model size: ~2-4GB
- Required VRAM: 16GB (A100/A6000 recommended)
- Generation speed: ~1-2x real-time on A100
- Output: 44.1kHz, stereo WAV

**Licensing**:
- Research license available
- Commercial license required for production
- Check https://stability.ai/license for current terms

**Integration Difficulty**: Medium
- Well-documented Python API
- Requires careful prompt engineering
- May need fine-tuning for specific genres

**Recommendation**: **Primary candidate** for Phase 2

---

### 2. MusicGen (Meta / AudioCraft)

**Description**: Open-source text-to-music model from Meta, part of the AudioCraft toolkit.

**Pros**:
- Fully open source (MIT license)
- Good quality for short clips (10-30s)
- Multiple model sizes (small, medium, large)
- Easy integration via HuggingFace

**Cons**:
- Quality degrades for longer generations
- Less control over musical structure
- May produce repetitive patterns

**Technical Specs**:
- Model sizes: 300MB (small) to 3.9GB (large)
- Required VRAM: 8GB (small), 16GB (large)
- Generation speed: Real-time on A100
- Output: 32kHz, mono or stereo

**Licensing**: MIT License (commercial use allowed)

**Integration Difficulty**: Easy
- Available on HuggingFace
- Good Python API
- Extensive documentation

**Recommendation**: **Good fallback** or for free tier with small model

---

### 3. Riffusion XL

**Description**: Fine-tuned Stable Diffusion model that generates spectrogram images, which are then converted to audio.

**Pros**:
- Novel approach with interesting capabilities
- Can do style transfer
- Open source

**Cons**:
- Audio quality limited by spectrogram conversion
- Artifacts and noise common
- Shorter generations (10-15s typical)
- Not true text-to-audio (uses image diffusion)

**Technical Specs**:
- Model size: ~5GB
- Required VRAM: 12GB
- Generation speed: 10-15s for 10s of audio
- Output: 44.1kHz, stereo

**Licensing**: CreativeML OpenRAIL-M License (permissive)

**Integration Difficulty**: Medium
- Requires spectrogram-to-audio conversion
- May need post-processing

**Recommendation**: **Not recommended** - too many artifacts for production use

---

### 4. AudioLDM 2 (Tsinghua University)

**Description**: Latent Diffusion Model for audio generation, supports text-to-audio and audio-to-audio.

**Pros**:
- Good audio quality
- Supports both music and sound effects
- Open source
- Flexible conditioning (text, audio)

**Cons**:
- Primarily designed for sound effects, not full music
- Limited musical structure control
- Shorter generations

**Technical Specs**:
- Model size: ~1.5GB
- Required VRAM: 10GB
- Generation speed: ~1x real-time
- Output: 48kHz, stereo

**Licensing**: Apache 2.0 (commercial friendly)

**Integration Difficulty**: Medium

**Recommendation**: **Consider for sound effects**, not primary music generation

---

### 5. Jukebox (OpenAI)

**Description**: Neural network that generates music with vocals in various styles.

**Pros**:
- Generates music with vocals
- Impressive quality for its time
- Open source

**Cons**:
- Very slow (hours for minutes of audio)
- Requires massive compute (32GB+ VRAM)
- Dated (2020) - newer models are better
- Not text-conditioned (uses artist/genre/lyrics tokens)

**Technical Specs**:
- Model size: ~1.5GB per level (3 levels)
- Required VRAM: 32GB+
- Generation speed: 10+ minutes for 20s of audio
- Output: Variable sample rates

**Licensing**: MIT License

**Integration Difficulty**: Hard
- Complex setup
- Extremely slow inference
- Requires significant engineering

**Recommendation**: **Not recommended** - superseded by newer models

---

## Instrumental Rendering Implementation Status

### Phase 3: Engine Abstraction (✅ Complete)

**What We Built:**
- Clean abstraction layer (`BaseInstrumentalEngine`) ready for any AI model
- FakeInstrumentalEngine with realistic duration calculations
- HttpInstrumentalEngine stub for external API integration
- Database persistence for render jobs and blueprints
- Full-featured Instrumental Studio UI

**Current Architecture:**
```python
class BaseInstrumentalEngine(ABC):
    @abstractmethod
    def render_from_blueprint(blueprint: SongBlueprintResponse) -> Tuple[str, int]:
        """Render from AI-generated blueprint"""
        pass

    @abstractmethod
    def render_from_manual_project(project, tracks, patterns) -> Tuple[str, int]:
        """Render from user-composed MIDI"""
        pass
```

**Supported Input Sources:**
1. **AI Song Blueprints**: Generated by LLM or fake blueprint engine
2. **Manual Creator Projects**: User-composed MIDI patterns with tracks

**Integration Readiness:**

To integrate any of the above instrumental models (Stable Audio 2.0, MusicGen, etc.):

1. Create new class inheriting `BaseInstrumentalEngine`
2. Implement `render_from_blueprint()` method:
   - Extract BPM, key, genre, mood from blueprint
   - Convert sections to prompt or MIDI
   - Call AI model API
   - Return `(audio_url, duration_seconds)`
3. Implement `render_from_manual_project()` method:
   - Extract tracks and patterns
   - Convert MIDI notes to model input format
   - Apply tempo and key from project settings
   - Return `(audio_url, duration_seconds)`
4. Update `get_instrumental_engine()` factory in `app/core/dependencies.py`
5. Add configuration (API keys, model settings) to `app/core/config.py`

**No other code changes needed** - the entire stack (API routes, frontend, database) is ready.

---

### Phase 5: External Instrumental Provider (Real Audio MVP) ✅ **COMPLETE**

**What We Built:**
- `ExternalInstrumentalEngine` class for HTTP-based audio generation
- Configuration system for external audio providers
- Error handling for configuration and API failures
- Comprehensive test suite with mocked HTTP calls
- Frontend UI with engine selection

**External Audio Provider Support:**

QuillMusic now supports external audio generation APIs through a configurable HTTP engine:

**Configuration (Backend .env):**
```bash
QUILLMUSIC_AUDIO_PROVIDER=stable_audio_http  # or "fake" for demo
QUILLMUSIC_AUDIO_API_BASE_URL=https://api.your-provider.com
QUILLMUSIC_AUDIO_API_KEY=sk-your-api-key
```

**How It Works:**
1. User selects "External Real Audio (API)" engine in Instrumental Studio
2. Backend validates configuration when creating engine instance
3. External engine converts blueprint/manual project to text prompt
4. HTTP POST request sent to external API with prompt and duration
5. API returns audio URL which is stored in the job
6. If configuration is missing or API fails, job status = "failed" with clear error message

**Prompt Generation:**
- **From Blueprint**: Combines genre, mood, BPM, key, and section structure into descriptive prompt
- **From Manual Project**: Combines tempo, key, instrument types, and pattern count into prompt

**Error Handling:**
- `ConfigurationError`: Missing or invalid AUDIO_PROVIDER, AUDIO_API_BASE_URL, or AUDIO_API_KEY
- `ExternalAudioError`: HTTP errors, invalid responses, or network failures
- All errors propagate to job.error_message for user visibility

**Test Coverage:**
- Configuration validation tests (missing provider, base URL, API key)
- Successful rendering from blueprint and manual project
- HTTP error handling (500 responses, invalid JSON, network exceptions)
- All tests use mocked httpx.post - no real HTTP calls

**API Contract:**
```python
# Request
POST {base_url}/v2/generate/audio
Headers:
  Authorization: Bearer {api_key}
  Content-Type: application/json
Body:
  {
    "model": "music-gen-v1",
    "prompt": "Instrumental music: EDM genre, Energetic mood, 128 BPM, in Am, with sections: Intro, Buildup, Drop, Breakdown, Drop, Outro",
    "seconds_total": 120
  }

# Expected Response
{
  "id": "job-123",
  "status": "ready",
  "audio_url": "https://cdn.example.com/audio/job-123.mp3"
}
```

**Integration Options:**

This implementation is **provider-agnostic** and can work with:
- Stable Audio API (when available)
- MusicGen API endpoints
- Custom self-hosted models
- Any HTTP API following the contract above

**Next Steps for Real Model Integration:**

When ready to integrate real models, we recommend this order:

1. **Start with MusicGen (Easy Win)**:
   - Fully open source (MIT)
   - Available on HuggingFace
   - Can run on smaller GPUs (8-16GB)
   - Good for validating the integration pipeline
   - Use for "draft" quality tier

2. **Upgrade to Stable Audio 2.0 (Production Quality)**:
   - Better quality and longer outputs
   - Use for "standard" and "high" quality tiers
   - Requires licensing and bigger GPU (A100)
   - API integration via Replicate or self-hosted

3. **Manual Project Rendering (Advanced)**:
   - Convert MIDI patterns to audio
   - May require different approach (synthesizer + effects)
   - Consider hybrid: render MIDI with sampled instruments, then apply AI processing

**Estimated Integration Time:**
- MusicGen: 1-2 weeks (HuggingFace API)
- Stable Audio 2.0: 2-3 weeks (licensing + GPU setup)
- Manual Project rendering: 3-4 weeks (MIDI → audio pipeline)

---

## Vocal Synthesis Models

### 1. Bark (Suno AI)

**Description**: Transformer-based text-to-speech model that can generate speech, singing, and music.

**Pros**:
- Supports singing (not just speech)
- Multiple languages
- Emotional expression
- Open source
- Non-verbal sounds (laughter, sighs)

**Cons**:
- Quality varies significantly
- Limited control over pitch/timing
- Can be slow
- Voice consistency issues

**Technical Specs**:
- Model size: ~10GB
- Required VRAM: 8-12GB
- Generation speed: ~2-5x slower than real-time
- Output: 24kHz, mono

**Licensing**: MIT License (with ethical use guidelines)

**Integration Difficulty**: Medium
- Good Python API
- Voice cloning requires examples
- Prompt engineering needed

**Recommendation**: **Primary candidate** for initial vocal integration

---

### 2. OpenVPI / DiffSinger

**Description**: Neural singing voice synthesis system, popular in the vocaloid community.

**Pros**:
- High-quality singing
- Precise pitch and timing control
- Open source
- Active community

**Cons**:
- Requires MIDI + phoneme input (not text-to-speech)
- Need to train voices (time-consuming)
- Mandarin-focused (English support limited)

**Technical Specs**:
- Model size: ~500MB per voice
- Required VRAM: 6GB
- Generation speed: Faster than real-time
- Output: 44.1kHz, mono

**Licensing**: MIT License

**Integration Difficulty**: Hard
- Requires MIDI generation
- Need phoneme conversion
- Voice training complex

**Recommendation**: **Phase 3-4** after we have MIDI generation

---

### 3. RVC (Retrieval-based Voice Conversion)

**Description**: Voice conversion model that can change one voice to sound like another.

**Pros**:
- Extremely high quality
- Real-time capable
- Can clone voices with <1min of audio
- Open source

**Cons**:
- Requires source audio (can't generate from scratch)
- Need to train voice models
- Quality depends on source material

**Technical Specs**:
- Model size: ~200MB per voice
- Required VRAM: 4-6GB
- Generation speed: Real-time
- Output: 48kHz, mono

**Licensing**: MIT License

**Integration Difficulty**: Medium
- Good tooling available
- Voice training straightforward
- Can chain with TTS

**Recommendation**: **Combine with Bark** - use Bark to generate, RVC to improve quality

---

### 4. VALL-E (Microsoft)

**Description**: Neural codec language model for text-to-speech with voice cloning.

**Pros**:
- State-of-the-art quality
- 3-second voice cloning
- Emotional expression
- Multiple languages

**Cons**:
- Not publicly released
- Closed source
- Likely expensive API
- Singing capabilities unclear

**Technical Specs**:
- Unknown (not released)

**Licensing**: Proprietary (if/when released)

**Recommendation**: **Monitor for release** - would be game-changer if available

---

### 5. Tortoise TTS

**Description**: High-quality text-to-speech with voice cloning capabilities.

**Pros**:
- Excellent speech quality
- Voice cloning with short samples
- Open source
- Emotional control

**Cons**:
- Very slow (minutes for seconds of audio)
- Not designed for singing
- High compute requirements

**Technical Specs**:
- Model size: ~4GB
- Required VRAM: 8GB
- Generation speed: 10-20x slower than real-time
- Output: 24kHz, mono

**Licensing**: Apache 2.0

**Integration Difficulty**: Medium

**Recommendation**: **Not ideal for music** - better for narration/dialogue

---

## Mastering & Audio Processing

### 1. LANDR API

**Description**: Commercial API for AI-powered mastering.

**Pros**:
- Professional quality
- Easy integration (API)
- No local compute needed
- Proven track record

**Cons**:
- Costs per master
- Less customization
- Dependency on third party

**Pricing**: ~$9 per master (varies by tier)

**Recommendation**: **Consider for MVP** - offload mastering complexity initially

---

### 2. Matchering (Open Source)

**Description**: Python library for AI-assisted mastering using reference tracks.

**Pros**:
- Free and open source
- Reference-based mastering
- Local processing
- Good results

**Cons**:
- Requires good reference track
- Less "AI", more traditional DSP
- Manual parameter tuning

**Licensing**: GPL-3.0

**Integration Difficulty**: Easy

**Recommendation**: **Primary DIY option** for Phase 4

---

### 3. iZotope Ozone (Plugin)

**Description**: Industry-standard mastering plugin with AI assistant.

**Pros**:
- Professional quality
- AI-assisted settings
- Widely used

**Cons**:
- Desktop plugin (not server-friendly)
- Expensive licensing
- Not designed for automation

**Recommendation**: **Reference standard** but not practical for automation

---

### 4. Custom Mastering Chain

**Build our own using:**
- **pyloudnorm**: Loudness normalization (LUFS)
- **pedalboard** (Spotify): Python audio effects
- **pydub**: Audio manipulation
- **librosa**: Audio analysis

**Pros**:
- Full control
- No external dependencies
- No per-use costs
- Can iterate and improve

**Cons**:
- Time to develop
- Need audio engineering expertise
- Won't match pro tools initially

**Recommendation**: **Final target** - build incrementally

---

## Model Hosting Options

### Local / Self-Hosted
**Pros**: Full control, no API costs, data privacy
**Cons**: High upfront cost, maintenance burden

**Recommended GPU**: NVIDIA A100 (40GB) or A6000 (48GB)
**Cost**: $1-2/hour (cloud), $10k-20k (purchase)

### Cloud APIs
**Options**:
- **Replicate**: Easy model hosting, pay-per-use
- **HuggingFace Inference**: Managed model endpoints
- **Banana.dev**: Optimized for ML inference
- **AWS SageMaker**: Enterprise-grade

**Pros**: No infrastructure management, easy scaling
**Cons**: Higher per-generation cost, vendor lock-in

### Hybrid Approach
**Strategy**:
- Use cloud APIs for MVP and testing
- Self-host for production at scale
- Keep APIs as fallback

---

## Recommended Stack for QuillMusic

### Phase 3 (Instrumental Engine Abstraction) ✅ **COMPLETE**
**Status**: Engine architecture implemented with fake engine
**Next**: Integrate real AI models (Phase 4)

### Phase 4 (Real Instrumental AI Models)
**Primary**: Stable Audio 2.0 (licensed)
**Fallback**: MusicGen (open source)
**Hosting**: Replicate API → Self-hosted A100

### Phase 5 (Vocals)
**Primary**: Bark + RVC chain
**Alternative**: Wait for VALL-E public release
**Hosting**: Self-hosted (voice models proprietary)

### Phase 6 (Mastering)
**Initial**: Matchering (open source)
**Future**: Custom chain with pedalboard + pyloudnorm

### Long-term
- Fine-tune models on user feedback
- Explore custom model training
- Build genre-specific models

---

## Evaluation Criteria

When selecting models, consider:

1. **Quality**: MOS (Mean Opinion Score) > 3.5
2. **Speed**: < 2x real-time for good UX
3. **Cost**: < $0.10 per generation at scale
4. **Licensing**: Commercial use allowed
5. **Maintainability**: Active development, good docs
6. **Scalability**: Can handle 100+ req/min

---

## Benchmarking Plan

Before integrating any model:

1. Generate 100 test samples
2. Measure generation time
3. Conduct blind listening tests (MOS)
4. Test edge cases (very long, very short, weird prompts)
5. Measure GPU memory usage
6. Calculate cost at scale
7. Check output consistency

---

## Staying Current

AI music models evolve rapidly. Monitor:
- **Papers**: ArXiv, Papers with Code
- **Repos**: HuggingFace, GitHub trending
- **Communities**: r/MachineLearning, Discord servers
- **Companies**: Stability AI, Meta AI, Suno, Udio

Update this document quarterly with new findings.

---

## Conclusion

The current AI music landscape offers strong options for all our needs:
- **Stable Audio 2.0** for instrumentals
- **Bark + RVC** for vocals
- **Matchering** for mastering

This stack should get us to MVP. As models improve, we can swap them transparently thanks to our abstraction layer.

Next review: [3 months from now]
