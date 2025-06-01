from dataclasses import dataclass
from pandas import Timestamp

@dataclass
class RawMessage:
    user: str
    content: str

    def is_aside(self):
        return self.user == "__ASIDE__"

    def is_assistant(self):
        return self.user == "Lily"

@dataclass
class QaPair:
    id: int
    system: str
    instruction: str
    output: str
    history: list[list[str]]
    time: Timestamp
    score: int


@dataclass
class ChatMLMessage:
    role: str
    content: str

@dataclass
class ChatMLMessages:
    messages: list[ChatMLMessage]   
