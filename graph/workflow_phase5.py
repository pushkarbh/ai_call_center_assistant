from langgraph.graph import StateGraph, END
from models.schemas import AgentState
from agents.input_validation_agent import InputValidationAgent
from agents.intake_agent import IntakeAgent
from agents.transcription_agent import TranscriptionAgent
from agents.summarization_agent import SummarizationAgent
from agents.critic_agent import CriticAgent
from agents.abuse_detection_agent import AbuseDetectionAgent
from agents.qa_scoring_agent import QAScoringAgent

def create_phase5_workflow():
    """Create Phase 5 workflow with Guardrails (Input Validation + Abuse Detection)"""

    # Initialize agents
    validation_agent = InputValidationAgent()
    intake_agent = IntakeAgent()
    transcription_agent = TranscriptionAgent()
    abuse_detection_agent = AbuseDetectionAgent()
    summarization_agent = SummarizationAgent()
    critic_agent = CriticAgent()
    qa_agent = QAScoringAgent()

    # Create workflow graph
    workflow = StateGraph(AgentState)

    # Define agent nodes
    workflow.add_node("validation", validation_agent.run)
    workflow.add_node("intake", intake_agent.run)
    workflow.add_node("transcription", transcription_agent.run)
    workflow.add_node("abuse_detection", abuse_detection_agent.run)
    workflow.add_node("summarization", summarization_agent.run)
    workflow.add_node("critic", critic_agent.run)
    workflow.add_node("qa_scoring", qa_agent.run)

    # Conditional routing functions
    def should_continue_after_validation(state):
        """Stop if validation fails, otherwise continue"""
        if not state.validation_result or not state.validation_result.is_valid:
            return "END"
        return "intake"

    def should_continue_after_critic(state):
        """Decide whether to revise summary or continue to QA"""
        if state.needs_revision and state.revision_count < 3:
            return "summarization"
        else:
            return "qa_scoring"

    # Set entry point
    workflow.set_entry_point("validation")
    
    # Conditional flow after validation
    workflow.add_conditional_edges(
        "validation",
        should_continue_after_validation,
        {
            "intake": "intake",
            "END": END
        }
    )
    
    # Linear flow: intake -> transcription -> abuse_detection
    workflow.add_edge("intake", "transcription")
    workflow.add_edge("transcription", "abuse_detection")
    
    # After abuse detection, continue to summarization
    workflow.add_edge("abuse_detection", "summarization")
    
    # Critic and revision loop
    workflow.add_edge("summarization", "critic")
    workflow.add_conditional_edges(
        "critic",
        should_continue_after_critic,
        {
            "summarization": "summarization",
            "qa_scoring": "qa_scoring"
        }
    )
    
    # Final edge
    workflow.add_edge("qa_scoring", END)

    # Compile the workflow
    app = workflow.compile()

    return app


def run_phase5_analysis(
    raw_input: str,
    input_type: str = "transcript",
    input_file_path: str = None
) -> dict:
    """Run the Phase 5 call analysis workflow with guardrails"""

    # Create initial state
    initial_state = AgentState(
        raw_input=raw_input,
        input_type=input_type,
        input_file_path=input_file_path
    )

    # Get workflow
    app = create_phase5_workflow()

    # Run the workflow
    final_state = app.invoke(initial_state)

    return final_state
