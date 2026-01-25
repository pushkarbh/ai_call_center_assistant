#!/usr/bin/env python
"""Test script for Phase 4 multi-agent workflow with Critic loop"""

import os
from dotenv import load_dotenv
load_dotenv()

# Disable LangSmith for testing
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from graph.workflow_phase4 import run_phase4_analysis

# Test with a transcript that might need revision
test_transcript = """Customer: Hi, my bill is wrong. You charged me twice!
Agent: Let me check that. What's your account number?
Customer: 12345678
Agent: I see a duplicate charge. I'll refund it. Should be back in 3-5 days.
Customer: Thanks!
Agent: You're welcome. Anything else?
Customer: No, that's all.
Agent: Have a great day!"""

print('🚀 Running Phase 4 multi-agent workflow with Critic...\n')
result = run_phase4_analysis(
    raw_input=test_transcript,
    input_type='transcript'
)

print('✅ Workflow completed!\n')
print(f'Type of result: {type(result)}')
print(f'📍 Execution path: {" → ".join(result["execution_path"])}')
print(f'🤖 Models used: {", ".join(result["models_used"])}')
print(f'🆔 Call ID: {result["metadata"].call_id}')

print(f'\n📝 Summary: {result["summary"].brief_summary[:150]}...')

if result.get("summary_critique"):
    critique = result["summary_critique"]
    print(f'\n🔍 Critique Scores:')
    print(f'   Faithfulness: {critique.faithfulness_score}/10')
    print(f'   Completeness: {critique.completeness_score}/10')
    print(f'   Conciseness: {critique.conciseness_score}/10')
    print(f'   Needs Revision: {critique.needs_revision}')
    print(f'   Revision Count: {result["revision_count"]}')

if result.get("qa_scores"):
    print(f'\n📊 QA Scores:')
    print(f'   Empathy: {result["qa_scores"].empathy}/10')
    print(f'   Professionalism: {result["qa_scores"].professionalism}/10')
    print(f'   Resolution: {result["qa_scores"].resolution}/10')
    print(f'   Tone: {result["qa_scores"].tone}/10')
    print(f'   Overall: {result["qa_scores"].overall}/10')

print('\n✅ Phase 4 multi-agent workflow with Critic is working!')
