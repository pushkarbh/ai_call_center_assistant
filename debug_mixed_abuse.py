from dotenv import load_dotenv
load_dotenv()

from agents.abuse_detection_agent import AbuseDetectionAgent
from pathlib import Path

agent = AbuseDetectionAgent()

# Load the mixed abuse test file
test_file = Path("test_data/guardrail_tests/07_mixed_abuse.txt")
transcript_text = test_file.read_text()

print("=== TRANSCRIPT ===")
print(transcript_text)
print("\n" + "="*80 + "\n")

# Get LLM response
response = agent.chain.invoke({'transcript': transcript_text})
print("=== LLM RESPONSE ===")
print(response.content)
print("\n" + "="*80 + "\n")

# Parse into flags
flags = agent._parse_abuse_response(response.content)
print(f"=== PARSED FLAGS ({len(flags)}) ===")
for i, flag in enumerate(flags, 1):
    print(f"\n{i}. {', '.join([t.value for t in flag.abuse_type])} - {flag.severity.value}")
    print(f"   Evidence: {flag.evidence}")
    print(f"   Action: {flag.recommended_action[:80]}...")
