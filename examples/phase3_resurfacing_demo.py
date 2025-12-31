import os
import sys
import asyncio
from datetime import datetime, timedelta

# Ensure the package is in python path if not installed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zettel_memory.core.brain import ZettelBrain

async def main():
    print("Initializing Brain (Resurfacing Demo)...")
    try:
        # We need a new directory to ensure clean state
        storage_path = "./test_brain_data_resurfacing"
        brain = ZettelBrain(storage_path=storage_path)
    except ValueError as e:
        print(f"Error: {e}")
        return

    print("\n[Step 1] Creating memories...")
    
    # 1. Ancient wisdom (Relevant)
    ids1 = await brain.add_memory("Ancient Zen wisdom: Only when you empty your cup can you fill it.", ["philosophy", "zen"])
    note1 = brain.storage.get(ids1[0])
    note1.last_accessed = datetime.now() - timedelta(days=100) # Very old
    brain.storage.add(note1) # Upsert
    print(f"Added Old relevant note: '{note1.content[:30]}...'")

    # 2. Recent thought (Relevant but too new)
    ids2 = await brain.add_memory("I need to learn more about Zen philosophy.", ["plan"])
    # Last accessed is NOW (by add_memory)
    print(f"Added Recent relevant note: '{brain.storage.get(ids2[0]).content[:30]}...'")

    # 3. Irrelevant stuff
    await brain.add_memory("My grocery list: milk, eggs.", ["grocery"])
    print("Added Irrelevant note")

    print("\n[Step 2] User is talking about 'cup' or 'filling mind'...")
    context = "I feel my mind is too full to learn anything new."
    
    print(f"Context: '{context}'")
    print("Triggering Resurfacing (exclude recent 5 mins)...")
    
    surfaced = await brain.resurfacer.resurface(context, exclude_recent_minutes=5)
    
    print(f"\n[Step 3] Surfaced Results ({len(surfaced)}):")
    for note in surfaced:
        print(f"- {note.content} (Last Access: {note.last_accessed})")
        
    # Validation
    found_ancient = any("Only when you empty" in n.content for n in surfaced)
    found_recent = any("learn more about Zen" in n.content for n in surfaced)
    
    if found_ancient and not found_recent:
        print("\nSUCCESS: Surfaced old wisdom but ignored recent redundancy.")
    else:
        print(f"\nFAILURE: Ancient Found={found_ancient}, Recent Found={found_recent}")

if __name__ == "__main__":
    asyncio.run(main())
