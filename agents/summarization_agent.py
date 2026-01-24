from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import CallSummary
import os

class SummarizationAgent:
    """Agent that generates structured summaries from call transcripts"""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model_name = model
        self.llm = ChatOpenAI(
            model=model,
            api_key=os.getenv("OPENAI_API_KEY")
        ).with_structured_output(CallSummary)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert call center analyst. Analyze the following call transcript and provide a structured summary.

Your task:
1. Write a brief 2-3 sentence summary of the call
2. Extract 3-5 key points discussed
3. List any action items or follow-ups needed
4. Identify what the customer wanted (their intent)
5. Determine if the issue was resolved, unresolved, or escalated
6. List the main topics discussed
7. Assess the overall sentiment (positive, neutral, or negative)

Be concise but thorough. Focus on facts from the transcript."""),
            ("human", """Please analyze this call transcript:

{transcript}""")
        ])

        self.chain = self.prompt | self.llm

    def run(self, transcript: str) -> CallSummary:
        """Generate a summary from the transcript"""
        return self.chain.invoke({"transcript": transcript})

    async def arun(self, transcript: str) -> CallSummary:
        """Async version"""
        return await self.chain.ainvoke({"transcript": transcript})
