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


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences, preserving sentence-ending punctuation.

    Handles abbreviations (Mr., Dr., etc.) to avoid false splits.
    """
    # Normalize whitespace
    text = " ".join(text.split())

    sentences = []
    current = []
    words = text.split(" ")

    for i, word in enumerate(words):
        current.append(word)

        # Check if word ends with sentence-ending punctuation
        if word and word[-1] in ".!?":
            # Check if it's an abbreviation (word without punctuation, lowercase)
            word_base = word.rstrip(".!?,;:").lower()

            # It's a sentence end if:
            # - Ends with ! or ?
            # - Ends with . but is NOT an abbreviation
            # - Is the last word
            is_abbrev = word[-1] == "." and word_base in ABBREVIATIONS
            is_last = i == len(words) - 1

            if not is_abbrev or is_last:
                sentences.append(" ".join(current))
                current = []

    # Don't forget remaining words
    if current:
        sentences.append(" ".join(current))

    return [s.strip() for s in sentences if s.strip()]


def chunk_text(
    text: str,
    max_chars: int = DEFAULT_MAX_CHUNK_CHARS,
) -> list[str]:
    """
    Split text into chunks that fit within max_chars.

    Splits on sentence boundaries first, then groups sentences
    into chunks. Single sentences exceeding max_chars become
    their own chunk (no mid-sentence splits).

    Args:
        text: Text to chunk
        max_chars: Maximum characters per chunk

    Returns:
        List of text chunks
    """
    sentences = split_into_sentences(text)
    logger.debug(f"Split text into {len(sentences)} sentences")

    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        sentence_len = len(sentence)

        # If single sentence exceeds max, it becomes its own chunk (never split mid-sentence)
        if sentence_len > max_chars:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_len = 0
            chunks.append(sentence)
            logger.debug(f"Long sentence ({sentence_len} chars) as own chunk: {sentence[:50]}...")
            continue

        # Check if adding this sentence exceeds the limit
        new_len = current_len + sentence_len + (1 if current_chunk else 0)
        if new_len > max_chars and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_len = sentence_len
        else:
            current_chunk.append(sentence)
            current_len = new_len

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    logger.info(f"Chunked text into {len(chunks)} chunks (max {max_chars} chars each)")
    return chunks


def crossfade_concat(
    wavs: list[np.ndarray],
    sample_rate: int = 24000,
    crossfade_ms: int = 150,
) -> np.ndarray:
    """
    Concatenate audio arrays with crossfade to smooth transitions.

    Args:
        wavs: List of audio arrays to concatenate
        sample_rate: Audio sample rate (default 24kHz)
        crossfade_ms: Crossfade duration in milliseconds (default 150ms)

    Returns:
        Concatenated audio array
    """
    if len(wavs) == 0:
        return np.array([], dtype=np.float32)
    if len(wavs) == 1:
        return wavs[0]

    crossfade_samples = int(sample_rate * crossfade_ms / 1000)

    # Build output with crossfades
    result = wavs[0].copy()

    for wav in wavs[1:]:
        if len(result) < crossfade_samples or len(wav) < crossfade_samples:
            # Not enough samples for crossfade, just concatenate
            result = np.concatenate([result, wav])
        else:
            # Create crossfade
            fade_out = np.linspace(1, 0, crossfade_samples)
            fade_in = np.linspace(0, 1, crossfade_samples)

            # Apply fades to overlapping region
            result[-crossfade_samples:] *= fade_out
            wav_copy = wav.copy()
            wav_copy[:crossfade_samples] *= fade_in

            # Overlap-add
            result[-crossfade_samples:] += wav_copy[:crossfade_samples]
            result = np.concatenate([result, wav_copy[crossfade_samples:]])

    return result
