from .common import TTS


def run(engine: TTS, story: str, output_path: str) -> None:
    engine.text_to_speech(story, output_path)
