from models.schemas import TranscriptData, TranscriptSegment, AgentState
from openai import OpenAI
import os
import io

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

    def _transcribe_audio(self, audio_data: bytes, file_name: str = "audio.mp3") -> str:
        """Transcribe audio using OpenAI Whisper API

        Args:
            audio_data: Raw audio bytes
            file_name: Original file name (used to determine format)

        Returns:
            Transcribed text
        """
        client = self._get_client()

        # Wrap bytes in a file-like object with the correct name
        # The name helps Whisper understand the audio format
        audio_file = io.BytesIO(audio_data)
        audio_file.name = file_name

        # Call Whisper API
        response = client.audio.transcriptions.create(
            model=self.model_name,
            file=audio_file,
            response_format="verbose_json"  # Get detailed response with segments
        )

        return response

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
            if not state.audio_data:
                raise ValueError("Audio input type specified but no audio_data provided")

            client = self._get_client()

            # Get file name for format detection
            file_name = state.input_file_path or "audio.mp3"

            # Transcribe using Whisper
            response = self._transcribe_audio(state.audio_data, file_name)

            # Extract segments if available
            segments = []
            if hasattr(response, 'segments') and response.segments:
                for seg in response.segments:
                    # Handle both dict and object responses
                    if isinstance(seg, dict):
                        text = seg.get('text', '').strip()
                        start = seg.get('start', 0.0)
                        end = seg.get('end', 0.0)
                    else:
                        text = getattr(seg, 'text', '').strip()
                        start = getattr(seg, 'start', 0.0)
                        end = getattr(seg, 'end', 0.0)

                    segments.append(TranscriptSegment(
                        speaker="Speaker",  # Whisper doesn't do diarization
                        text=text,
                        start_time=start,
                        end_time=end
                    ))

            transcript = TranscriptData(
                segments=segments,
                full_text=response.text,
                language=getattr(response, 'language', 'en'),
                confidence=0.95  # Whisper doesn't return confidence scores
            )
            state.models_used.append(self.model_name)

        else:
            raise ValueError(f"Unknown input type: {state.input_type}")

        state.transcript = transcript
        state.execution_path.append("transcription")

        return state
