from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import CallSummary, AgentState
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

    def run(self, state: AgentState) -> AgentState:
        """Generate a summary from the transcript in the state"""
        if not state.transcript:
            raise ValueError("No transcript available for summarization")

        # Check if this is a revision
        if state.revision_count > 0 and state.summary_critique:
            # Add revision instructions to the prompt
            revised_prompt = self.prompt + ChatPromptTemplate.from_messages([
                ("human", """REVISION REQUIRED (Attempt {revision_count}/3):

Previous critique:
{critique_feedback}

Revision instructions:
{revision_instructions}

Please improve the summary based on this feedback.""")
            ])
            
            revised_chain = revised_prompt | self.llm
            
            summary = revised_chain.invoke({
                "transcript": state.transcript.full_text,
                "revision_count": state.revision_count,
                "critique_feedback": state.summary_critique.feedback,
                "revision_instructions": state.summary_critique.revision_instructions or "Improve based on the critique scores."
            })
        else:
            # First attempt - standard summarization
            summary = self.chain.invoke({"transcript": state.transcript.full_text})
        
        state.summary = summary
        state.execution_path.append(f"summarization{'_v'+str(state.revision_count+1) if state.revision_count > 0 else ''}")
        state.models_used.append(self.model_name)
        
        return state

    async def arun(self, state: AgentState) -> AgentState:
        """Async version"""
        if not state.transcript:
            raise ValueError("No transcript available for summarization")

        summary = await self.chain.ainvoke({"transcript": state.transcript.full_text})
        
        state.summary = summary
        state.execution_path.append("summarization")
        state.models_used.append(self.model_name)
        
        return state
