# Guardrail Test Transcripts

This folder contains test transcripts designed to validate the Phase 5 Guardrails functionality (Input Validation + Abuse Detection).

## Test Files

### Input Validation Tests

1. **01_valid_normal.txt** - Normal, valid transcript
   - Expected: Pass validation, no abuse flags
   - Word count: ~70 words
   - Structure: Proper conversation format

2. **02_too_short.txt** - Too short to be valid
   - Expected: FAIL validation (< 10 words)
   - Word count: ~7 words

3. **08_spam_repetition.txt** - Excessive word repetition
   - Expected: Pass validation with WARNING (low vocabulary diversity)
   - Flags spam-like behavior

4. **10_no_structure.txt** - Single paragraph, no speaker labels
   - Expected: Pass validation with WARNING (no speaker labels detected)
   - Long run-on text without dialogue format

### Abuse Detection Tests

5. **03_profanity.txt** - Mild to moderate profanity
   - Expected: Detect profanity abuse (low-medium severity)
   - Contains: "bullshit", "damn", "crap", "idiots"

6. **04_threats.txt** - Threats of legal action and physical harm
   - Expected: Detect threat abuse (medium-high severity)
   - Contains: lawsuit threats, physical threats, intimidation

7. **05_harassment.txt** - Personal attacks and insults
   - Expected: Detect harassment abuse (medium severity)
   - Contains: direct insults, competence attacks, name-calling

8. **06_hate_speech.txt** - Discriminatory language
   - Expected: Detect hate_speech abuse (high severity)
   - Contains: racial/nationality discrimination, xenophobic comments

9. **07_mixed_abuse.txt** - Multiple abuse types
   - Expected: Detect profanity, threat, AND harassment
   - Mix of profanity, legal threats, and insults

### Edge Cases

10. **09_frustrated_but_polite.txt** - Strong frustration without abuse
    - Expected: Pass validation, NO abuse flags
    - Shows normal customer frustration is not flagged as abuse

11. **11_professional_complaint.txt** - Professional complaint handling
    - Expected: Pass validation, NO abuse flags
    - Demonstrates proper escalation without abuse

## Testing Instructions

### Manual Testing
1. Load each file through the UI file uploader
2. Click "Analyze Call"
3. Verify validation results and abuse flags match expectations

### Automated Testing
```bash
python test_phase5.py
```

## Expected Results Summary

| File | Validation | Abuse Flags | Notes |
|------|-----------|-------------|-------|
| 01_valid_normal.txt | ✅ Pass | None | Clean conversation |
| 02_too_short.txt | ❌ Fail | N/A | Stops at validation |
| 03_profanity.txt | ✅ Pass | Profanity (low-med) | Multiple instances |
| 04_threats.txt | ✅ Pass | Threat (med-high) | Legal + physical |
| 05_harassment.txt | ✅ Pass | Harassment (med) | Personal attacks |
| 06_hate_speech.txt | ✅ Pass | Hate Speech (high) | Discrimination |
| 07_mixed_abuse.txt | ✅ Pass | Multiple types | Profanity + Threat + Harassment |
| 08_spam_repetition.txt | ⚠️ Pass w/ Warning | None | Low vocab diversity |
| 09_frustrated_but_polite.txt | ✅ Pass | None | No false positives |
| 10_no_structure.txt | ⚠️ Pass w/ Warning | None | Missing speaker labels |
| 11_professional_complaint.txt | ✅ Pass | None | Professional handling |

## Notes

- Validation agent catches structural issues before processing
- Abuse detection uses GPT-4o-mini for context-aware detection
- False positive rate should be low (frustrated ≠ abusive)
- Severity levels: low (1-3), medium (4-6), high (7-10)
