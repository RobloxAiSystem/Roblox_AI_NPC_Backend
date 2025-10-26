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
    
# ------------------------------------------------------------------
#  🧾  List all logged memory files
# ------------------------------------------------------------------
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
    
# ------------------------------------------------------------------
#  🧾  Load all NPC memory files
# ------------------------------------------------------------------
@app.get("/api/load/{npc_id}")
async def load(npc_id: str):
    mem = await store.load(npc_id)
    summary = await store.summarize(npc_id)
    return {"summary": summary, "count": len(mem)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# ------------------------------------------------------------------
#  🧾  List all NPC memory files
# ------------------------------------------------------------------
import os
@app.get("/api/list")
async def list_npcs():
    folder = "npc_memory"
    if not os.path.exists(folder):
        return {"npcs": []}
    npc_files = [f.replace(".json", "") for f in os.listdir(folder) if f.endswith(".json")]
    return {"npcs": npc_files}

# ------------------------------------------------------------------
#  🧠  Return full memory log for a specific NPC
# ------------------------------------------------------------------
@app.get("/api/memory/{npc_id}")
async def get_full_memory(npc_id: str):
    events = memory_store.load_memory(npc_id)
    return {"npc_id": npc_id, "events": events, "count": len(events)}

# ------------------------------------------------------------------
#  🧹  Delete / reset one NPC’s memory
# ------------------------------------------------------------------
@app.delete("/api/memory/{npc_id}")
async def clear_memory(npc_id: str):
    import os
    path = os.path.join("npc_memory", f"{npc_id}.json")
    if os.path.exists(path):
        os.remove(path)
        return {"detail": f"{npc_id} memory cleared."}
    return {"detail": "No such NPC."}

# ------------------------------------------------------------------
#  🧩  (Optional) POST /api/save – append arbitrary event
# ------------------------------------------------------------------
from fastapi import Request
@app.post("/api/save")
async def save_from_request(request: Request):
    data = await request.json()
    npc_id = data.get("npc_id", "unknown")
    memory_store.save_memory(npc_id, data)
    return {"message": "Saved manually"}