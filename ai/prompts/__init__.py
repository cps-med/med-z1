"""
AI Prompts module - System prompts and suggested questions for AI agents.

This module centralizes all AI content (prompts, questions, templates)
separate from technical configuration (config.py).

Available:
    - get_system_prompt: Get system prompt for agent type
    - SUGGESTED_QUESTIONS: List of suggested questions for UI
"""

from ai.prompts.system_prompts import get_system_prompt, AgentType
from ai.prompts.suggested_questions import SUGGESTED_QUESTIONS

__all__ = [
    "get_system_prompt",
    "SUGGESTED_QUESTIONS",
    "AgentType",
]
