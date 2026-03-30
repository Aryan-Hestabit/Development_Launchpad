from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType

def build_session_memory() -> ListMemory:
    return ListMemory(name="session_memory")


async def add_to_session(memory: ListMemory, role: str, content: str) -> None:
    await memory.add(
        MemoryContent(
            content=f"[{role}]: {content}",
            mime_type=MemoryMimeType.TEXT,
        )
    )