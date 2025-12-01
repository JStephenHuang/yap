# YAP: Creepypastas

## v1

Here is a result video from the first version of YAP:

https://youtu.be/l-CNBpAGitw

Everything was generated using transformer and diffusion models (LLM, TTS, TTI).

**What it does:** Automatically generates full narration-style videos end-to-end, pulling content, writing scripts, generating speech, creating visuals, and assembling the final output with no manual editing.

Resources:

- [PRAW](https://praw.readthedocs.io/)
- [CoquiTTS](https://github.com/coqui-ai/TTS)
- [Ollama](https://ollama.com/)
- [HuggingFace](https://huggingface.co/)

Running the pipeline was a nightmare, you needed to run each node individually and all the data was tracked by a huge csv.

### Setup

to be filled

## v2

Version 2 is in development and will allow the user to easily **inject** new models into **different** steps.

**What’s new:** A modular pipeline that lets users swap in their own LLMs, TTS engines, or image models, making the system flexible for different content workflows.

Resources:

- ...v1.ressources
- [LangGraph](https://github.com/langchain-ai/langgraph)
- SQLite

### Setup (Windows)

#### 1. Dependencies

**NVIDIA CUDA Toolkit:**
Download and install from [developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads) (Windows → x86_64 → exe)

```powershell
nvidia-smi          # verify driver
nvcc --version      # verify CUDA
```

**FFmpeg with NVENC:**
Download `ffmpeg-release-full.7z` from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/), extract to `C:\ffmpeg`, add `C:\ffmpeg\bin` to PATH.

```powershell
ffmpeg -encoders | findstr nvenc   # should show hevc_nvenc, h264_nvenc
```

**uv (Python package manager):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart terminal after install.

#### 2. Clone & Install

```powershell
git clone https://github.com/JStephenHuang/yap.git
cd yap/creepypasta/v2
uv sync
```

**Install PyTorch with CUDA:**

Check your CUDA version (`nvcc --version`) and use matching wheel:

```powershell
# For CUDA 12.4
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# For CUDA 12.1
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Verify CUDA is detected:**

```powershell
uv run python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Devices: {torch.cuda.device_count()}')"
# Expected: CUDA: True, Devices: 2
```

#### 3. Environment Variables

Create `.env` in `creepypasta/v2/`:

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

Place your YouTube OAuth client secret JSON at `creepypasta/v2/secrets/youtube_client_secret.json`.

#### 4. Run Pipeline

```powershell
# Scrape stories first
uv run scrape-reddit

# Check queue
uv run python src/main.py status

# Process next story (with reviews)
uv run python src/main.py run

# Process without reviews (auto-approve)
uv run python src/main.py run --no-review

# Test with sample data (no db)
uv run python src/main.py test

# Resume from checkpoint
uv run python src/main.py resume <thread_id>
```

### Configuration

All configs are in `src/config/`. Modify to swap models, prompts, or settings:

| File | What to tweak |
|------|---------------|
| `tts.py` | TTS provider, model, speaker voice reference |
| `tti.py` | Image model, dimensions, inference steps |
| `video.py` | Intro duration, crossfades, encoding settings |
| `triage.py` | LLM provider/model, triage prompt |
| `refine_story.py` | Story refinement prompt |
| `scene_prompts.py` | Image prompt generation |
| `thumbnail_prompt.py` | Thumbnail prompt generation |
| `yt_metadata.py` | Title/description generation |

**Adding a new speaker:**

Edit `src/config/tts.py`:
```python
SPEAKERS: dict[str, Speaker] = {
    "ghoul": Speaker(
        name="ghoul",
        audio=Path("assets/narrators/ghoul.mp3"),
        transcript="The exact words spoken in the audio file.",
    ),
    "myspeaker": Speaker(
        name="myspeaker",
        audio=Path("assets/narrators/myspeaker.wav"),
        transcript="What myspeaker says in the reference audio.",
    ),
}
DEFAULT_SPEAKER: str = "myspeaker"
```

### Output

Each run creates a folder in `runs/{checkpoint_id}/`:

```
runs/a1b2c3d4/
├── metadata.json      # Pipeline state (checkpoint_thread_id for resume)
├── narration.wav      # TTS audio
├── scene_0.png        # Generated images
├── scene_1.png
├── scene_2.png
├── thumbnail.png      # YouTube thumbnail
└── video.mp4          # Final video
```

**metadata.json** contains:
- `checkpoint_thread_id` - Use this to resume if pipeline fails
- `script` - Refined story text
- `scene_prompts` - Image generation prompts
- `yt_title`, `yt_description` - YouTube metadata
- `status` - Current pipeline state

**Databases** in `db/`:
- `threads.sqlite` - Scraped reddit threads
- `checkpoints.sqlite` - LangGraph checkpoints for resume
