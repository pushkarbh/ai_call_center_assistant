from models.schemas import TranscriptData, TranscriptSegment, AgentState
from openai import OpenAI
import os

class TranscriptionAgent:
    """Agent that handles transcription (pass-through for text, Whisper for audio)"""

    def __init__(self):
        self.model_name = "whisper-1"
        self.client = None  # Lazy initialization

    def _get_client(self):
        """Lazy initialization of OpenAI client"""
        if self.client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")
            self.client = OpenAI(api_key=api_key)
        return self.client

    def run(self, state: AgentState) -> AgentState:
        """Transcribe audio or pass through text"""

        if state.input_type == "transcript":
            # Text input - create transcript structure from raw text
            transcript = TranscriptData(
                segments=[],  # No speaker diarization for plain text
                full_text=state.raw_input,
                language="en",
                confidence=1.0
            )
            state.models_used.append("pass-through")

        elif state.input_type == "audio":
            # Audio input - use Whisper API
            # Note: In Phase 3, we'll just handle the structure
            # Full audio transcription will be implemented when needed
            client = self._get_client()
            # TODO: Implement actual Whisper API call
            transcript = TranscriptData(
                segments=[],
                full_text=state.raw_input or "",
                language="en",
                confidence=0.95
            )
            state.models_used.append(self.model_name)

        else:
            raise ValueError(f"Unknown input type: {state.input_type}")

        state.transcript = transcript
        state.execution_path.append("transcription")

        return state
