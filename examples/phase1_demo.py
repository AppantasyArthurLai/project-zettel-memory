import os
import sys

# Ensure the package is in python path if not installed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zettel_memory.core.brain import ZettelBrain

def main():
    print("Initializing Brain...")
    try:
        brain = ZettelBrain(storage_path="./test_brain_data")
    except ValueError as e:
        print(f"Error: {e}")
        return

    print("Adding memories...")
    memories = [
        ("Python is a high-level, interpreted programming language known for its readability.", ["coding", "python"]),
        ("Machine learning uses statistical algorithms to enable computers to learn from data.", ["ai", "ml"]),
        ("To cook a perfect steak, sear it on high heat and let it rest.", ["cooking", "food"]),
        ("The capital of France is Paris.", ["geography", "europe"])
    ]

    for content, tags in memories:
        note_id = brain.add_memory(content, tags)
        print(f"Added note: {note_id} - {content[:30]}...")

    print("\nRetrieving memories (Query: 'coding')...")
    results = brain.retrieve("coding", top_k=2)
    for i, res in enumerate(results):
        print(f"{i+1}. {res}")

    print("\nRetrieving memories (Query: 'food')...")
    results = brain.retrieve("food", top_k=1)
    for i, res in enumerate(results):
        print(f"{i+1}. {res}")

    # Cleanup (Optional config for cleanup manually later)
    print("\nDone.")

if __name__ == "__main__":
    main()
