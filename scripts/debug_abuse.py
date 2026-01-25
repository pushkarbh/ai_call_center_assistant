from dotenv import load_dotenv
load_dotenv()

from agents.abuse_detection_agent import AbuseDetectionAgent

agent = AbuseDetectionAgent()

transcript_text = """Customer: This is the worst service! You guys are complete idiots!
Customer: Damn right! This is bullshit! I've been waiting over an hour!"""

response = agent.chain.invoke({'transcript': transcript_text})
print('=== LLM RESPONSE ===')
print(response.content)
print()
print('=== PARSED FLAGS ===')
flags = agent._parse_abuse_response(response.content)
print(f'Number of flags: {len(flags)}')
for flag in flags:
    print(f'  - {flag.abuse_type.value} ({flag.severity.value}): "{flag.quoted_text[:60]}"')
