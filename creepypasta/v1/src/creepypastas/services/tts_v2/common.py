import typing


class TTS(typing.Protocol):
    def text_to_speech(self, story: str, output_path: str) -> None: ...
