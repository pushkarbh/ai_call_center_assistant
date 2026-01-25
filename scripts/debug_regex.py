import re

response = """TYPE: harassment  
SEVERITY: 5  
TEXT: "You guys are complete idiots!"  
CONTEXT: The customer is insulting the service representatives by calling them "complete idiots."

TYPE: profanity  
SEVERITY: 6  
TEXT: "Damn right! This is bullshit!"  
CONTEXT: The customer uses mild profanity to express frustration with the service."""

print("=== TESTING REGEX PATTERNS ===")
type_pattern = r'TYPE:\s*(\w+)'
severity_pattern = r'SEVERITY:\s*(\d+)'
text_pattern = r'TEXT:\s*["\'](.+?)["\']'
context_pattern = r'CONTEXT:\s*(.+?)(?=TYPE:|$)'

entries = re.split(r'(?=TYPE:)', response.strip())
print(f"\nNumber of entries after split: {len(entries)}")

for i, entry in enumerate(entries):
    print(f"\n--- Entry {i} ---")
    print(f"Entry content: {repr(entry[:100])}")
    
    type_match = re.search(type_pattern, entry, re.IGNORECASE)
    severity_match = re.search(severity_pattern, entry)
    text_match = re.search(text_pattern, entry, re.DOTALL)
    context_match = re.search(context_pattern, entry, re.DOTALL)
    
    print(f"TYPE match: {type_match.group(1) if type_match else 'NONE'}")
    print(f"SEVERITY match: {severity_match.group(1) if severity_match else 'NONE'}")
    print(f"TEXT match: {text_match.group(1) if text_match else 'NONE'}")
    print(f"CONTEXT match: {context_match.group(1)[:50] if context_match else 'NONE'}")
