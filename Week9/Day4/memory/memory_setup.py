from autogen_core.memory import ListMemory, MemoryContent

# Initialize the memory store
user_memory = ListMemory(name="user_preferences")

# Function to add "Important Facts" to the store
async def remember_fact(content: str):
    await user_memory.add(MemoryContent(content=content))