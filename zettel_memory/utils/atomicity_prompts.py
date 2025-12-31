ATOMIZATION_PROMPT = """You are an expert at creating Zettelkasten notes.
Your task is to split the following raw text into multiple "atomic" notes.
Each note should contain exactly one distinct idea or fact.

Raw Text:
"{raw_content}"

Instructions:
1. Analyze the text and identify distinct concepts.
2. Split them into separate notes.
3. If the text is already short and atomic, return it as a single note.
4. If the text contains irrelevant conversational filler, ignore it.

Output (JSON):
{{
    "notes": [
        "First atomic note content...",
        "Second atomic note content..."
    ]
}}
"""
