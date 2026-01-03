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

        # if single sentence exceeds max, put it in its own chunk
        if sentence_len > max_chars:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_len = 0
            chunks.append(sentence)
            continue

        # current len + sentence len + space
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