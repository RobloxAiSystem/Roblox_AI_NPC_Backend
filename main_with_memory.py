from fastapi import FastAPI
from pydantic import BaseModel
from memory_store import store
import uvicorn, asyncio

app = FastAPI()

class Event(BaseModel):
    npc_id: str
    player: str
    message: str
    position: list[float]

@app.post("/api/event")
async def event(ev: Event):
    await store.append(ev.npc_id, ev.dict())
    msg = ev.message.lower()
    if "bye" in msg:
        reply = f"Goodbye {ev.player}! I'll remember you."
    elif "hi" in msg or "hello" in msg:
        reply = f"Hello {ev.player}! Nice to see you again."
    else:
        mem = len(await store.load(ev.npc_id))
        reply = f"I’ve logged {mem} events so far."
    await store.save(ev.npc_id)
    return {"reply": reply, "actions": []}

@app.get("/api/load/{npc_id}")
async def load(npc_id: str):
    mem = await store.load(npc_id)
    summary = await store.summarize(npc_id)
    return {"summary": summary, "count": len(mem)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)