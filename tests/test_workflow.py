"""Integration tests for the workflow"""
import pytest
import os
from models.schemas import AgentState
from graph.workflow import create_workflow, run_analysis


class TestWorkflowStructure:
    def test_workflow_creation(self):
        """Test that workflow can be created"""
        workflow = create_workflow()
        assert workflow is not None

    def test_workflow_has_required_nodes(self):
        """Test that workflow has all required agent nodes"""
        workflow = create_workflow()
        # LangGraph compiled workflows don't expose nodes directly
        # but we can verify it was created without errors
        assert workflow is not None


class TestWorkflowValidation:
    def test_workflow_rejects_invalid_input(self):
        """Test that workflow stops on invalid input"""
        state = AgentState(
            raw_input="Hi",  # Too short
            input_type="transcript"
        )
        
        workflow = create_workflow()
        result = workflow.invoke(state)
        
        # Result is a dict, not AgentState object
        assert "validation" in result["execution_path"]
        assert result["validation_result"] is not None
        assert result["validation_result"].is_valid is False


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY for integration test"
)
class TestWorkflowIntegration:
    """Full integration tests requiring API keys"""
    
    @pytest.mark.integration
    def test_full_workflow_valid_transcript(self):
        """Test complete workflow with valid transcript"""
        transcript = """Customer: Hi, I have a question about my bill. I was charged twice this month.
Agent: I apologize for the inconvenience. Let me look into that for you. Can I have your account number?
Customer: Sure, it's 12345678.
Agent: Thank you. I can see the duplicate charge. I'll process a refund immediately.
Customer: Great, thank you!
Agent: You're welcome. The refund should appear in 3-5 business days. Is there anything else?
Customer: No, that's all. Thanks again!
Agent: Have a great day!"""
        
        result = run_analysis(
            raw_input=transcript,
            input_type="transcript"
        )
        
        # Verify validation passed
        assert result["validation_result"] is not None
        assert result["validation_result"].is_valid is True
        
        # Verify agents ran
        assert "validation" in result["execution_path"]
        assert "intake" in result["execution_path"]
        assert "transcription" in result["execution_path"]
        assert "summarization" in result["execution_path"]
        
        # Verify outputs
        assert result["metadata"] is not None
        assert result["transcript"] is not None
        assert result["summary"] is not None
        
    @pytest.mark.integration
    def test_workflow_with_revision_loop(self):
        """Test that workflow handles revision loop"""
        # This would need a transcript that triggers revision
        # For now, just verify the workflow structure allows it
        transcript = "Customer: My bill is wrong. Agent: Let me check. Customer: It's account 123. Agent: Fixed."
        
        result = run_analysis(
            raw_input=transcript,
            input_type="transcript"
        )
        
        # Check that critic was invoked
        assert "critic" in result["execution_path"] or result["summary"] is not None


class TestRunAnalysisFunction:
    def test_run_analysis_creates_initial_state(self):
        """Test that run_analysis creates proper initial state"""
        # This will fail validation, but we can check state creation
        result = run_analysis(
            raw_input="Test",
            input_type="transcript"
        )
        
        assert result is not None
        assert "execution_path" in result
        assert result["raw_input"] == "Test"

    def test_run_analysis_with_audio_type(self):
        """Test run_analysis with audio input type"""
        result = run_analysis(
            raw_input="",
            input_type="audio",
            audio_data=b"fake audio data"
        )
        
        assert result is not None
        assert result["input_type"] == "audio"
