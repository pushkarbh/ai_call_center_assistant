from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import SummaryCritique, AgentState
import os

class CriticAgent:
    """Agent that evaluates summary quality and decides if revision is needed.

    Uses Claude as an independent evaluator to critique GPT-generated summaries,
    creating a 'student/teacher' dynamic for more rigorous quality control.
    """

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model_name = model
        self.llm = ChatAnthropic(
            model=model,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        ).with_structured_output(SummaryCritique)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert quality evaluator for call center summaries. Your job is to critique the summary against the original transcript.

Evaluate on three dimensions (1-10 scale):

1. **Faithfulness**: Does the summary accurately reflect what was said? No hallucinations or misrepresentations?
   - 9-10: Perfectly accurate
   - 7-8: Mostly accurate with minor issues
   - 5-6: Some inaccuracies
   - 1-4: Significant errors or hallucinations

2. **Completeness**: Are all important points covered? Nothing critical missing?
   - 9-10: All key information captured
   - 7-8: Most important points covered
   - 5-6: Missing some important details
   - 1-4: Major gaps in coverage

3. **Conciseness**: Is it clear and to-the-point without unnecessary verbosity?
   - 9-10: Perfect balance, clear and concise
   - 7-8: Good but could be tighter
   - 5-6: Somewhat verbose or unclear
   - 1-4: Too wordy or confusing

**Revision Criteria**:
- Set needs_revision=True if ANY score is below 7
- Set needs_revision=False if all scores are 7 or above

If revision is needed, provide specific, actionable revision_instructions."""),
            ("human", """**Original Transcript**:
{transcript}

**Current Summary**:
Brief: {brief_summary}
Key Points: {key_points}
Action Items: {action_items}
Customer Intent: {customer_intent}
Sentiment: {sentiment}
Resolution: {resolution_status}
Topics: {topics}

Please evaluate this summary and provide your critique.""")
        ])

        self.chain = self.prompt | self.llm

    def run(self, state: AgentState) -> AgentState:
        """Evaluate the summary and decide if revision is needed"""
        
        if not state.summary or not state.transcript:
            state.errors.append("Cannot critique: missing summary or transcript")
            return state

        # Prepare summary details for evaluation
        summary = state.summary
        
        critique = self.chain.invoke({
            "transcript": state.transcript.full_text,
            "brief_summary": summary.brief_summary,
            "key_points": ", ".join(summary.key_points),
            "action_items": ", ".join(summary.action_items) if summary.action_items else "None",
            "customer_intent": summary.customer_intent,
            "sentiment": summary.sentiment.value,
            "resolution_status": summary.resolution_status.value,
            "topics": ", ".join(summary.topics)
        })

        # Update state with critique
        state.summary_critique = critique
        state.needs_revision = critique.needs_revision
        
        # If revision needed, increment counter
        if critique.needs_revision:
            state.revision_count += 1
            state.current_agent = "summarization"  # Route back to summarization
        else:
            state.current_agent = "qa_scoring"  # Continue to QA
        
        state.execution_path.append("critic")
        state.models_used.append(self.model_name)

        return state

    async def arun(self, state: AgentState) -> AgentState:
        """Async version"""
        if not state.summary or not state.transcript:
            state.errors.append("Cannot critique: missing summary or transcript")
            return state

        summary = state.summary
        
        critique = await self.chain.ainvoke({
            "transcript": state.transcript.full_text,
            "brief_summary": summary.brief_summary,
            "key_points": ", ".join(summary.key_points),
            "action_items": ", ".join(summary.action_items) if summary.action_items else "None",
            "customer_intent": summary.customer_intent,
            "sentiment": summary.sentiment.value,
            "resolution_status": summary.resolution_status.value,
            "topics": ", ".join(summary.topics)
        })

        state.summary_critique = critique
        state.needs_revision = critique.needs_revision
        
        if critique.needs_revision:
            state.revision_count += 1
            state.current_agent = "summarization"
        else:
            state.current_agent = "qa_scoring"
        
        state.execution_path.append("critic")
        state.models_used.append(self.model_name)

        return state
