import os
from typing import List, Optional
from dotenv import load_dotenv
import asyncio
from google import genai

from zettel_memory.core.models import Note
from zettel_memory.storage.chroma_storage import ChromaStorage
from zettel_memory.storage.graph_storage import NetworkXStorage
from zettel_memory.utils.prompts import AUTO_LINKING_PROMPT
from zettel_memory.utils.atomicity_prompts import ATOMIZATION_PROMPT
from zettel_memory.utils.forget_prompts import SEMANTIC_FORGET_PROMPT
import json
from datetime import datetime

load_dotenv()

class ZettelBrain:
    def __init__(self, api_key: str = None, storage_path: str = "./brain_data"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in .env or pass it to constructor.")
        
        # Initialize Google GenAI Client
        self.client = genai.Client(api_key=self.api_key)
        
        self.embedding_model = "text-embedding-004"
        self.model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash-exp") # Updated default model name as well to be modern
        
        self.storage = ChromaStorage(persist_path=storage_path)
        self.graph = NetworkXStorage(persist_path=os.path.join(storage_path, "graph.gml"))
        
        # Cortex Components
        from zettel_memory.core.cortex import Dreamer, MemoryDecayer, Resurfacer
        self.dreamer = Dreamer(self)
        self.decayer = MemoryDecayer(self)
        self.resurfacer = Resurfacer(self)
        self.recent_note_ids = []

    async def _get_embedding(self, text: str) -> List[float]:
        try:
            response = await self.client.aio.models.embed_content(
                model=self.embedding_model,
                contents=[text],
                config={'task_type': 'retrieval_document'}
            )
            # Response structure: response.embeddings[0].values
            return response.embeddings[0].values
        except Exception as e:
            # Fallback or strict error
            print(f"Embedding failed: {e}")
            return [0.0] * 768

    async def _get_query_embedding(self, text: str) -> List[float]:
        try:
            response = await self.client.aio.models.embed_content(
                model=self.embedding_model,
                contents=[text],
                config={'task_type': 'retrieval_query'}
            )
            return response.embeddings[0].values
        except Exception as e:
             print(f"Query embedding failed: {e}")
             return [0.0] * 768

    async def add_memory(self, content: str, tags: List[str] = None) -> List[str]:
        """
        Add a memory note asynchronously.
        1. Atomize content into sub-notes.
        2. Embedding & Save each sub-note.
        3. Auto-link each sub-note.
        4. Return list of new Note IDs.
        """
        tags = tags or []
        
        # 1. Atomization - Split content
        prompt = ATOMIZATION_PROMPT.format(raw_content=content)
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text.replace("```json", "").replace("```", "").strip()
            # Handle potential non-JSON output gracefully or strict parsing
            try:
                result = json.loads(text)
                sub_contents = result.get("notes", [content])
            except json.JSONDecodeError:
                # If LLM failed to return JSON, fall back to raw content as single note
                print(f"[Brain] Atomization JSON parse failed. Using raw content.")
                sub_contents = [content]
        except Exception as e:
            print(f"[Brain] Atomization failed: {e}. Using raw content.")
            sub_contents = [content]

        new_ids = []

        for sub_content in sub_contents:
            if not sub_content.strip():
                continue
            
            # 2. Embedding & Save Vector
            embedding = await self._get_embedding(sub_content)
            note = Note(
                content=sub_content,
                tags=tags,
                embedding=embedding
            )
            # Storage operations
            self.storage.add(note)
            
            # 3. Add Node to Graph
            self.graph.add_node(note.id, tags=",".join(note.tags))

            # 4. Auto-linking (Async LLM)
            await self._auto_link(note)
            
            # 5. Trigger Cortex (Dreaming) - Fire and Forget
            self.recent_note_ids.append(note.id)
            new_ids.append(note.id)
            
            if len(self.recent_note_ids) >= 3:
                notes_to_process = self.recent_note_ids[:]
                self.recent_note_ids = [] # Reset buffer
                asyncio.create_task(self.dreamer.compact(notes_to_process))
        
        return new_ids

    def delete_memory(self, note_id: str) -> None:
        """
        Delete a specific memory by ID.
        Removes from both VectorDB and Graph.
        """
        self.storage.delete(note_id)
        self.graph.remove_node(note_id)

    def clear_all_memories(self) -> None:
        """
        wipe the brain clean.
        Clears both VectorDB and Graph.
        """
        self.storage.clear()
        self.graph.clear()



    async def forget_by_query(self, query: str) -> List[str]:
        """
        Semantically forget memories based on a natural language query.
        1. Search for candidates.
        2. Ask LLM to confirm which ones to delete.
        3. Execute deletion.
        """
        # 1. Retrieve candidates (broad search)
        candidates = await self.retrieve(query, top_k=10, return_objects=True, update_stats=False)
        
        if not candidates:
            return []

        # 2. Format for LLM
        candidates_text = "\n".join([f"- ID: {n.id}, Content: {n.content}" for n in candidates])
        
        prompt = SEMANTIC_FORGET_PROMPT.format(
            query=query,
            candidates_list=candidates_text
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(text)
            
            ids_to_delete = result.get("notes_to_delete", [])
            
            deleted_contents = []
            
            # 3. Execute Deletion
            for note_id in ids_to_delete:
                # Find the note object to get content for reporting
                note = next((n for n in candidates if n.id == note_id), None)
                if note:
                    deleted_contents.append(note.content)
                    self.delete_memory(note_id)
            
            if deleted_contents:
                print(f"Forget intent: '{query}' -> Deleted {len(deleted_contents)} memories.")
                
            return deleted_contents

        except Exception as e:
            print(f"Semantic forgetting failed: {e}")
            return []

    async def _auto_link(self, new_note: Note):
        """
        Find candidates via vector search and use LLM to decide on links.
        """
        candidates = self.storage.query(new_note.embedding, top_k=5)
        candidates = [n for n in candidates if n.id != new_note.id]
        
        if not candidates:
            return

        candidates_text = "\n".join([f"- Note ID: {c.id}, Content: {c.content}" for c in candidates])
        
        prompt = AUTO_LINKING_PROMPT.format(
            new_note_content=new_note.content,
            candidates_list=candidates_text
        )

        try:
            # Generate content async
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(text)
            
            for link in result.get("links", []):
                target_id = link["target_id"]
                reason = link.get("reason", "")
                
                if any(c.id == target_id for c in candidates):
                    self.graph.add_edge(new_note.id, target_id, reason=reason)
                    print(f"Auto-linked {new_note.id} -> {target_id} ({reason})")

        except Exception as e:
            print(f"Auto-linking failed: {e}")

    async def retrieve(self, query: str, top_k: int = 5, return_objects: bool = False, update_stats: bool = True) -> List[any]:
        """
        Hybrid retrieval: Vector Search + Graph Neighbor Expansion.
        If return_objects is True, returns List[Note]. Otherwise returns List[str] (content).
        If update_stats is True, updates last_accessed and access_count.
        """
        # 1. Vector Search
        query_embedding = await self._get_query_embedding(query)
        initial_notes = self.storage.query(query_embedding, top_k=top_k)
        
        if not initial_notes:
            return []

        # 2. Graph Expansion (1-hop)
        expanded_ids = set(note.id for note in initial_notes)
        for note in initial_notes:
            neighbors = self.graph.get_neighbors(note.id, hops=1)
            for neighbor_id in neighbors:
                expanded_ids.add(neighbor_id)
        
        # 3. Fetch content
        final_notes = []
        
        # Add initial notes
        for note in initial_notes:
            if update_stats:
                # Update access stats
                note.last_accessed = datetime.now()
                note.access_count += 1
            final_notes.append(note)
            
        # Add neighbors
        for nid in expanded_ids:
            if nid not in [n.id for n in initial_notes]:
                note = self.storage.get(nid)
                if note:
                    final_notes.append(note)
                    
        # Update persistence for stats (Optional/MVP Skip for perf)
        # for n in final_notes: self.storage.add(n) 

        if return_objects:
            return final_notes
            
        return [n.content for n in final_notes]
