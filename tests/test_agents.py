"""Unit tests for individual agents"""
import pytest
import os
from unittest.mock import Mock, patch
from models.schemas import (
    AgentState,
    CallMetadata,
    TranscriptData,
    InputValidationResult,
    Sentiment,
    ResolutionStatus
)
from agents.intake_agent import IntakeAgent
from agents.transcription_agent import TranscriptionAgent


class TestIntakeAgent:
    def test_intake_agent_initialization(self):
        agent = IntakeAgent()
        assert agent.model_name == "rule-based"

    def test_intake_agent_generates_call_id(self):
        agent = IntakeAgent()
        state = AgentState(
            raw_input="Customer: Hello. Agent: Hi there.",
            input_type="transcript"
        )
        
        result = agent.run(state)
        
        assert result.metadata is not None
        assert result.metadata.call_id.startswith("CALL-")
        assert len(result.metadata.call_id) == 13  # CALL- + 8 chars
        assert "intake" in result.execution_path

    def test_intake_agent_estimates_duration(self):
        agent = IntakeAgent()
        # Create transcript with ~150 words (should be ~1 minute)
        words = " ".join(["word"] * 150)
        state = AgentState(
            raw_input=words,
            input_type="transcript"
        )
        
        result = agent.run(state)
        
        # Rough estimate: 150 words / 150 wpm = 1 minute = 60 seconds
        assert result.metadata.duration_seconds is not None
        assert 50 < result.metadata.duration_seconds < 70


class TestTranscriptionAgent:
    def test_transcription_agent_text_passthrough(self):
        agent = TranscriptionAgent()
        state = AgentState(
            raw_input="Customer: Hello. Agent: Hi.",
            input_type="transcript"
        )
        
        result = agent.run(state)
        
        assert result.transcript is not None
        assert result.transcript.full_text == "Customer: Hello. Agent: Hi."
        assert result.transcript.confidence == 1.0
        assert "transcription" in result.execution_path
        assert "pass-through" in result.models_used

    def test_transcription_agent_audio_placeholder(self):
        """Test audio handling with mocked API call"""
        from unittest.mock import patch, MagicMock
        
        agent = TranscriptionAgent()
        state = AgentState(
            raw_input="",
            input_type="audio",
            audio_data=b"fake audio bytes"
        )
        
        # Create a proper mock response object
        mock_response = MagicMock()
        mock_response.text = "This is a mocked transcription from audio."
        mock_response.language = "en"
        mock_response.segments = []  # No segments for simplicity
        
        # Patch the _transcribe_audio method directly
        with patch.object(agent, '_transcribe_audio', return_value=mock_response):
            result = agent.run(state)
            
            assert result.transcript is not None
            assert result.transcript.full_text == "This is a mocked transcription from audio."
            assert result.transcript.language == "en"
            assert "transcription" in result.execution_path


class TestInputValidationAgent:
    @pytest.fixture
    def agent(self):
        from agents.input_validation_agent import InputValidationAgent
        return InputValidationAgent()

    def test_validation_agent_valid_transcript(self, agent):
        state = AgentState(
            raw_input="Customer: I have a question about my bill. Agent: I'd be happy to help. What's the issue? Customer: I was charged twice.",
            input_type="transcript"
        )
        
        result = agent.run(state)
        
        assert result.validation_result is not None
        assert result.validation_result.is_valid is True
        assert "validation" in result.execution_path

    def test_validation_agent_too_short(self, agent):
        state = AgentState(
            raw_input="Hello. Bye.",  # Too short
            input_type="transcript"
        )
        
        result = agent.run(state)
        
        assert result.validation_result is not None
        assert result.validation_result.is_valid is False
        assert len(result.validation_result.issues) > 0


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY"
)
class TestSummarizationAgentIntegration:
    """Integration tests requiring actual API calls"""
    
    def test_summarization_with_mock(self):
        """Test with mocked LLM response"""
        from agents.summarization_agent import SummarizationAgent
        from models.schemas import CallSummary
        
        mock_summary = CallSummary(
            brief_summary="Customer called about billing issue",
            key_points=["Duplicate charge", "Refund requested"],
            customer_intent="Get refund",
            resolution_status=ResolutionStatus.RESOLVED,
            topics=["billing"],
            sentiment=Sentiment.NEUTRAL
        )
        
        with patch.object(SummarizationAgent, 'run') as mock_run:
            mock_run.return_value = AgentState(
                raw_input="test",
                input_type="transcript",
                summary=mock_summary
            )
            
            agent = SummarizationAgent()
            state = AgentState(
                raw_input="Customer: I was charged twice. Agent: Let me help.",
                input_type="transcript"
            )
            state.transcript = TranscriptData(full_text=state.raw_input)
            
            result = mock_run(state)
            
            assert result.summary is not None
            assert result.summary.brief_summary == "Customer called about billing issue"


@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="Requires ANTHROPIC_API_KEY"
)
class TestCriticAgentIntegration:
    """Integration tests requiring actual API calls"""
    
    def test_critic_with_mock(self):
        """Test with mocked LLM response"""
        from agents.critic_agent import CriticAgent
        from models.schemas import SummaryCritique
        
        mock_critique = SummaryCritique(
            faithfulness_score=8,
            completeness_score=9,
            conciseness_score=8,
            needs_revision=False,
            feedback="Good summary"
        )
        
        with patch.object(CriticAgent, 'run') as mock_run:
            mock_state = AgentState(
                raw_input="test",
                input_type="transcript",
                summary_critique=mock_critique
            )
            mock_run.return_value = mock_state
            
            agent = CriticAgent()
            state = AgentState(
                raw_input="Customer: Hello. Agent: Hi.",
                input_type="transcript"
            )
            
            result = mock_run(state)
            
            assert result.summary_critique is not None
            assert result.summary_critique.needs_revision is False
