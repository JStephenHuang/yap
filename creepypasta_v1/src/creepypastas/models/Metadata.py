import dataclasses


@dataclasses.dataclass
class Metadata:
    thread_id: str
    url: str
    title: str
    author: str
    story: str
