AUTO_LINKING_PROMPT = """You are an intelligent knowledge assistant managing a Zettelkasten-like memory system.
Your task is to determine if a new memory note should be linked to existing memory notes based on their content.

New Note:
"{new_note_content}"

Existing Candidate Notes:
{candidates_list}

Instructions:
1. Analyze the content of the New Note and each Candidate Note.
2. Determine if there is a meaningful semantic relationship (e.g., related concept, continuation, contradiction, example of, etc.).
3. Return a JSON object with a list of "links". Each link should have "target_id" (the ID of the existing note) and a short "reason" for the link.
4. Only suggest links that are strong and meaningful. If no strong link exists, return an empty list.

Output Format (JSON only):
{{
    "links": [
        {{
            "target_id": "uuid-of-note",
            "reason": "Both discuss machine learning concepts."
        }}
    ]
}}
"""
