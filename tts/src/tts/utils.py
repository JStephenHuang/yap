"""
TTS utilities - shared helpers for text processing.
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)

# Default max characters per chunk (conservative for most models)
DEFAULT_MAX_CHUNK_CHARS = 300

# Common abbreviations that shouldn't be treated as sentence endings
ABBREVIATIONS = {
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "vs", "etc", "inc", "ltd",
    "st", "ave", "blvd", "rd", "apt", "no", "vol", "pg", "pp", "fig",
}


def split_into_sentences(text: str, sentences_per_chunk: int = 1) -> list[str]:
    text = " ".join(text.split())

    sentences = []
    current = []
    words = text.split(" ")

    for i, word in enumerate(words):
        current.append(word)

        if word and word[-1] in ".!?":
            word_base = word.rstrip(".!?,;:").lower()
            is_abbrev = word[-1] == "." and word_base in ABBREVIATIONS
            is_last = i == len(words) - 1

            if not is_abbrev or is_last:
                sentences.append(" ".join(current))
                current = []

    if current:
        sentences.append(" ".join(current))

    # Group sentences into chunks
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = " ".join(sentences[i:i + sentences_per_chunk])
        chunks.append(chunk.strip())

    return chunks

def chunk_text(
    text: str,
    max_chars: int,
) -> list[str]:
    sentences = split_into_sentences(text)

    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        sentence_len = len(sentence)

        if sentence_len > max_chars:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_len = 0
            chunks.append(sentence)
            continue

        projected_len = current_len + sentence_len + (1 if current_chunk else 0)

        if current_chunk and projected_len > max_chars:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_len = sentence_len
        else:
            current_chunk.append(sentence)
            current_len = projected_len

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def simple_concat(
    wavs: list[np.ndarray],
    sample_rate: int = 24000,
    silence_ms: int = 300,
) -> np.ndarray:
    """
    Concatenate audio arrays with silence padding between chunks.

    Args:
        wavs: List of audio arrays to concatenate
        sample_rate: Audio sample rate (default 24kHz)
        silence_ms: Silence duration between chunks in milliseconds (default 300ms)

    Returns:
        Concatenated audio array
    """
    if len(wavs) == 0:
        return np.array([], dtype=np.float32)
    if len(wavs) == 1:
        return wavs[0]

    silence_samples = int(sample_rate * silence_ms / 1000)
    silence = np.zeros(silence_samples, dtype=np.float32)

    # Concatenate with silence between chunks
    result = []
    for i, wav in enumerate(wavs):
        result.append(wav)
        if i < len(wavs) - 1:  # Don't add silence after last chunk
            result.append(silence)

    return np.concatenate(result)

def concat_crossfade(
    wavs: list[np.ndarray],
    sample_rate: int = 24000,
    crossfade_ms: int = 15,
    silence_ms: int = 200,
) -> np.ndarray:
    if not wavs:
        return np.array([], dtype=np.float32)

    crossfade = int(sample_rate * crossfade_ms / 1000)
    silence = np.zeros(int(sample_rate * silence_ms / 1000), dtype=np.float32)

    output = wavs[0].astype(np.float32)

    for wav in wavs[1:]:
        wav = wav.astype(np.float32)

        cf = min(crossfade, len(output), len(wav))
        fade_out = np.linspace(1.0, 0.0, cf)
        fade_in = np.linspace(0.0, 1.0, cf)

        output[-cf:] = output[-cf:] * fade_out + wav[:cf] * fade_in
        output = np.concatenate([output[:-cf], output[-cf:], wav[cf:], silence])

    return output