from models.schemas import InputValidationResult, AgentState
import re

class InputValidationAgent:
    """Agent that validates input quality and flags potential issues"""

    def __init__(self):
        self.model_name = "input-validator"
        self.min_words = 10
        self.max_words = 5000

    def run(self, state: AgentState) -> AgentState:
        """Validate the input transcript"""
        
        if not state.raw_input:
            state.validation_result = InputValidationResult(
                is_valid=False,
                confidence=1.0,
                input_type_detected="empty",
                issues=["No input provided"],
                warnings=[],
                rejection_reason="No input text provided"
            )
            state.errors.append("Input validation failed: No input")
            state.execution_path.append("validation")
            state.models_used.append(self.model_name)
            return state

        raw_text = state.raw_input.strip()
        issues = []
        warnings = []

        # Word count validation
        word_count = len(raw_text.split())
        
        if word_count < self.min_words:
            issues.append(f"Input too short: {word_count} words (minimum: {self.min_words})")
        elif word_count > self.max_words:
            issues.append(f"Input too long: {word_count} words (maximum: {self.max_words})")
        
        # Check for reasonable conversation structure
        if ":" not in raw_text and word_count > 20:
            warnings.append("No speaker labels detected (missing 'Speaker:' or 'Agent:' format)")
        
        # Check for excessive special characters (may indicate corrupted text)
        special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s:.,!?\-\']', raw_text)) / len(raw_text)
        if special_char_ratio > 0.1:
            warnings.append(f"High special character ratio: {special_char_ratio:.1%}")
        
        # Check for excessive repetition (possible spam or corrupted input)
        words = raw_text.lower().split()
        if len(words) > 20:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.5:  # Less than 50% unique words
                warnings.append(f"Low vocabulary diversity: {unique_ratio:.1%} (possible spam or repetitive input)")
        
        # Check for minimum dialogue structure
        lines = raw_text.split('\n')
        if len(lines) < 2 and word_count > 50:
            warnings.append("Single-line input may not be a conversation transcript")
        
        # Determine if valid
        is_valid = len(issues) == 0
        
        # Detect input type
        if ":" in raw_text and len(lines) > 1:
            input_type_detected = "conversation"
        elif len(lines) > 5:
            input_type_detected = "multi-line-text"
        else:
            input_type_detected = "single-text"
        
        # Calculate confidence (higher confidence when no issues/warnings)
        confidence = 1.0
        if warnings:
            confidence -= 0.1 * len(warnings)
        if issues:
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))
        
        # Create validation result
        state.validation_result = InputValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            input_type_detected=input_type_detected,
            issues=issues,
            warnings=warnings,
            rejection_reason="; ".join(issues) if issues else None
        )
        
        if not is_valid:
            state.errors.extend(issues)
        
        state.execution_path.append("validation")
        state.models_used.append(self.model_name)
        
        return state
