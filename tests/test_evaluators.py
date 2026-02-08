"""Unit tests for evaluators"""
import pytest
import os
from models.schemas import QAScores
from evaluation.evaluators.faithfulness import FaithfulnessEvaluator
from evaluation.evaluators.completeness import CompletenessEvaluator
from evaluation.evaluators.qa_validator import QAScoreValidator


class TestFaithfulnessEvaluator:
    def test_evaluator_initialization(self):
        evaluator = FaithfulnessEvaluator()
        assert evaluator is not None

    def test_evaluate_faithful_summary(self):
        evaluator = FaithfulnessEvaluator()
        
        transcript = "Customer: I was charged twice. Agent: I'll refund you."
        summary_dict = {
            "brief_summary": "Customer was charged twice and agent issued refund",
            "key_points": ["Duplicate charge", "Refund issued"],
            "customer_intent": "Get refund for duplicate charge",
            "resolution_status": "RESOLVED",
            "topics": ["billing"],
            "sentiment": "NEUTRAL"
        }
        
        # This test would make an API call, so we skip it unless API key is available
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("Requires OPENAI_API_KEY")
        
        result = evaluator.evaluate(transcript, summary_dict)
        
        assert result is not None
        assert hasattr(result, "score")
        assert result.score >= 1
        assert result.score <= 10


class TestCompletenessEvaluator:
    def test_evaluator_initialization(self):
        evaluator = CompletenessEvaluator()
        assert evaluator is not None

    def test_evaluate_complete_summary(self):
        evaluator = CompletenessEvaluator()
        
        transcript = "Customer: Billing issue. Agent: Fixed it."
        summary_dict = {
            "brief_summary": "Customer had billing issue, agent fixed it",
            "key_points": ["Billing issue", "Issue resolved"],
            "customer_intent": "Fix billing",
            "resolution_status": "RESOLVED",
            "topics": ["billing"],
            "sentiment": "POSITIVE"
        }
        
        # This test would make an API call, so we skip it unless API key is available
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("Requires OPENAI_API_KEY")
        
        result = evaluator.evaluate(transcript, summary_dict)
        
        assert result is not None
        assert hasattr(result, "score")


class TestQAScoreValidator:
    def test_validator_initialization(self):
        validator = QAScoreValidator()
        assert validator is not None

    def test_validate_valid_scores(self):
        validator = QAScoreValidator()
        
        scores_dict = {
            "empathy": 8.5,
            "professionalism": 9.0,
            "resolution": 7.5,
            "tone": 8.0,
            "overall": 8.2,
            "comments": "Good performance"
        }
        
        result = validator.validate(scores_dict)
        
        assert result.is_valid is True
        assert len(result.issues) == 0

    def test_validate_out_of_range_scores(self):
        validator = QAScoreValidator()
        
        # This should fail validation in the model itself
        with pytest.raises(ValueError):
            QAScores(
                empathy=11.0,  # > 10
                professionalism=9.0,
                resolution=8.0,
                tone=7.0
            )

    def test_validate_missing_comments(self):
        validator = QAScoreValidator()
        
        scores_dict = {
            "empathy": 8.0,
            "professionalism": 9.0,
            "resolution": 7.0,
            "tone": 8.0,
            "overall": 8.0,
            "comments": ""  # Empty comments
        }
        
        result = validator.validate(scores_dict)
        
        # Should still be valid, but may have warnings
        assert result.is_valid is True
