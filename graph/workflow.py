from langgraph.graph import StateGraph, END
from models.schemas import AgentState
from agents.intake_agent import IntakeAgent
from agents.transcription_agent import TranscriptionAgent
from agents.summarization_agent import SummarizationAgent
from agents.qa_scoring_agent import QAScoringAgent

def create_call_analysis_workflow():
    """Create the linear multi-agent workflow for call analysis"""

    # Initialize agents
    intake_agent = IntakeAgent()
    transcription_agent = TranscriptionAgent()
    summarization_agent = SummarizationAgent()
    qa_agent = QAScoringAgent()

    # Create workflow graph
    workflow = StateGraph(AgentState)

    # Define agent nodes
    workflow.add_node("intake", intake_agent.run)
    workflow.add_node("transcription", transcription_agent.run)
    workflow.add_node("summarization", summarization_agent.run)
    workflow.add_node("qa_scoring", qa_agent.run)

    # Define linear flow
    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "transcription")
    workflow.add_edge("transcription", "summarization")
    workflow.add_edge("summarization", "qa_scoring")
    workflow.add_edge("qa_scoring", END)

    # Compile the workflow
    app = workflow.compile()

    return app


def run_call_analysis(
    raw_input: str,
    input_type: str = "transcript",
    input_file_path: str = None
) -> AgentState:
    """Run the complete call analysis workflow"""

    # Create initial state
    initial_state = AgentState(
        raw_input=raw_input,
        input_type=input_type,
        input_file_path=input_file_path
    )

    # Get workflow
    app = create_call_analysis_workflow()

    # Run the workflow
    final_state = app.invoke(initial_state)

    return final_state
