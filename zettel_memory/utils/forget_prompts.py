SEMANTIC_FORGET_PROMPT = """
You are the memory manager of an AI Brain.
The user wants to FORGET specific memories based on this intent:
"{query}"

Here are the candidate memories found in the database (Semantic Search Results):
{candidates_list}

Task:
Identify which of the above notes DIRECTLY match the user's intent to forget.
Be CAREFUL. Do not delete memories that are only tangentially related if the user didn't ask to remove them.
If the user says "Forget everything about X", remove all notes about X.
If the user says "Forget that I like pizza", only remove the specific note about liking pizza, not all food notes.

Return a JSON object:
{{
    "notes_to_delete": ["id_1", "id_2"],
    "reason": "Explanation of why these were chosen"
}}
Return ONLY JSON.
"""
