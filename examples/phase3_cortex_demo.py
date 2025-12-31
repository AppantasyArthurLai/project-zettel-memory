import os
import sys
import asyncio

# Ensure the package is in python path if not installed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zettel_memory.core.brain import ZettelBrain

async def main():
    print("Initializing Brain (Cortex Demo)...")
    try:
        # Use a fresh DB to easily observe the count trigger (set to 3 in our logic)
        brain = ZettelBrain(storage_path="./test_brain_data_cortex")
    except ValueError as e:
        print(f"Error: {e}")
        return

    print("\n[Step 1] Adding 3 related notes to trigger Dreaming...")
    ids1 = await brain.add_memory("To make good coffee, use freshly ground beans.", ["coffee", "howto"])
    print(f"Added: {ids1}")
    
    ids2 = await brain.add_memory("Water temperature for coffee should be around 90-96 degrees Celsius.", ["coffee", "temperature"])
    print(f"Added: {ids2}")
    
    ids3 = await brain.add_memory("A standard ratio is 60g of coffee per liter of water.", ["coffee", "ratio"])
    print(f"Added: {ids3} (This should trigger Dreaming)")

    # Wait a bit for the async dreaming task to complete
    print("Waiting for dreaming to happen in background...")
    await asyncio.sleep(8) 
    
    print("\n[Step 2] Verifying Insight Note...")
    # We search for "insight" tag or "coffee" query to see if we get the summary
    results = await brain.retrieve("coffee", top_k=5)
    
    print(f"Retrieval Results ({len(results)}):")
    found_insight = False
    for res in results:
        print(f"- {res}")
        # A simple heuristic check if it looks like a summary (not one of the original sentences)
        if "To make good coffee" not in res and "Water temperature" not in res and "standard ratio" not in res:
            # It might be the insight!
            print("  ^ POTENTIAL INSIGHT DETECTED")
            found_insight = True
            
    if found_insight:
        print("\nSUCCESS: Insight note found!")
    else:
        print("\nWARNING: Insight note not clearly identified (might need manual check or longer wait).")

if __name__ == "__main__":
    asyncio.run(main())
