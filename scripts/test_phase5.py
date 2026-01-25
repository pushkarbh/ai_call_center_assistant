#!/usr/bin/env python
"""Test script for Phase 5 workflow with Guardrails"""

import os
from dotenv import load_dotenv
load_dotenv()

# Disable LangSmith for testing
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from graph.workflow_phase5 import run_phase5_analysis

# Test 1: Normal transcript (should pass validation, no abuse)
print("=" * 60)
print("TEST 1: Normal Transcript")
print("=" * 60)

normal_transcript = """Customer: Hi, I need help with my account.
Agent: I'd be happy to help. What seems to be the issue?
Customer: I was charged twice for my subscription.
Agent: I apologize for that. Let me check your account right away.
Customer: Thank you.
Agent: I've found the duplicate charge and processed a refund. It should appear in 3-5 business days.
Customer: Great, thank you so much!
Agent: You're welcome. Is there anything else I can help with?
Customer: No, that's all. Have a good day!"""

result1 = run_phase5_analysis(normal_transcript, "transcript")
print(f"✅ Validation: {result1['validation_result'].is_valid}")
print(f"🚨 Abuse Flags: {len(result1['abuse_flags'])}")
print(f"📍 Path: {' → '.join(result1['execution_path'])}")

# Test 2: Short transcript (should fail validation)
print("\n" + "=" * 60)
print("TEST 2: Too Short (Validation Should Fail)")
print("=" * 60)

short_transcript = "Hello. Bye."

result2 = run_phase5_analysis(short_transcript, "transcript")
print(f"✅ Validation: {result2['validation_result'].is_valid}")
if not result2['validation_result'].is_valid:
    print(f"❌ Issues: {result2['validation_result'].issues}")
print(f"📍 Path: {' → '.join(result2['execution_path'])}")

# Test 3: Abusive language (should detect abuse)
print("\n" + "=" * 60)
print("TEST 3: Abusive Language")
print("=" * 60)

abusive_transcript = """Customer: This is bullshit! You people are idiots!
Agent: I understand you're frustrated. Let me help you.
Customer: You're damn right I'm frustrated! This is the worst service I've ever seen!
Agent: I apologize for the experience. What can I do to help resolve this?
Customer: Fix your damn system! This is ridiculous!
Agent: I'll escalate this to my supervisor right away."""

result3 = run_phase5_analysis(abusive_transcript, "transcript")
print(f"✅ Validation: {result3['validation_result'].is_valid}")
print(f"🚨 Abuse Flags: {len(result3['abuse_flags'])}")
if result3['abuse_flags']:
    for flag in result3['abuse_flags']:
        print(f"   - {flag.abuse_type.value} ({flag.severity.value}): \"{flag.quoted_text[:50]}...\"")
print(f"📍 Path: {' → '.join(result3['execution_path'])}")

print("\n✅ Phase 5 Guardrails workflow complete!")
