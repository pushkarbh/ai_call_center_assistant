from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import QAScores, AgentState
import os

class QAScoringAgent:
    """Agent that evaluates call quality on multiple dimensions"""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model_name = model
        self.llm = ChatOpenAI(
            model=model,
            api_key=os.getenv("OPENAI_API_KEY")
        ).with_structured_output(QAScores)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert call center quality analyst. Evaluate the following call transcript on these dimensions:

1. **Empathy (0-10)**: Did the agent show understanding and compassion for the customer's situation?
2. **Professionalism (0-10)**: Was the agent courteous, respectful, and maintained professional standards?
3. **Resolution (0-10)**: How effectively was the customer's issue addressed and resolved?
4. **Tone (0-10)**: Was the agent's tone friendly, helpful, and appropriate throughout?

Scoring Guide:
- 9-10: Exceptional
- 7-8: Good
- 5-6: Adequate
- 3-4: Needs improvement
- 0-2: Poor

Provide specific comments explaining your scores and highlighting strengths or areas for improvement."""),
            ("human", """Please evaluate this call transcript:

{transcript}

Provide scores and detailed comments.""")
        ])

        self.chain = self.prompt | self.llm

    def run(self, state: AgentState) -> AgentState:
        """Generate QA scores from the transcript"""
        
        if not state.transcript:
            raise ValueError("No transcript available for QA scoring")

        qa_scores = self.chain.invoke({
            "transcript": state.transcript.full_text
        })

        state.qa_scores = qa_scores
        state.execution_path.append("qa_scoring")
        state.models_used.append(self.model_name)

        return state

    async def arun(self, state: AgentState) -> AgentState:
        """Async version"""
        if not state.transcript:
            raise ValueError("No transcript available for QA scoring")

        qa_scores = await self.chain.ainvoke({
            "transcript": state.transcript.full_text
        })

        state.qa_scores = qa_scores
        state.execution_path.append("qa_scoring")
        state.models_used.append(self.model_name)

        return state
