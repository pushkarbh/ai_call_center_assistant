"""
Completeness Evaluator - LLM-as-Judge

Evaluates whether the summary captures all important information from the transcript.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional
import os


class CompletenessScore(BaseModel):
    """Structured output for completeness evaluation"""
    score: int = Field(ge=1, le=10, description="Completeness score from 1-10")
    reasoning: str = Field(description="Explanation for the score")
    missing_information: list[str] = Field(default=[], description="Important information missing from summary")
    covered_well: list[str] = Field(default=[], description="Topics covered thoroughly")


class CompletenessEvaluator:
    """Evaluates whether summary captures all important information"""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model_name = model
        self.llm = ChatOpenAI(
            model=model,
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0
        ).with_structured_output(CompletenessScore)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert evaluator assessing the completeness of call center summaries.

Your task is to determine if the summary captures all important information from the transcript:
1. Main customer issue/request
2. Key actions taken by the agent
3. Resolution or outcome
4. Important commitments or follow-ups
5. Relevant reference numbers, dates, amounts

Scoring Guide:
- 9-10: All critical information captured, nothing important missing
- 7-8: Most important points covered, minor details missing
- 5-6: Core issue covered but missing significant supporting details
- 3-4: Major gaps in coverage, important information missing
- 1-2: Severely incomplete, misses the main points

Focus on business-relevant information. Filler conversation can be omitted."""),
            ("human", """**Original Transcript:**
{transcript}

**Generated Summary:**
Brief Summary: {brief_summary}
Key Points: {key_points}
Action Items: {action_items}
Customer Intent: {customer_intent}
Topics: {topics}

Please evaluate the completeness of this summary.""")
        ])

        self.chain = self.prompt | self.llm

    def evaluate(self, transcript: str, summary: dict) -> CompletenessScore:
        """Evaluate a single summary for completeness

        Args:
            transcript: Original transcript text
            summary: Dictionary with summary fields

        Returns:
            CompletenessScore with score, reasoning, and missing info
        """
        result = self.chain.invoke({
            "transcript": transcript,
            "brief_summary": summary.get("brief_summary", ""),
            "key_points": ", ".join(summary.get("key_points", [])),
            "action_items": ", ".join(summary.get("action_items", [])) or "None",
            "customer_intent": summary.get("customer_intent", ""),
            "topics": ", ".join(summary.get("topics", []))
        })

        return result

    async def aevaluate(self, transcript: str, summary: dict) -> CompletenessScore:
        """Async version of evaluate"""
        result = await self.chain.ainvoke({
            "transcript": transcript,
            "brief_summary": summary.get("brief_summary", ""),
            "key_points": ", ".join(summary.get("key_points", [])),
            "action_items": ", ".join(summary.get("action_items", [])) or "None",
            "customer_intent": summary.get("customer_intent", ""),
            "topics": ", ".join(summary.get("topics", []))
        })

        return result


def completeness_evaluator(run, example) -> dict:
    """LangSmith-compatible evaluator function

    Args:
        run: The run object containing outputs
        example: The example object containing inputs

    Returns:
        Dictionary with score and reasoning
    """
    evaluator = CompletenessEvaluator()

    # Extract transcript and summary from run
    transcript = example.inputs.get("transcript", "")
    summary = run.outputs.get("summary", {})

    if not transcript or not summary:
        return {
            "key": "completeness",
            "score": 0,
            "comment": "Missing transcript or summary"
        }

    result = evaluator.evaluate(transcript, summary)

    return {
        "key": "completeness",
        "score": result.score / 10,  # Normalize to 0-1
        "comment": result.reasoning
    }
