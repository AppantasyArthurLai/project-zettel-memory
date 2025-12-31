COMPACTION_PROMPT = """You are analyzing a cluster of related memory notes.
Your goal is to synthesize them into a single, higher-level "Insight Note".

Notes:
{notes_content}

Instructions:
1. Identify the common theme.
2. Write a concise summary (max 3 sentences) that captures the core insight.
3. This insight will serve as a parent node to these notes.

Output (JSON):
{{
    "summary": "The concise summary text here."
}}
"""
