from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType

def build_session_memory() -> ListMemory:
    return ListMemory(name="session_memory")

async def add_to_session(memory: ListMemory, role: str, content: str) -> None:
    # Sliding Window: Keep only the most recent 20 messages
    if len(memory._contents) >= 20:
        memory._contents.pop(0) 

    await memory.add(
        MemoryContent(
            content=f"[{role}]: {content}",
            mime_type=MemoryMimeType.TEXT,
        )
    )