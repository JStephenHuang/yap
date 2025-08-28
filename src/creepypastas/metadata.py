from __future__ import annotations

import dataclasses
import enum
import json
import pathlib


class State(enum.IntEnum):
    FETCHED = enum.auto()
    TRIAGED = enum.auto()
    SANITIZED = enum.auto()
    AUDIO_GENERATED = enum.auto()
    IMAGE_GENERATED = enum.auto()
    EXPORTED = enum.auto()
    PUBLISHED = enum.auto()


@dataclasses.dataclass
class Metadata:
    uri: str
    title: str
    author: str
    state: State

    def save(self, path: pathlib.Path) -> None:
        data = dataclasses.asdict(self)
        data["state"] = self.state.name

        with path.open("w") as f:
            json.dump(data, f)

    @staticmethod
    def load(path: pathlib.Path) -> Metadata:
        with path.open("r") as f:
            data = json.load(f)
            data["state"] = State[data.get("state")]

            return Metadata(**data)


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = pathlib.Path(tmpdir) / "metadata.json"

        sample = Metadata(
            uri="https://example.com/story",
            title="Example Story",
            author="Unknown",
            state=State.FETCHED,
        )

        sample.save(temp_path)
        read_sample = Metadata.load(temp_path)

        assert sample.uri == read_sample.uri, "URI should be the same"
        assert sample.title == read_sample.title, "Title should be the same"
        assert sample.author == read_sample.author, "Author should be the same"
        assert sample.state == read_sample.state, "State should be the same"
