from dataclasses import dataclass

@dataclass
class RawMessage:
    user: str
    content: str

    def is_aside(self):
        return self.user == "__ASIDE__"

    def is_assistant(self):
        return self.user == "Lily"

@dataclass
class SftMessage:
    role: str
    content: str

@dataclass
class SftMessages:
    messages: list[SftMessage]   
