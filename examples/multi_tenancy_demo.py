import asyncio
import shutil
import os
from zettel_memory.core.brain import ZettelBrain

async def main():
    print("--- Multi-tenancy Isolation Demo ---")
    
    # Define separate paths
    path_alice = "./brain_data/users/alice"
    path_bob = "./brain_data/users/bob"
    
    # Clean up previous run
    if os.path.exists(path_alice): shutil.rmtree(path_alice)
    if os.path.exists(path_bob): shutil.rmtree(path_bob)
    
    print(f"[Setup] Creating brains for Alice and Bob...")
    brain_alice = ZettelBrain(storage_path=path_alice)
    brain_bob = ZettelBrain(storage_path=path_bob)
    
    # 1. Alice adds a secret
    print("\n[Action] Alice adds a secret...")
    await brain_alice.add_memory("Alice's secret: The treasure is buried under the old oak tree.")
    
    # 2. Bob adds his own note
    print("[Action] Bob adds a note...")
    await brain_bob.add_memory("Bob's note: I need to buy milk today.")
    
    # 3. Bob tries to retrieve Alice's secret
    print("\n[Test] Bob tries to search for 'treasure'...")
    results_bob = await brain_bob.retrieve("treasure")
    print(f"Bob's Results: {results_bob}")
    
    found_leak = any("treasure" in r.lower() for r in results_bob)
    
    if not found_leak:
        print(f"✅ SUCCESS: Bob found safe results: {results_bob}")
    else:
        print(f"❌ FAILURE: Bob found Alice's secret! {results_bob}")
        
    # 4. Alice retrieves her secret
    print("\n[Test] Alice searches for 'treasure'...")
    results_alice = await brain_alice.retrieve("treasure")
    print(f"Alice's Results: {results_alice}")
    
    if len(results_alice) > 0 and "treasure" in results_alice[0]:
         print("✅ SUCCESS: Alice found her own data.")
    else:
         print("❌ FAILURE: Alice lost her data.")

    # Cleanup (Optional)
    # shutil.rmtree("./brain_data/users")

if __name__ == "__main__":
    asyncio.run(main())
