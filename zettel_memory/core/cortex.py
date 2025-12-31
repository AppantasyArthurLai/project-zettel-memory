from datetime import datetime
import asyncio
import json
from zettel_memory.utils.dream_prompts import COMPACTION_PROMPT

class MemoryDecayer:
    """
    Simulates Ebbinghaus forgetting curve.
    """
    def __init__(self, brain):
        self.brain = brain

    async def forget(self, threshold_days: int = 30, importance_threshold: float = 0.5):
        print("[Cortex] Running forgetting cycle...")
        
        # 1. Iterate over all notes (In MVP we iterate all via manual fetch if possible, 
        # but Chroma API doesn't support 'get_all' easily without knowing IDs.
        # Workaround: We query with empty embedding or use 'get' with limit if supported.
        # A better way for MVP: Just rely on Graph nodes which we can iterate if we loaded graph.
        
        nodes_to_remove = []
        now = datetime.now()

        # Iterate via Graph nodes (assuming all notes are in graph)
        all_nodes = list(self.brain.graph.graph.nodes())
        
        for note_id in all_nodes:
            note = self.brain.storage.get(note_id)
            if not note:
                nodes_to_remove.append(note_id)
                continue
            
            # 2. Check conditions
            delta = now - note.last_accessed
            
            if delta.days >= threshold_days and note.importance < importance_threshold:
                print(f"[Cortex] Forgetting Note {note_id}: {note.content[:30]}... (Inactive for {delta.days} days)")
                nodes_to_remove.append(note_id)
        
        # 3. Execute Deletion
        for nid in nodes_to_remove:
            try:
                self.brain.storage.delete(nid)
                self.brain.graph.remove_node(nid)
            except Exception as e:
                print(f"[Cortex] Error deleting {nid}: {e}")
        
        if not nodes_to_remove:
            print("[Cortex] key memories retained. No forgetting needed.")


class Dreamer:
    """
    Background process to compact memories into insights.
    """
    def __init__(self, brain):
        self.brain = brain

    async def compact(self, note_ids: list):
        if not note_ids:
            return
            
        print(f"[Cortex] Dreaming started on {len(note_ids)} notes...")
        try:
            # 1. Fetch contents
            notes_content = []
            for nid in note_ids:
                note = self.brain.storage.get(nid)
                if note:
                    notes_content.append(f"- {note.content}")
            
            if not notes_content:
                return

            # 2. Generate Insight
            prompt = COMPACTION_PROMPT.format(notes_content="\n".join(notes_content))
            response = await self.brain.client.aio.models.generate_content(
                model=self.brain.model_name,
                contents=prompt
            )
            
            text = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(text)
            summary = result.get("summary")
            
            if summary:
                # 3. Create Insight Note
                # We use a special tag 'insight' to identify it
                # 3. Create Insight Note
                # we get a list of IDs back (usually just 1 for summary)
                insight_ids = await self.brain.add_memory(summary, tags=["insight", "compaction"])
                if insight_ids:
                    insight_id = insight_ids[0]
                    print(f"[Cortex] Created Insight Note: {insight_id} - '{summary[:30]}...'")
                    
                    # 4. Link original notes to Insight (Hierarchy)
                    for nid in note_ids:
                        # In Zettelkasten, this might be "consolidated_by" or "parent"
                        self.brain.graph.add_edge(nid, insight_id, reason="consolidated_by")
                    
        except Exception as e:
            print(f"[Cortex] Dreaming failed: {e}")

class Resurfacer:
    """
    Proactively surfaces relevant memories based on context.
    """
    def __init__(self, brain):
        self.brain = brain
        self.last_resurface_time = datetime.min

    async def resurface(self, context: str, exclude_recent_minutes: int = 5, top_k: int = 3):
        """
        Finds relevant notes that haven't been accessed recently.
        """
        now = datetime.now()
        
        # Rate limit: Avoid spamming resurfacing too often (e.g. at least 10s gap)
        # For demo purposes, we allow frequent calls but could enforce limit here.
        
        # 1. Vector Search
        # We use standard retrieve but will filter results
        candidates = await self.brain.retrieve(context, top_k=top_k * 5, return_objects=True, update_stats=False) # Get more to filter
        
        surfaced = []
        for note in candidates:
            # 2. Filter: Exclude if accessed VERY recently (meaning it's already in context or just retrieved)
            time_since_access = now - note.last_accessed
            
            # If accessed within exclude_recent_minutes, skip it.
            # Convert minutes to seconds for comparison
            if time_since_access.total_seconds() < (exclude_recent_minutes * 60):
                continue
                
            # 3. Boost by Importance (Optional logic)
            # For now, we just accept it if it's relevant enough (top_k from vector search)
            surfaced.append(note)
            
            if len(surfaced) >= top_k:
                break
        
        if surfaced:
            print(f"[Cortex] Resurfacing {len(surfaced)} old memories related to context...")
            self.last_resurface_time = now
            
        return surfaced
