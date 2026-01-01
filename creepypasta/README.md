# YAP: Creepypastas

Automatically generates full narration-style videos end-to-end using AI models (LLM, TTS, TTI). Pulls content from Reddit, writes scripts, generates speech, creates visuals, and assembles the final output with no manual editing.

## Versions

### v1

First version proof of concept. Result video: https://youtu.be/l-CNBpAGitw

**Technologies:**
- [PRAW](https://praw.readthedocs.io/) - Reddit API
- [CoquiTTS](https://github.com/coqui-ai/TTS) - Text-to-Speech
- [Ollama](https://ollama.com/) - Local LLM
- [HuggingFace](https://huggingface.co/) - Diffusion models

**Status:** Functional but required running each pipeline node individually with CSV tracking.

### v2 (Current)

A modular, graph-based pipeline with dependency injection for swapping models at any step.

**What's new:**
- [LangGraph](https://github.com/langchain-ai/langgraph) workflow orchestration with checkpointing
- Modular architecture with injectable LLM, TTS, and TTI providers
- Local editable packages (`llm`, `tts`, `tti`) for cross-project reuse
- SQLite persistence for resumable pipelines

## Setup (Windows)

### Prerequisites

#### 1. NVIDIA CUDA Toolkit

Download and install from [developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads)

**Check your CUDA version:**
```powershell
nvidia-smi
nvcc --version
```

Look at the top-right corner of `nvidia-smi` output for "CUDA Version: X.X". This is the maximum CUDA version your driver supports.

#### 2. FFmpeg with NVENC

```powershell
scoop install ffmpeg
```

Verify NVENC support:
```powershell
ffmpeg -encoders | findstr nvenc
```

#### 3. eSpeak NG (for TTS phonemizer)

```powershell
scoop install espeak.espeak-ng
```

Set environment variable (add to your PowerShell profile to make it permanent):
```powershell
$env:PHONEMIZER_ESPEAK_LIBRARY = "C:\Program Files\eSpeak NG\libespeak-ng.dll"
```

#### 4. uv (Python package manager)

```powershell
scoop install uv
```

Restart your terminal after installation.

### Installation

```powershell
git clone https://github.com/JStephenHuang/yap.git
cd yap/creepypasta/v2
```

**Select your CUDA version:**

Edit `pyproject.toml` and uncomment the PyTorch index you need (CUDA 12.6, CUDA 12.4)

Then install:

```powershell
uv sync
```

**Verify CUDA is detected:**

```powershell
uv run check-cuda
```

Expected output (with CUDA):
```
CUDA Available: True
CUDA Version: 12.6
Device: NVIDIA GeForce GTX XXXX
Device Count: n
```

### Environment Variables

Edit `.env` in `v2/` and add your API keys:

```env
# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# LLM APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...

# YouTube
YOUTUBE_CLIENT_SECRET_FILE=youtube_client_secret.json
YOUTUBE_CHANNEL_ID=your_channel_id
```

For Reddit API credentials: https://www.geeksforgeeks.org/python/how-to-get-client_id-and-client_secret-for-python-reddit-api-registration/

Place your YouTube OAuth client secret JSON at `v2/youtube_client_secret.json`.

## Usage

```powershell
# Scrape Reddit stories
uv run scrape-reddit

# Check queue
uv run python src/main.py status

# Process next story (with review prompts)
uv run python src/main.py run

# Process without reviews (auto-approve)
uv run python src/main.py run --no-review

# Resume from checkpoint
uv run python src/main.py resume <checkpoint_id>

# Rerun from specific step
uv run python src/main.py rerun <checkpoint_id> narrate  # or images, video, upload

# Restart from beginning
uv run python src/main.py restart <checkpoint_id>
```

## Configuration

All configuration files are in `v2/src/config/`. Swap models and tweak settings:

| File                  | What it controls                              |
| --------------------- | --------------------------------------------- |
| `tts.py`              | TTS provider, model, speaker voice, chunking  |
| `tti.py`              | Image model, dimensions, inference steps      |
| `video.py`            | Intro duration, crossfades, encoding          |
| `triage.py`           | LLM provider/model for story selection        |
| `refine_story.py`     | Story refinement prompts                      |
| `scene_prompts.py`    | Image prompt generation                       |
| `thumbnail_prompt.py` | Thumbnail prompt generation                   |
| `yt_metadata.py`      | YouTube title/description generation          |

## Output

Each run creates a folder in `v2/runs/{checkpoint_id}/`:

```
runs/a1b2c3d4/
├── metadata.json      # Pipeline state, use checkpoint_thread_id to resume
├── narration.wav      # Generated TTS audio
├── scene_*.png        # Generated images
├── thumbnail.png      # YouTube thumbnail
└── video.mp4          # Final video
```

Databases are stored in `v2/db/`:
- `threads.sqlite` - Scraped Reddit threads
- `checkpoints.sqlite` - LangGraph checkpoints

## Architecture

The project uses a modular monorepo structure:

```
yap/
├── llm/          # LLM provider abstraction (OpenAI, Groq, Ollama)
├── tts/          # TTS provider abstraction (NeuTTS)
├── tti/          # Image generation provider abstraction (Juggernaut)
└── creepypasta/
    └── v2/       # Main application using the providers
```

Each provider package is installed as an editable local package, allowing cross-project reuse while keeping provider implementations separate from the main application logic.

## Troubleshooting

### CUDA Not Detected

If PyTorch can't find CUDA:

1. Verify CUDA toolkit is in PATH: `nvcc --version`
2. Check your driver supports CUDA 12.6: `nvidia-smi`
3. Reinstall: `rm -r .venv; uv sync`

### Module Not Found Errors

The project uses local editable packages (`llm`, `tts`, `tti`). Make sure you're in the `v2/` directory and have run `uv sync`.
