from typing import Dict, Any, List

class ConversationMemory:
    """
    Lightweight in-memory store.
    Stores last N turns and a scratchpad of resolved slots for follow-ups.
    """
    def __init__(self, max_turns: int = 20):
        self.turns: List[Dict[str, Any]] = []
        self.slots: Dict[str, Any] = {}

    def add_turn(self, user: str, agent: str, meta: Dict[str, Any] = None):
        self.turns.append({"user": user, "agent": agent, "meta": meta or {}})
        if len(self.turns) > self.max_len:
            self.turns.pop(0)

    @property
    def max_len(self):
        return 20

    def remember(self, key: str, value: Any):
        self.slots[key] = value

    def recall(self, key: str, default=None):
        return self.slots.get(key, default)

    def last_answer_table(self):
        for t in reversed(self.turns):
            meta = t.get("meta", {})
            if "table" in meta:
                return meta["table"]
        return None
