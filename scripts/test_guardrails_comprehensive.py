#!/usr/bin/env python
"""Comprehensive test suite for Guardrails using test transcripts"""

import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Disable LangSmith for testing
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from graph.workflow import run_analysis

# Define test cases with expected results
test_cases = [
    {
        "file": "01_valid_normal.txt",
        "name": "Valid Normal Transcript",
        "expect_validation": True,
        "expect_abuse": False,
        "expect_warnings": False
    },
    {
        "file": "02_too_short.txt",
        "name": "Too Short (Validation Failure)",
        "expect_validation": False,
        "expect_abuse": None,  # Won't process if validation fails
        "expect_warnings": False
    },
    {
        "file": "03_profanity.txt",
        "name": "Profanity Detection",
        "expect_validation": True,
        "expect_abuse": True,
        "expect_warnings": False
    },
    {
        "file": "04_threats.txt",
        "name": "Threat Detection",
        "expect_validation": True,
        "expect_abuse": True,
        "expect_warnings": False
    },
    {
        "file": "05_harassment.txt",
        "name": "Harassment Detection",
        "expect_validation": True,
        "expect_abuse": True,
        "expect_warnings": False
    },
    {
        "file": "06_hate_speech.txt",
        "name": "Hate Speech Detection",
        "expect_validation": True,
        "expect_abuse": True,
        "expect_warnings": False
    },
    {
        "file": "07_mixed_abuse.txt",
        "name": "Mixed Abuse Types",
        "expect_validation": True,
        "expect_abuse": True,
        "expect_warnings": False
    },
    {
        "file": "08_spam_repetition.txt",
        "name": "Spam/Repetition Warning",
        "expect_validation": True,
        "expect_abuse": False,
        "expect_warnings": True
    },
    {
        "file": "09_frustrated_but_polite.txt",
        "name": "Frustrated But Polite (No False Positive)",
        "expect_validation": True,
        "expect_abuse": False,
        "expect_warnings": False
    },
    {
        "file": "10_no_structure.txt",
        "name": "No Speaker Structure Warning",
        "expect_validation": True,
        "expect_abuse": False,
        "expect_warnings": True
    },
    {
        "file": "11_professional_complaint.txt",
        "name": "Professional Complaint (No False Positive)",
        "expect_validation": True,
        "expect_abuse": False,
        "expect_warnings": False
    }
]

test_dir = Path("test_data/guardrail_tests")
passed = 0
failed = 0
errors = []

print("=" * 80)
print("GUARDRAILS - COMPREHENSIVE TEST SUITE")
print("=" * 80)
print()

for i, test in enumerate(test_cases, 1):
    file_path = test_dir / test["file"]
    
    if not file_path.exists():
        print(f"❌ Test {i}: {test['name']}")
        print(f"   ERROR: File not found: {file_path}")
        failed += 1
        errors.append(f"Test {i}: File not found")
        print()
        continue
    
    print(f"Test {i}/{len(test_cases)}: {test['name']}")
    print(f"File: {test['file']}")
    
    try:
        # Load transcript
        transcript = file_path.read_text()
        
        # Run analysis
        result = run_analysis(transcript, "transcript")
        
        # Check validation result
        validation_passed = result['validation_result'].is_valid
        has_warnings = len(result['validation_result'].warnings) > 0
        has_abuse = len(result['abuse_flags']) > 0
        
        # Verify expectations
        test_passed = True
        
        # Check validation
        if validation_passed != test['expect_validation']:
            print(f"   ❌ FAIL: Expected validation={test['expect_validation']}, got {validation_passed}")
            test_passed = False
        else:
            print(f"   ✅ Validation: {validation_passed}")
        
        # Check warnings
        if test['expect_warnings'] and not has_warnings:
            print(f"   ❌ FAIL: Expected warnings, got none")
            test_passed = False
        elif not test['expect_warnings'] and has_warnings:
            print(f"   ⚠️  Unexpected warnings: {result['validation_result'].warnings}")
        
        if has_warnings:
            print(f"   ⚠️  Warnings: {len(result['validation_result'].warnings)}")
            for w in result['validation_result'].warnings:
                print(f"      - {w}")
        
        # Check abuse detection (only if validation passed)
        if validation_passed and test['expect_abuse'] is not None:
            if has_abuse != test['expect_abuse']:
                print(f"   ❌ FAIL: Expected abuse={test['expect_abuse']}, got {has_abuse}")
                test_passed = False
            else:
                print(f"   ✅ Abuse Detection: {has_abuse}")
            
            if has_abuse:
                print(f"   🚨 Abuse Flags: {len(result['abuse_flags'])}")
                for flag in result['abuse_flags']:
                    abuse_types_str = ", ".join([t.value for t in flag.abuse_type])
                    evidence_preview = flag.evidence[0][:40] if flag.evidence else "N/A"
                    print(f"      - {abuse_types_str} ({flag.severity.value}): \"{evidence_preview}...\"")
        
        # Show execution path
        print(f"   📍 Path: {' → '.join(result['execution_path'])}")
        
        if test_passed:
            print(f"   ✅ PASSED")
            passed += 1
        else:
            print(f"   ❌ FAILED")
            failed += 1
            errors.append(f"Test {i}: {test['name']}")
        
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        failed += 1
        errors.append(f"Test {i}: {test['name']} - {str(e)}")
    
    print()

# Summary
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total Tests: {len(test_cases)}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"Success Rate: {passed/len(test_cases)*100:.1f}%")

if errors:
    print("\nFailed Tests:")
    for error in errors:
        print(f"  - {error}")
    exit(1)
else:
    print("\n🎉 All tests passed!")
    exit(0)
