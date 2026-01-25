from langgraph.graph import StateGraph, END
from models.schemas import AgentState
from agents.intake_agent import IntakeAgent
from agents.transcription_agent import TranscriptionAgent
from agents.summarization_agent import SummarizationAgent
from agents.critic_agent import CriticAgent
from agents.qa_scoring_agent import QAScoringAgent
from agents.supervisor_agent import SupervisorAgent

def create_phase4_workflow():
    """Create Phase 4 multi-agent workflow with Supervisor and Critic + revision loop"""

    # Initialize agents
    intake_agent = IntakeAgent()
    transcription_agent = TranscriptionAgent()
    summarization_agent = SummarizationAgent()
    critic_agent = CriticAgent()
    qa_agent = QAScoringAgent()
    supervisor = SupervisorAgent()

    # Create workflow graph
    workflow = StateGraph(AgentState)

    # Define agent nodes
    workflow.add_node("intake", intake_agent.run)
    workflow.add_node("transcription", transcription_agent.run)
    workflow.add_node("summarization", summarization_agent.run)
    workflow.add_node("critic", critic_agent.run)
    workflow.add_node("qa_scoring", qa_agent.run)

    # Define conditional routing
    def should_continue_after_critic(state):
        """Decide whether to revise summary or continue to QA"""
        if state.needs_revision and state.revision_count < 3:
            return "summarization"  # Send back for revision
        else:
            return "qa_scoring"  # Continue to QA

    # Set entry point
    workflow.set_entry_point("intake")
    
    # Linear flow until critic
    workflow.add_edge("intake", "transcription")
    workflow.add_edge("transcription", "summarization")
    workflow.add_edge("summarization", "critic")
    
    # Conditional routing after critic
    workflow.add_conditional_edges(
        "critic",
        should_continue_after_critic,
        {
            "summarization": "summarization",  # Loop back for revision
            "qa_scoring": "qa_scoring"  # Continue forward
        }
    )
    
    # Final edge
    workflow.add_edge("qa_scoring", END)

    # Compile the workflow
    app = workflow.compile()

    return app


def run_phase4_analysis(
    raw_input: str,
    input_type: str = "transcript",
    input_file_path: str = None
) -> dict:
    """Run the Phase 4 call analysis workflow with critic loop"""

    # Create initial state
    initial_state = AgentState(
        raw_input=raw_input,
        input_type=input_type,
        input_file_path=input_file_path
    )

    # Get workflow
    app = create_phase4_workflow()

    # Run the workflow
    final_state = app.invoke(initial_state)

    return final_state
