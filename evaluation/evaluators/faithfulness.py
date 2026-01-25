"""
Faithfulness Evaluator - LLM-as-Judge

Evaluates whether the generated summary accurately reflects the original transcript
without hallucinations or misrepresentations.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional
import os


class FaithfulnessScore(BaseModel):
    """Structured output for faithfulness evaluation"""
    score: int = Field(ge=1, le=10, description="Faithfulness score from 1-10")
    reasoning: str = Field(description="Explanation for the score")
    hallucinations: list[str] = Field(default=[], description="List of any hallucinated facts")
    misrepresentations: list[str] = Field(default=[], description="List of any misrepresented facts")


class FaithfulnessEvaluator:
    """Evaluates summary faithfulness against the original transcript"""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model_name = model
        self.llm = ChatOpenAI(
            model=model,
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0
        ).with_structured_output(FaithfulnessScore)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert evaluator assessing the faithfulness of call center summaries.

Your task is to determine if the summary accurately reflects what was said in the transcript, without:
1. Hallucinations (facts not present in the transcript)
2. Misrepresentations (facts twisted or changed from the original meaning)
3. Unsupported conclusions

Scoring Guide:
- 9-10: Perfectly faithful, no hallucinations or misrepresentations
- 7-8: Mostly faithful with minor imprecisions that don't change meaning
- 5-6: Some inaccuracies or unsupported statements
- 3-4: Significant misrepresentations or hallucinations
- 1-2: Mostly unfaithful to the source material

Be strict but fair. Minor paraphrasing is acceptable; invented facts are not."""),
            ("human", """**Original Transcript:**
{transcript}

**Generated Summary:**
Brief Summary: {brief_summary}
Key Points: {key_points}
Action Items: {action_items}
Customer Intent: {customer_intent}
Sentiment: {sentiment}
Resolution: {resolution_status}

Please evaluate the faithfulness of this summary.""")
        ])

        self.chain = self.prompt | self.llm

    def evaluate(self, transcript: str, summary: dict) -> FaithfulnessScore:
        """Evaluate a single summary for faithfulness

        Args:
            transcript: Original transcript text
            summary: Dictionary with summary fields

        Returns:
            FaithfulnessScore with score, reasoning, and issues found
        """
        result = self.chain.invoke({
            "transcript": transcript,
            "brief_summary": summary.get("brief_summary", ""),
            "key_points": ", ".join(summary.get("key_points", [])),
            "action_items": ", ".join(summary.get("action_items", [])) or "None",
            "customer_intent": summary.get("customer_intent", ""),
            "sentiment": summary.get("sentiment", ""),
            "resolution_status": summary.get("resolution_status", "")
        })

        return result

    async def aevaluate(self, transcript: str, summary: dict) -> FaithfulnessScore:
        """Async version of evaluate"""
        result = await self.chain.ainvoke({
            "transcript": transcript,
            "brief_summary": summary.get("brief_summary", ""),
            "key_points": ", ".join(summary.get("key_points", [])),
            "action_items": ", ".join(summary.get("action_items", [])) or "None",
            "customer_intent": summary.get("customer_intent", ""),
            "sentiment": summary.get("sentiment", ""),
            "resolution_status": summary.get("resolution_status", "")
        })

        return result


def faithfulness_evaluator(run, example) -> dict:
    """LangSmith-compatible evaluator function

    Args:
        run: The run object containing outputs
        example: The example object containing inputs

    Returns:
        Dictionary with score and reasoning
    """
    evaluator = FaithfulnessEvaluator()

    # Extract transcript and summary from run
    transcript = example.inputs.get("transcript", "")
    summary = run.outputs.get("summary", {})

    if not transcript or not summary:
        return {
            "key": "faithfulness",
            "score": 0,
            "comment": "Missing transcript or summary"
        }

    result = evaluator.evaluate(transcript, summary)

    return {
        "key": "faithfulness",
        "score": result.score / 10,  # Normalize to 0-1
        "comment": result.reasoning
    }
