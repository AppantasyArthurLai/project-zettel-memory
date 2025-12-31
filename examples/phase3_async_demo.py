import os
import sys
import asyncio

# Ensure the package is in python path if not installed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zettel_memory.core.brain import ZettelBrain
from zettel_memory.core.cortex import MemoryDecayer, Dreamer

async def main():
    print("Initializing Brain (Phase 3 Async)...")
    try:
        brain = ZettelBrain(storage_path="./test_brain_data_p3")
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Test Async Adding
    print("\n[Async Test] Adding memories in parallel...")
    tasks = [
        brain.add_memory("Async python is great for I/O bound tasks.", ["python", "async"]),
        brain.add_memory("Zettelkasten helps in connecting thoughts.", ["memory", "method"]),
        brain.add_memory("Dreams consolidate memories during sleep.", ["sleep", "brain"])
    ]
    
    # Run all adds concurrently
    results = await asyncio.gather(*tasks)
    print(f"Added {len(results)} notes concurrently: {results}")

    # Test Async Retrieve
    print("\n[Async Test] Retrieving...")
    memories = await brain.retrieve("python", top_k=1)
    print(f"Retrieved: {memories}")

    # Test Cortex
    print("\n[Cortex Test] Triggering Dreamer...")
    dreamer = Dreamer(brain)
    await dreamer.compact()
    
    print("\n[Cortex Test] Triggering Decayer...")
    decayer = MemoryDecayer(brain)
    await decayer.forget()

    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
