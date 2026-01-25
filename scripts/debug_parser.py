from dotenv import load_dotenv
load_dotenv()

from agents.abuse_detection_agent import AbuseDetectionAgent
import re

agent = AbuseDetectionAgent()

response_text = """TYPE: harassment  
SEVERITY: 5  
TEXT: "You guys are complete idiots!"  
CONTEXT: The customer is insulting the service representatives by calling them "complete idiots."

TYPE: profanity  
SEVERITY: 6  
TEXT: "Damn right! This is bullshit!"  
CONTEXT: The customer uses mild profanity to express frustration with the service."""

print('=== MANUAL PARSING ===')
type_pattern = r'TYPE:\s*(\w+)'
severity_pattern = r'SEVERITY:\s*(\d+)'
text_pattern = r'TEXT:\s*["\'](.+?)["\']'
context_pattern = r'CONTEXT:\s*(.+?)(?=TYPE:|$)'

entries = re.split(r'(?=TYPE:)', response_text.strip())
print(f'Entries: {len(entries)}')

for i, entry in enumerate(entries):
    print(f'\n--- Entry {i} (len={len(entry.strip())}) ---')
    if not entry.strip():
        print('Empty - SKIPPED')
        continue
    if 'TYPE:' not in entry:
        print('No TYPE: - SKIPPED')
        continue
    
    try:
        type_match = re.search(type_pattern, entry, re.IGNORECASE)
        severity_match = re.search(severity_pattern, entry)
        text_match = re.search(text_pattern, entry, re.DOTALL)
        context_match = re.search(context_pattern, entry, re.DOTALL)
        
        print(f'TYPE: {type_match.group(1) if type_match else "NONE"}')
        print(f'SEVERITY: {severity_match.group(1) if severity_match else "NONE"}')
        print(f'TEXT: {text_match.group(1) if text_match else "NONE"}')
        print(f'CONTEXT: {context_match.group(1)[:50] if context_match else "NONE"}...')
        
        if not type_match:
            print('NO TYPE MATCH - SKIPPED')
            continue
        
        print('SUCCESS - would create AbuseFlag')
    except Exception as e:
        print(f'EXCEPTION: {e}')

print('\n\n=== USING AGENT METHOD ===')
flags = agent._parse_abuse_response(response_text)
print(f'Flags returned: {len(flags)}')
