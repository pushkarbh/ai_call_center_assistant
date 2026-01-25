#!/usr/bin/env python
"""Test script for Phase 3 multi-agent workflow"""

import os
from dotenv import load_dotenv
load_dotenv()

# Disable LangSmith for testing
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from graph.workflow import run_call_analysis

# Test with simple input
test_transcript = """Customer: Hi, I have a question about my bill. I was charged twice for my subscription this month.
Agent: I apologize for the inconvenience. Let me look into that for you right away. Can I have your account number?
Customer: Sure, it's 12345678.
Agent: Thank you. I see the duplicate charge. I'll process a refund immediately. It should appear in your account within 3-5 business days.
Customer: Great, thank you so much!
Agent: You're welcome! Is there anything else I can help you with today?
Customer: No, that's all. Thanks again!
Agent: Have a great day!"""

print('🚀 Running multi-agent workflow...\n')
result = run_call_analysis(
    raw_input=test_transcript,
    input_type='transcript'
)

print('✅ Workflow completed!\n')
print(f'Type of result: {type(result)}')
print(f'Result keys: {result.keys() if isinstance(result, dict) else "Not a dict"}')

# LangGraph returns a dict with the state
if isinstance(result, dict):
    print(f'\n📍 Execution path: {" → ".join(result["execution_path"])}')
    print(f'🤖 Models used: {", ".join(result["models_used"])}')
    print(f'🆔 Call ID: {result["metadata"].call_id}')
    print(f'\n📝 Summary: {result["summary"].brief_summary[:150]}...')
    print(f'\n📊 QA Scores:')
    print(f'   Empathy: {result["qa_scores"].empathy}/10')
    print(f'   Professionalism: {result["qa_scores"].professionalism}/10')
    print(f'   Resolution: {result["qa_scores"].resolution}/10')
    print(f'   Tone: {result["qa_scores"].tone}/10')
    
    avg = result["qa_scores"].overall
    print(f'   Overall: {avg:.1f}/10')
else:
    print(f'\n📍 Execution path: {" → ".join(result.execution_path)}')
    print(f'🤖 Models used: {", ".join(result.models_used)}')
    print(f'🆔 Call ID: {result.metadata.call_id}')
    print(f'\n📝 Summary: {result.summary.brief_summary[:150]}...')
    print(f'\n📊 QA Scores:')
    print(f'   Empathy: {result.qa_scores.empathy}/10')
    print(f'   Professionalism: {result.qa_scores.professionalism}/10')
    print(f'   Resolution: {result.qa_scores.resolution}/10')
    print(f'   Tone: {result.qa_scores.tone}/10')
    
    avg = result.qa_scores.overall
    print(f'   Overall: {avg:.1f}/10')

# Overall score already printed above

print('\n✅ Phase 3 multi-agent pipeline is working!')
