from creepypastas.higgs_audio.boson_multimodal.serve.serve_engine import (
    HiggsAudioServeEngine,
    HiggsAudioResponse,
)
from creepypastas.higgs_audio.boson_multimodal.data_types import (
    ChatMLSample,
    Message,
    AudioContent,
)

import torch
import torchaudio
import pathlib

from .common import TTS

MODEL_PATH = "bosonai/higgs-audio-v2-generation-3B-base"
AUDIO_TOKENIZER_PATH = "bosonai/higgs-audio-v2-tokenizer"
voice = pathlib.Path("assets/speakers/ghoul.mp3")
voice_path = str(voice)


device = "cuda" if torch.cuda.is_available() else "cpu"

system_prompt = """Generate audio that matches the narration style provided in the reference audio."""


class HiggsAudioTTS(TTS):
    def __init__(self):
        self.engine = HiggsAudioServeEngine(
            MODEL_PATH, AUDIO_TOKENIZER_PATH, device=device
        )

    def text_to_speech(self, story: str, output_path: str) -> None:
        messages = [
            Message(
                role="system",
                content=system_prompt,
            ),
            Message(role="user", content=story),
        ]

        output: HiggsAudioResponse = self.engine.generate(
            chat_ml_sample=ChatMLSample(messages=messages),
            max_new_tokens=1024,
            temperature=0.2,
            top_p=0.9,
            top_k=40,
            stop_strings=["<|end_of_text|>", "<|eot_id|>"],
        )

        torchaudio.save(
            output_path, torch.from_numpy(output.audio)[None, :], output.sampling_rate
        )


if __name__ == "__main__":
    print("hello")

    hig = HiggsAudioTTS()
    hig.text_to_speech("Once upon a time...", "output.wav")
