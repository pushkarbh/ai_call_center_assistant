"""
QA Score Validator - Heuristic Evaluator

Validates that QA scores are within expected ranges and all required fields are present.
Also checks for consistency between scores and the transcript content.
"""

from typing import Optional
from pydantic import BaseModel, Field


class QAValidationResult(BaseModel):
    """Result of QA score validation"""
    is_valid: bool = Field(description="Whether all validations passed")
    score: float = Field(ge=0, le=1, description="Validation score 0-1")
    issues: list[str] = Field(default=[], description="List of validation issues found")
    warnings: list[str] = Field(default=[], description="Non-critical warnings")


class QAScoreValidator:
    """Validates QA scores for correctness and consistency"""

    def __init__(self):
        self.required_fields = ["empathy", "professionalism", "resolution", "tone", "overall"]
        self.score_range = (0, 10)

    def validate(self, qa_scores: dict, transcript: str = None, expected: dict = None) -> QAValidationResult:
        """Validate QA scores

        Args:
            qa_scores: Dictionary of QA scores
            transcript: Optional transcript for consistency checks
            expected: Optional expected values for comparison

        Returns:
            QAValidationResult with validation status and issues
        """
        issues = []
        warnings = []

        if not qa_scores:
            return QAValidationResult(
                is_valid=False,
                score=0,
                issues=["No QA scores provided"]
            )

        # Check required fields
        for field in self.required_fields:
            if field not in qa_scores:
                issues.append(f"Missing required field: {field}")

        # Check score ranges
        for field, value in qa_scores.items():
            if field in self.required_fields:
                if not isinstance(value, (int, float)):
                    issues.append(f"Invalid type for {field}: expected number, got {type(value).__name__}")
                elif value < self.score_range[0] or value > self.score_range[1]:
                    issues.append(f"{field} score {value} out of range {self.score_range}")

        # Check overall score consistency
        if all(f in qa_scores for f in ["empathy", "professionalism", "resolution", "tone", "overall"]):
            component_avg = (
                qa_scores["empathy"] +
                qa_scores["professionalism"] +
                qa_scores["resolution"] +
                qa_scores["tone"]
            ) / 4

            # Overall should be reasonably close to component average
            if abs(qa_scores["overall"] - component_avg) > 2:
                warnings.append(
                    f"Overall score ({qa_scores['overall']}) differs significantly from "
                    f"component average ({component_avg:.1f})"
                )

        # Check for suspiciously uniform scores
        score_values = [v for k, v in qa_scores.items() if k in self.required_fields[:4]]
        if len(set(score_values)) == 1 and len(score_values) == 4:
            warnings.append("All component scores are identical - may indicate low-effort evaluation")

        # Transcript-based consistency checks
        if transcript:
            transcript_lower = transcript.lower()

            # If customer uses profanity but professionalism score is very high
            profanity_indicators = ["bullshit", "damn", "crap", "hell", "ass"]
            has_profanity = any(word in transcript_lower for word in profanity_indicators)

            # If there are threats mentioned
            threat_indicators = ["sue", "lawyer", "come down to your office", "make sure someone pays"]
            has_threats = any(phrase in transcript_lower for phrase in threat_indicators)

            # These are just warnings, not failures
            if has_profanity and qa_scores.get("tone", 0) > 8:
                warnings.append("High tone score despite profanity in transcript")

            if has_threats and qa_scores.get("tone", 0) > 6:
                warnings.append("High tone score despite threatening language in transcript")

        # Compare with expected values if provided
        if expected:
            for field, expected_value in expected.items():
                if field in qa_scores:
                    actual = qa_scores[field]
                    if abs(actual - expected_value) > 3:
                        warnings.append(
                            f"{field}: actual ({actual}) differs significantly from expected ({expected_value})"
                        )

        # Calculate final score
        is_valid = len(issues) == 0
        num_checks = 5 + len(self.required_fields)  # Basic checks
        failed_checks = len(issues)
        score = max(0, (num_checks - failed_checks) / num_checks)

        # Reduce score slightly for warnings
        score -= len(warnings) * 0.05
        score = max(0, min(1, score))

        return QAValidationResult(
            is_valid=is_valid,
            score=score,
            issues=issues,
            warnings=warnings
        )


def qa_score_validator(run, example) -> dict:
    """LangSmith-compatible evaluator function

    Args:
        run: The run object containing outputs
        example: The example object containing inputs and expected outputs

    Returns:
        Dictionary with score and reasoning
    """
    validator = QAScoreValidator()

    qa_scores = run.outputs.get("qa_scores", {})
    transcript = example.inputs.get("transcript", "")
    expected = example.outputs.get("expected_qa_scores") if example.outputs else None

    result = validator.validate(qa_scores, transcript, expected)

    comment = "Valid" if result.is_valid else f"Issues: {'; '.join(result.issues)}"
    if result.warnings:
        comment += f" | Warnings: {'; '.join(result.warnings)}"

    return {
        "key": "qa_score_validity",
        "score": result.score,
        "comment": comment
    }
