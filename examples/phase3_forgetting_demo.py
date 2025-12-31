import os
import sys
import asyncio
from datetime import datetime, timedelta

# Ensure the package is in python path if not installed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zettel_memory.core.brain import ZettelBrain
from zettel_memory.core.cortex import MemoryDecayer

async def main():
    print("Initializing Brain (Forgetting Demo)...")
    try:
        brain = ZettelBrain(storage_path="./test_brain_data_forget")
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    decayer = MemoryDecayer(brain)

    print("\n[Step 1] Adding notes...")
    # Note 1: High importance, Old (Should be kept)
    ids1 = await brain.add_memory("Important long-term vision.", ["strategy"])
    brain.storage.get(ids1[0]).importance = 0.9
    # Hack: Manually backdate last_accessed
    # We need to access the collection metadata directly or just mock property if we only check loaded obj.
    # But wait, our 'forget' loads from storage fresh. So we need to hack storage meta.
    # Chroma metadata is updated on 'add'. So we re-add with modified metadata?
    # Our retrieval updates 'last_accessed' on the Note object but doesn't persist it in 'retrieve' for MVP.
    # For this test, valid approach: 
    # Since our 'forget' reads 'last_accessed' from Note reconstruction, which reads from Chroma metadata.
    # We must ensure Chroma metadata has old date.
    
    # Let's modify the Note object and re-add/update it.
    note1 = brain.storage.get(ids1[0])
    note1.importance = 0.9
    note1.last_accessed = datetime.now() - timedelta(days=40)
    brain.storage.add(note1) # Overwrite
    print(f"Added Note 1 (Important, Old): {ids1[0]}")

    # Note 2: Low importance, Recent (Should be kept)
    ids2 = await brain.add_memory("Just a fleeting thought.", ["thought"])
    note2 = brain.storage.get(ids2[0])
    note2.importance = 0.2
    note2.last_accessed = datetime.now()
    brain.storage.add(note2)
    print(f"Added Note 2 (Unimportant, Recent): {ids2[0]}")

    # Note 3: Low importance, Old (Should be FORGOTTEN)
    ids3 = await brain.add_memory("Old trash data.", ["trash"])
    note3 = brain.storage.get(ids3[0])
    note3.importance = 0.1
    note3.last_accessed = datetime.now() - timedelta(days=40)
    brain.storage.add(note3)
    print(f"Added Note 3 (Unimportant, Old): {ids3[0]} -> TARGET")

    print("\n[Step 2] Triggering Forgetting...")
    await decayer.forget(threshold_days=30, importance_threshold=0.5)

    print("\n[Step 3] Verifying existence...")
    
    n1 = brain.storage.get(ids1[0])
    print(f"Note 1 exists: {n1 is not None}")
    
    n2 = brain.storage.get(ids2[0])
    print(f"Note 2 exists: {n2 is not None}")
    
    n3 = brain.storage.get(ids3[0])
    print(f"Note 3 exists: {n3 is not None}")

    if n1 and n2 and not n3:
        print("\nSUCCESS: Only the unimportant old note was forgotten.")
    else:
        print("\nFAILURE: Forgetting logic incorrect.")

if __name__ == "__main__":
    asyncio.run(main())
