from models.schemas import CallMetadata, AgentState
from datetime import datetime
import uuid
import os

class IntakeAgent:
    """Agent that validates input and extracts metadata"""

    def __init__(self):
        self.model_name = "rule-based"  # No LLM needed for basic intake

    def run(self, state: AgentState) -> AgentState:
        """Extract metadata from input"""

        # Generate call ID
        call_id = f"CALL-{uuid.uuid4().hex[:8].upper()}"

        # Determine input type
        input_type = state.input_type

        # Calculate approximate duration (rough estimate from text length)
        if state.raw_input:
            # Rough estimate: ~150 words per minute of conversation
            word_count = len(state.raw_input.split())
            estimated_duration = (word_count / 150) * 60  # seconds
        else:
            estimated_duration = None

        # Create metadata
        metadata = CallMetadata(
            call_id=call_id,
            timestamp=datetime.now(),
            duration_seconds=estimated_duration,
            input_type=input_type,
            file_name=state.input_file_path
        )

        # Update state
        state.metadata = metadata
        state.execution_path.append("intake")
        state.models_used.append(self.model_name)

        return state
