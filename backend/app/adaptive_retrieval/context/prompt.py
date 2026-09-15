"""
Prompt Construction Module

Responsible for:
- Building final LLM prompts
- Combining system instructions
- Adding context
- Adding user query
- Managing prompt templates
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional



# ============================================================
# Prompt Template
# ============================================================

@dataclass
class PromptTemplate:

    system: str

    instruction: str

    context_placeholder: str = "{context}"

    query_placeholder: str = "{query}"



# ============================================================
# Default RAG Prompt
# ============================================================

DEFAULT_RAG_TEMPLATE = PromptTemplate(

    system="""
You are an enterprise AI assistant.

Answer using only the provided context.
If information is unavailable, say you don't know.

Always provide accurate and concise answers.
""",

    instruction="""
Context:

{context}


Question:

{query}


Answer:
"""
)



# ============================================================
# Prompt Builder
# ============================================================

class PromptBuilder:
    """
    Builds final prompts for LLM inference.
    """

    def __init__(
        self,
        template: PromptTemplate = DEFAULT_RAG_TEMPLATE,
    ):

        self.template = template



    def build(
        self,
        query: str,
        context: str,
    ) -> str:
        """
        Creates final prompt.
        """

        instruction = (
            self.template.instruction
            .replace(
                self.template.context_placeholder,
                context,
            )
            .replace(
                self.template.query_placeholder,
                query,
            )
        )


        return (
            self.template.system.strip()
            +
            "\n\n"
            +
            instruction.strip()
        )



# ============================================================
# Chat Prompt Builder
# ============================================================

class ChatPromptBuilder(PromptBuilder):
    """
    Creates chat-model compatible messages.
    """

    def build_messages(
        self,
        query: str,
        context: str,
    ):

        return [

            {
                "role": "system",
                "content":
                    self.template.system,
            },

            {
                "role": "user",
                "content":
                    self.build(
                        query,
                        context
                    ),
            }
        ]



# ============================================================
# Dynamic Prompt Manager
# ============================================================

class PromptManager:
    """
    Handles multiple prompt strategies.
    """

    def __init__(self):

        self.templates: Dict[
            str,
            PromptTemplate
        ] = {}


    def register(
        self,
        name: str,
        template: PromptTemplate,
    ):

        self.templates[name] = template



    def get(
        self,
        name: str,
    ) -> Optional[PromptTemplate]:

        return self.templates.get(name)



# ============================================================
# Prompt Optimizer
# ============================================================

class PromptOptimizer:
    """
    Applies prompt improvements.
    """

    def optimize(
        self,
        prompt: str,
    ) -> str:

        return prompt.strip()



    def add_instruction(
        self,
        prompt: str,
        instruction: str,
    ):

        return (
            instruction
            +
            "\n\n"
            +
            prompt
        )