"""
Suggested questions for AI Clinical Insights chat interface.

These questions appear as clickable chips in the UI to guide clinicians
toward high-value queries that showcase the agent's capabilities.

Design Principles:
- Questions should demonstrate available tools (DDI, vitals, notes, patient summary)
- Broad enough to apply to most patients
- Specific enough to yield actionable insights

To modify questions: Edit the SUGGESTED_QUESTIONS list below.
"""

# Questions displayed in the AI Clinical Insights interface
# These appear as clickable chips when the user opens /insight
SUGGESTED_QUESTIONS = [
    "What are the key clinical risks for this patient?",
    "Are there any drug-drug interaction concerns?",
    "Summarize this patient's recent clinical activity.",
    "What did recent clinical notes say about this patient?",
    "Has the patient seen cardiology?",
    "What imaging studies were done recently?",
]
