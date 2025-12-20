"""
NeuTTS Air provider - voice cloning TTS.
"""

import io
from pathlib import Path

import numpy as np
import soundfile as sf

from tts.providers.base import BaseTTSProvider
from tts.utils import chunk_text, crossfade_concat
from tts.vendor.neutts import NeuTTSAir


# Max characters per chunk (NeuTTS has ~2048 token limit for ref + text + audio tokens)
# Larger chunks = more natural flow but risk hitting limit
MAX_CHUNK_CHARS = 400


class NeuTTSProvider(BaseTTSProvider):
    """
    NeuTTS Air provider for voice cloning TTS.

    Voices are reference audio files. Each voice_id maps to a tuple of
    (audio_path, transcript_text) that defines the target voice.
    """

    def __init__(self):
        self._model: NeuTTSAir | None = None
        self._voices: dict[str, tuple[Path, str]] = {}
        self._ref_codes_cache: dict[str, np.ndarray] = {}

    def load(self, model: str = "neuphonic/neutts-air", device: str = "cpu", **kwargs) -> None:
        """
        Load the NeuTTS model.

        Args:
            model: HuggingFace repo for backbone (default: neuphonic/neutts-air)
            device: "cpu" or "cuda" - used for both backbone and codec unless overridden
            **kwargs:
                codec_repo: Codec model repo (default: neuphonic/neucodec)
                codec_device: Override device for codec (defaults to device)
        """
        self._model = NeuTTSAir(
            backbone_repo=model,
            backbone_device=device,
            codec_repo=kwargs.get("codec_repo", "neuphonic/neucodec"),
            codec_device=kwargs.get("codec_device", device),
        )

    def register_voice(
        self,
        voice_id: str,
        audio_path: str | Path,
        transcript: str,
    ) -> None:
        """
        Register a reference voice for cloning.

        Args:
            voice_id: Unique identifier for this voice
            audio_path: Path to reference audio file
            transcript: Text spoken in the reference audio
        """
        self._voices[voice_id] = (Path(audio_path), transcript)
        # Clear cached codes for this voice if it existed
        self._ref_codes_cache.pop(voice_id, None)

    def synthesize(
        self,
        text: str,
        voice_id: str | None = None,
        output_path: Path | None = None,
    ) -> bytes:
        """
        Synthesize speech from text using a registered voice.

        Args:
            text: Text to synthesize
            voice_id: ID of registered voice to clone
            output_path: Optional path to save audio file

        Returns:
            Raw audio bytes (WAV format, 24kHz)
        """
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        if voice_id is None:
            raise ValueError("voice_id required - NeuTTS is a voice cloning model")

        if voice_id not in self._voices:
            raise ValueError(
                f"Voice '{voice_id}' not registered. "
                f"Available: {list(self._voices.keys())}"
            )

        # Get or encode reference
        if voice_id not in self._ref_codes_cache:
            audio_path, _ = self._voices[voice_id]
            self._ref_codes_cache[voice_id] = self._model.encode_reference(audio_path)

        ref_codes = self._ref_codes_cache[voice_id]
        _, ref_text = self._voices[voice_id]

        # Chunk text to stay within token limit
        chunks = chunk_text(text, MAX_CHUNK_CHARS)

        # Generate audio for each chunk
        wavs = []
        for chunk in chunks:
            wav = self._model.infer(chunk, ref_codes, ref_text)
            wavs.append(wav)

        # Concatenate with crossfade (24kHz sample rate)
        final_wav = crossfade_concat(wavs, sample_rate=24000)

        # Convert to WAV bytes
        buffer = io.BytesIO()
        sf.write(buffer, final_wav, 24000, format="WAV")
        audio_bytes = buffer.getvalue()

        # Optionally save to file
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            sf.write(str(output_path), final_wav, 24000)

        return audio_bytes

    def unload(self) -> None:
        """Unload model from memory."""
        self._model = None
        self._ref_codes_cache.clear()
        # Force garbage collection for GPU memory
        import gc
        import torch
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def list_voices(self) -> list[str]:
        """List registered voice IDs."""
        return list(self._voices.keys())
