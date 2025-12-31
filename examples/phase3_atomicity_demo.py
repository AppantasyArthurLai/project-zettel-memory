import os
import sys
import asyncio

# Ensure the package is in python path if not installed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zettel_memory.core.brain import ZettelBrain

async def main():
    print("Initializing Brain (Atomicity Demo)...")
    try:
        brain = ZettelBrain(storage_path="./test_brain_data_atomicity")
    except ValueError as e:
        print(f"Error: {e}")
        return

    print("\n[Step 1] Adding a composite long text...")
    long_text = """
    Python is a popular programming language known for its simplicity. 
    In contrast, C++ is complex but highly performant. 
    Also, don't forget to buy milk from the store.
    """
    
    print(f"Input: {long_text.strip()}")
    
    # This should be split into 3 notes: Python, C++, and Milk
    new_ids = await brain.add_memory(long_text, ["test", "atomicity"])
    
    print(f"\n[Step 2] Resulting IDs: {len(new_ids)}")
    print(f"IDs: {new_ids}")
    
    if len(new_ids) >= 2:
        print("SUCCESS: Input was split into multiple notes.")
    else:
        print("WARNING: Input was NOT split (or split into 1).")

    print("\n[Step 3] Verifying content of split notes...")
    for nid in new_ids:
        note = brain.storage.get(nid)
        if note:
            print(f"- ID: {nid}, Content: {note.content}")

if __name__ == "__main__":
    asyncio.run(main())
