# External Instrumental Audio Engine - Setup & Usage

## Overview

QuillMusic supports real instrumental generation via external audio providers (like Stable Audio, MusicGen, etc.) through the `ExternalInstrumentalEngine`. This guide explains how to configure and use this feature.

## Architecture

QuillMusic has two engine modes for instrumental rendering:

1. **FakeInstrumentalEngine** (default) - Development mode that generates fake audio URLs for testing
2. **ExternalInstrumentalEngine** - Production mode that calls real AI audio generation APIs

The engine is selected via the `engine_type` parameter when creating a render job:
- `engine_type: "fake"` → Uses FakeInstrumentalEngine
- `engine_type: "external_http"` → Uses ExternalInstrumentalEngine (requires configuration)

## Backend Configuration

### Environment Variables

Set these environment variables to enable external audio generation:

```bash
# Required for external_http engine
QUILLMUSIC_AUDIO_PROVIDER=stable_audio_http
QUILLMUSIC_AUDIO_API_BASE_URL=https://api.your-audio-provider.com
QUILLMUSIC_AUDIO_API_KEY=your-api-key-here
```

### Configuration Options

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `QUILLMUSIC_AUDIO_PROVIDER` | Yes (for external) | `"fake"` | Audio provider type (`"fake"` or `"stable_audio_http"`) |
| `QUILLMUSIC_AUDIO_API_BASE_URL` | Yes (for external) | `None` | Base URL for the audio generation API |
| `QUILLMUSIC_AUDIO_API_KEY` | Yes (for external) | `None` | API key for authentication |

### Example .env File

```bash
# QuillMusic Backend - External Audio Configuration

# Audio Provider Settings
QUILLMUSIC_AUDIO_PROVIDER=stable_audio_http
QUILLMUSIC_AUDIO_API_BASE_URL=https://api.stabilityai.com
QUILLMUSIC_AUDIO_API_KEY=sk-your-stability-ai-api-key-here

# Other settings...
QUILLMUSIC_DEBUG=true
QUILLMUSIC_API_PREFIX=/api
```

## How It Works

### 1. Request Flow

When you make a render request with `engine_type: "external_http"`:

```python
POST /api/instrumental/render
{
  "source_type": "blueprint",
  "source_id": "song_123",
  "engine_type": "external_http",  # Use external engine
  "model": "Stable Audio 2.0",      # Optional: specific model
  "duration_seconds": 60
}
```

### 2. Engine Selection

The `get_instrumental_engine()` factory function validates configuration:

```python
# From app/services/instrumental_engine.py
engine = get_instrumental_engine("external_http", settings)

# Validates:
# - AUDIO_PROVIDER == "stable_audio_http"
# - AUDIO_API_BASE_URL is set
# - AUDIO_API_KEY is set

# Returns: ExternalInstrumentalEngine(base_url, api_key)
```

### 3. Prompt Generation

The engine builds a text prompt from your blueprint or manual project:

**From Blueprint:**
```
"Instrumental music: Pop genre, Happy mood, 120 BPM, in C,
 with sections: intro, verse, chorus, verse, chorus, bridge, chorus, outro"
```

**From Manual Project:**
```
"Instrumental music: 128 BPM, in Am,
 with instruments: drums, bass, chords, lead, 4 patterns"
```

### 4. API Call

The engine makes an HTTP POST request:

```http
POST https://api.your-provider.com/v2/generate/audio
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "model": "music-gen-v1",
  "prompt": "Instrumental music: Pop genre...",
  "seconds_total": 60
}
```

### 5. Response Handling

Expected API response:
```json
{
  "id": "job-abc123",
  "status": "ready",
  "audio_url": "https://cdn.provider.com/audio/job-abc123.mp3"
}
```

The engine returns `(audio_url, duration_seconds)` to the job service.

## Error Handling

### Configuration Errors

If external engine is requested but not properly configured:

```json
{
  "id": "job-xyz",
  "status": "failed",
  "error_message": "Configuration error: External audio provider missing AUDIO_API_KEY configuration"
}
```

### API Errors

If the external provider returns an error:

```json
{
  "id": "job-xyz",
  "status": "failed",
  "error_message": "Audio provider error: Audio API returned status 500: Internal server error"
}
```

### Network Errors

If there's a connection issue:

```json
{
  "id": "job-xyz",
  "status": "failed",
  "error_message": "Audio provider error: HTTP error calling audio API: Connection refused"
}
```

## Frontend Usage

### Using the Instrumental Studio UI

1. **Select Engine Type**: In the "Render Settings" section, choose:
   - "Fake Demo Engine" for development/testing
   - "External Real Audio (API)" for real generation

2. **Configure Settings**:
   - **Model** (if external): Select from available models
   - **Duration**: Specify length or leave empty for auto-calculation
   - **Style Hint**: Optional text guidance for the AI
   - **Quality**: draft/standard/high

3. **Render**: Click "Render Instrumental" button

### Feature Detection

The frontend can check if external audio is available:

```typescript
const config = await apiClient.getConfig()

if (config.features.external_instrumental_available) {
  // External audio is properly configured
  console.log("Available models:", config.features.audio_provider.models)
} else {
  // Only fake engine available
  console.log("External audio not configured")
}
```

### API Client Usage

```typescript
import { apiClient } from '@/lib/apiClient'

// Render with external engine
const job = await apiClient.instrumental.render({
  source_type: 'blueprint',
  source_id: 'song_abc123',
  engine_type: 'external_http',
  model: 'Stable Audio 2.0',
  duration_seconds: 120,
})

console.log(job.status)  // "processing" or "ready" or "failed"
console.log(job.audio_url)  // URL when ready
```

## Testing

### Running Tests

All instrumental tests include external engine scenarios:

```bash
cd quillmusic/backend
python -m pytest tests/test_instrumental*.py -v
```

Tests cover:
- ✅ Configuration validation
- ✅ Successful rendering (blueprint & manual project)
- ✅ HTTP error handling
- ✅ Invalid response handling
- ✅ Network exception handling

### Manual Testing

1. **Test with Fake Engine** (no setup needed):
   ```bash
   curl -X POST http://localhost:8000/api/instrumental/render \
     -H "Content-Type: application/json" \
     -d '{
       "source_type": "blueprint",
       "source_id": "song_123",
       "engine_type": "fake"
     }'
   ```

2. **Test Configuration Check**:
   ```bash
   curl http://localhost:8000/api/config
   ```

3. **Test with External Engine** (requires valid config):
   ```bash
   curl -X POST http://localhost:8000/api/instrumental/render \
     -H "Content-Type: application/json" \
     -d '{
       "source_type": "blueprint",
       "source_id": "song_123",
       "engine_type": "external_http",
       "model": "Stable Audio 2.0"
     }'
   ```

## Supported Providers

### Stable Audio (Stability AI)

**Provider value:** `stable_audio_http`

```bash
QUILLMUSIC_AUDIO_PROVIDER=stable_audio_http
QUILLMUSIC_AUDIO_API_BASE_URL=https://api.stabilityai.com
QUILLMUSIC_AUDIO_API_KEY=sk-your-key
```

**Models:**
- Stable Audio 2.0
- Stable Audio Open

### MusicGen (Future)

**Provider value:** `musicgen`

```bash
QUILLMUSIC_AUDIO_PROVIDER=musicgen
QUILLMUSIC_AUDIO_API_BASE_URL=https://api.your-musicgen-provider.com
QUILLMUSIC_AUDIO_API_KEY=your-key
```

**Models:**
- MusicGen Small
- MusicGen Medium
- MusicGen Large

## Development vs Production

### Development Mode
- Use `engine_type: "fake"`
- No API keys needed
- Instant responses
- Returns fake URLs for testing UI

### Production Mode
- Use `engine_type: "external_http"`
- Requires API configuration
- Real audio generation
- Returns actual audio URLs
- May take 10-60 seconds depending on provider

## Troubleshooting

### "Configuration error" when using external engine

**Problem:** Job fails immediately with configuration error

**Solution:** Check that all three env vars are set:
```bash
echo $QUILLMUSIC_AUDIO_PROVIDER
echo $QUILLMUSIC_AUDIO_API_BASE_URL
echo $QUILLMUSIC_AUDIO_API_KEY
```

### "Audio provider error: status 401"

**Problem:** API key is invalid

**Solution:** Verify your API key is correct and active

### "Audio provider error: status 429"

**Problem:** Rate limit exceeded

**Solution:** Wait and retry, or upgrade your API plan

### External engine not showing in UI

**Problem:** Only "Fake Demo Engine" visible

**Solution:** Check `/api/config` endpoint - `features.external_instrumental_available` should be `true`

## Next Steps

To add support for additional providers:

1. Add new provider value to `config.py`:
   ```python
   AUDIO_PROVIDER: Literal["fake", "stable_audio_http", "musicgen"] = "fake"
   ```

2. Update `ExternalInstrumentalEngine._post_generate()` to handle different API formats

3. Add provider-specific model lists in `config.py` route

4. Update tests with new provider scenarios

## API Reference

### POST /api/instrumental/render

Create an instrumental render job.

**Request:**
```typescript
{
  source_type: "blueprint" | "manual_project"
  source_id: string
  engine_type?: "fake" | "external_http"  // default: "fake"
  model?: string | null                    // e.g., "Stable Audio 2.0"
  duration_seconds?: number | null         // 1-600 seconds
  style_hint?: string | null              // Optional guidance
  quality?: "draft" | "standard" | "high"
}
```

**Response:**
```typescript
{
  id: string                    // Job ID
  status: "queued" | "processing" | "ready" | "failed"
  engine_type: "fake" | "external_http"
  model?: string | null
  source_type: "blueprint" | "manual_project"
  source_id: string
  duration_seconds?: number | null
  audio_url?: string | null     // Available when status="ready"
  error_message?: string | null // Available when status="failed"
  created_at: string
  updated_at: string
}
```

### GET /api/config

Get application configuration and feature flags.

**Response:**
```typescript
{
  app_name: string
  app_version: string
  features: {
    external_instrumental_available: boolean
    audio_provider: {
      provider: string       // "fake" | "stable_audio_http" | etc.
      available: boolean
      models: string[]       // Available AI models
    }
  }
}
```

---

Built with ❤️ by the QuillMusic team
