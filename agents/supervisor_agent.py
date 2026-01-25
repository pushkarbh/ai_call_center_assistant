from models.schemas import AgentState
from typing import Literal

class SupervisorAgent:
    """Agent that routes workflow decisions based on state"""

    def __init__(self):
        self.model_name = "supervisor"

    def route_after_intake(self, state: AgentState) -> Literal["transcription", "END"]:
        """Route after intake: always go to transcription unless errors"""
        if state.errors:
            return "END"
        return "transcription"

    def route_after_transcription(self, state: AgentState) -> Literal["summarization", "END"]:
        """Route after transcription: always go to summarization unless errors"""
        if state.errors or not state.transcript:
            return "END"
        return "summarization"

    def route_after_critic(self, state: AgentState) -> Literal["summarization", "qa_scoring"]:
        """Route after critic: revision loop or continue to QA"""
        if state.needs_revision and state.revision_count < 3:
            # Send back for revision (max 3 attempts)
            return "summarization"
        else:
            # Continue to QA scoring
            return "qa_scoring"

    def route_after_qa(self, state: AgentState) -> Literal["END"]:
        """Route after QA: always end"""
        return "END"

    def run(self, state: AgentState) -> AgentState:
        """Supervisor doesn't modify state, just routes"""
        state.execution_path.append("supervisor")
        state.models_used.append(self.model_name)
        return state
