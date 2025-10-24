import os, json, asyncio
from typing import Dict, Any

DATA_DIR = "npc_memory"
os.makedirs(DATA_DIR, exist_ok=True)

class MemoryStore:
    def __init__(self):
        self.cache: Dict[str, list[dict[str, Any]]] = {}

    async def load(self, npc_id: str):
        path = os.path.join(DATA_DIR, f"{npc_id}.json")
        if os.path.exists(path):
            with open(path) as f:
                self.cache[npc_id] = json.load(f)
        else:
            self.cache[npc_id] = []
        return self.cache[npc_id]

    async def append(self, npc_id: str, event: dict):
        if npc_id not in self.cache:
            await self.load(npc_id)
        self.cache[npc_id].append(event)

    async def save(self, npc_id: str):
        path = os.path.join(DATA_DIR, f"{npc_id}.json")
        with open(path, "w") as f:
            json.dump(self.cache.get(npc_id, []), f, indent=2)

    async def summarize(self, npc_id: str):
        mem = self.cache.get(npc_id, [])
        return f"NPC {npc_id} remembers {len(mem)} events."

store = MemoryStore()