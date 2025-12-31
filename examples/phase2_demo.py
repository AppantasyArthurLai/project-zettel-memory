import os
import sys

# Ensure the package is in python path if not installed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zettel_memory.core.brain import ZettelBrain

def main():
    print("Initializing Brain (Phase 2)...")
    try:
        brain = ZettelBrain(storage_path="./test_brain_data_p2")
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Clear previous run if needed
    # (Skip cleanup to allow seeing persistence, but for test reproducibility we might want it)

    print("\n[Case 1] Adding basic concepts...")
    id1 = brain.add_memory("Apple is a red fruit that grows on trees.", ["fruit", "nature"])
    print(f"Added Apple: {id1}")

    id2 = brain.add_memory("Bananas are yellow curved fruits rich in potassium.", ["fruit", "food"])
    print(f"Added Banana: {id2}")

    print("\n[Case 2] Adding a composite note (should auto-link to above)...")
    id3 = brain.add_memory("A standard fruit salad contains apples, bananas, and sometimes grapes.", ["recipe", "food"])
    print(f"Added Fruit Salad: {id3}")

    print("\n[Case 3] Hybrid Retrieval...")
    # Searching for "red" should find Apple via Vector.
    # If Fruit Salad is linked to Apple, it *might* show up via Graph Expansion if we search for "Red fruit" (stronger vector match to apple, then graph neighbor).
    
    print("Query: 'Red fruit'")
    results = brain.retrieve("Red fruit", top_k=1)
    print("Results:")
    for res in results:
        print(f"- {res}")
    
    # Check graph directly
    print("\n[Debug] Checking Graph connections for Fruit Salad:")
    neighbors = brain.graph.get_neighbors(id3)
    print(f"Neighbors of Fruit Salad ({id3}): {neighbors}")
    assert len(neighbors) > 0, "Auto-linking failed: Fruit Salad should be linked to Apple or Banana"
    print("Verification Passed: Auto-linking works.")

if __name__ == "__main__":
    main()
