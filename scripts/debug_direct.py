from dotenv import load_dotenv
load_dotenv()

import re
from models.schemas import AbuseFlag, AbuseType, AbuseSeverity

response_text = """TYPE: harassment  
SEVERITY: 5  
TEXT: "You guys are complete idiots!"  
CONTEXT: The customer is insulting the service representatives by calling them "complete idiots."

TYPE: profanity  
SEVERITY: 6  
TEXT: "Damn right! This is bullshit!"  
CONTEXT: The customer uses mild profanity to express frustration with the service."""

print("Testing direct parsing...")

abuse_flags = []

type_pattern = r'TYPE:\s*(\w+)'
severity_pattern = r'SEVERITY:\s*(\d+)'
text_pattern = r'TEXT:\s*["\'](.+?)["\']'
context_pattern = r'CONTEXT:\s*(.+?)(?=TYPE:|$)'

entries = re.split(r'(?=TYPE:)', response_text.strip())
print(f"Entries: {len(entries)}")

for i, entry in enumerate(entries):
    print(f"\n--- Processing entry {i} ---")
    if not entry.strip() or 'TYPE:' not in entry:
        print("Skipping (empty or no TYPE)")
        continue
    
    try:
        type_match = re.search(type_pattern, entry, re.IGNORECASE)
        severity_match = re.search(severity_pattern, entry)
        text_match = re.search(text_pattern, entry, re.DOTALL)
        context_match = re.search(context_pattern, entry, re.DOTALL)
        
        if not type_match:
            print("No type match!")
            continue
        
        abuse_type_str = type_match.group(1).lower().strip()
        severity_num = int(severity_match.group(1)) if severity_match else 5
        quoted_text = text_match.group(1).strip() if text_match else ""
        context = context_match.group(1).strip() if context_match else ""
        
        print(f"Parsed: type={abuse_type_str}, severity={severity_num}")
        
        abuse_type_map = {
            'profanity': AbuseType.PROFANITY,
            'threat': AbuseType.THREAT,
            'harassment': AbuseType.HARASSMENT,
            'sexual': AbuseType.DISCRIMINATION,
            'hate_speech': AbuseType.DISCRIMINATION,
            'discrimination': AbuseType.DISCRIMINATION
        }
        
        abuse_type = abuse_type_map.get(abuse_type_str, AbuseType.PROFANITY)
        
        if severity_num <= 3:
            severity = AbuseSeverity.LOW
        elif severity_num <= 6:
            severity = AbuseSeverity.MEDIUM
        else:
            severity = AbuseSeverity.HIGH
        
        print(f"Creating AbuseFlag...")
        abuse_flag = AbuseFlag(
            abuse_type=abuse_type,
            severity=severity,
            quoted_text=quoted_text,
            context=context
        )
        
        abuse_flags.append(abuse_flag)
        print(f"SUCCESS - Added flag")
        
    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

print(f"\n\nFinal result: {len(abuse_flags)} flags")
for flag in abuse_flags:
    print(f"  - {flag.abuse_type.value} ({flag.severity.value})")
