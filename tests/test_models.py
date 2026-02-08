"""Unit tests for Pydantic models"""
import pytest
from datetime import datetime
from models.schemas import (
    CallMetadata,
    TranscriptData,
    CallSummary,
    QAScores,
    SummaryCritique,
    AbuseFlag,
    InputValidationResult,
    AgentState,
    Sentiment,
    ResolutionStatus,
    AbuseType,
    AbuseSeverity
)


class TestCallMetadata:
    def test_call_metadata_creation(self):
        metadata = CallMetadata(
            call_id="CALL-12345678",
            duration_seconds=120.5,
            input_type="transcript",
            file_name="test.txt"
        )
        assert metadata.call_id == "CALL-12345678"
        assert metadata.duration_seconds == 120.5
        assert metadata.input_type == "transcript"
        assert isinstance(metadata.timestamp, datetime)

    def test_call_metadata_minimal(self):
        metadata = CallMetadata(
            call_id="CALL-ABC",
            input_type="audio"
        )
        assert metadata.call_id == "CALL-ABC"
        assert metadata.duration_seconds is None


class TestTranscriptData:
    def test_transcript_data_creation(self):
        transcript = TranscriptData(
            full_text="Customer: Hello. Agent: How can I help?",
            language="en",
            confidence=0.95
        )
        assert transcript.full_text.startswith("Customer:")
        assert transcript.language == "en"
        assert transcript.confidence == 0.95

    def test_transcript_data_validation(self):
        with pytest.raises(ValueError):
            TranscriptData(
                full_text="test",
                confidence=1.5  # Invalid: > 1.0
            )


class TestCallSummary:
    def test_call_summary_creation(self):
        summary = CallSummary(
            brief_summary="Customer had billing issue, resolved",
            key_points=["Duplicate charge", "Refund issued"],
            action_items=["Follow up in 3 days"],
            customer_intent="Get refund for duplicate charge",
            resolution_status=ResolutionStatus.RESOLVED,
            topics=["billing", "refund"],
            sentiment=Sentiment.POSITIVE
        )
        assert len(summary.key_points) == 2
        assert summary.resolution_status == ResolutionStatus.RESOLVED
        assert summary.sentiment == Sentiment.POSITIVE

    def test_call_summary_defaults(self):
        summary = CallSummary(
            brief_summary="Test",
            key_points=["Point 1"],
            customer_intent="Test intent",
            resolution_status=ResolutionStatus.UNRESOLVED,
            topics=["test"],
            sentiment=Sentiment.NEUTRAL
        )
        assert summary.action_items == []


class TestQAScores:
    def test_qa_scores_creation(self):
        scores = QAScores(
            empathy=8.5,
            professionalism=9.0,
            resolution=7.5,
            tone=8.0,
            comments="Good overall performance"
        )
        assert scores.empathy == 8.5
        # Average is rounded to 1 decimal: (8.5+9.0+7.5+8.0)/4 = 8.25 -> 8.2
        assert scores.overall == 8.2

    def test_qa_scores_validation(self):
        with pytest.raises(ValueError):
            QAScores(
                empathy=11.0,  # Invalid: > 10
                professionalism=9.0,
                resolution=8.0,
                tone=7.0
            )

    def test_qa_scores_overall_calculation(self):
        scores = QAScores(
            empathy=10.0,
            professionalism=8.0,
            resolution=6.0,
            tone=8.0
        )
        assert scores.overall == 8.0


class TestSummaryCritique:
    def test_critique_needs_revision(self):
        critique = SummaryCritique(
            faithfulness_score=6,
            completeness_score=8,
            conciseness_score=9,
            needs_revision=True,
            revision_instructions="Improve faithfulness",
            feedback="Summary has some inaccuracies"
        )
        assert critique.needs_revision is True
        assert critique.faithfulness_score == 6

    def test_critique_approved(self):
        critique = SummaryCritique(
            faithfulness_score=9,
            completeness_score=8,
            conciseness_score=9,
            needs_revision=False,
            feedback="Excellent summary"
        )
        assert critique.needs_revision is False


class TestAbuseFlag:
    def test_abuse_flag_detected(self):
        flag = AbuseFlag(
            detected=True,
            speaker="customer",
            abuse_type=[AbuseType.PROFANITY, AbuseType.HARASSMENT],
            severity=AbuseSeverity.MEDIUM,
            evidence=["Example text 1", "Example text 2"],
            recommended_action="Notify supervisor",
            requires_escalation=True
        )
        assert flag.detected is True
        assert len(flag.abuse_type) == 2
        assert flag.severity == AbuseSeverity.MEDIUM

    def test_abuse_flag_not_detected(self):
        flag = AbuseFlag()
        assert flag.detected is False
        assert flag.abuse_type == [AbuseType.NONE]
        assert flag.severity == AbuseSeverity.NONE


class TestInputValidationResult:
    def test_validation_passed(self):
        result = InputValidationResult(
            is_valid=True,
            confidence=0.95,
            input_type_detected="transcript",
            issues=[]
        )
        assert result.is_valid is True
        assert result.rejection_reason is None

    def test_validation_failed(self):
        result = InputValidationResult(
            is_valid=False,
            confidence=0.3,
            input_type_detected="unknown",
            issues=["Too short", "No structure"],
            rejection_reason="Input too short (< 10 words)"
        )
        assert result.is_valid is False
        assert len(result.issues) == 2


class TestAgentState:
    def test_agent_state_initialization(self):
        state = AgentState(
            raw_input="Test transcript",
            input_type="transcript"
        )
        assert state.raw_input == "Test transcript"
        assert state.input_type == "transcript"
        assert state.execution_path == []
        assert state.revision_count == 0

    def test_agent_state_with_metadata(self):
        metadata = CallMetadata(
            call_id="CALL-TEST",
            input_type="transcript"
        )
        state = AgentState(
            raw_input="Test",
            input_type="transcript",
            metadata=metadata
        )
        assert state.metadata.call_id == "CALL-TEST"

    def test_agent_state_execution_tracking(self):
        state = AgentState(
            raw_input="Test",
            input_type="transcript",
            execution_path=["intake", "transcription"],
            models_used=["rule-based", "pass-through"]
        )
        assert len(state.execution_path) == 2
        assert len(state.models_used) == 2
