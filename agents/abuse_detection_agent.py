from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import AbuseFlag, AbuseType, AbuseSeverity, AgentState
from typing import List
import os
import re

class AbuseDetectionAgent:
    """Agent that detects abusive language, threats, or inappropriate content"""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model_name = model
        self.llm = ChatOpenAI(
            model=model,
            temperature=0,  # Use low temperature for consistent detection
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a content moderation system for call center transcripts. Your job is to FLAG inappropriate content, not to make judgments about whether to allow it.

DETECTION CRITERIA:

1. **profanity**: Flag ANY swear words or vulgar language
   Examples: bullshit, damn, crap, hell, ass, bastard, bitch, fuck, shit
   
2. **threat**: Flag ANY threats, including:
   - Legal threats (lawsuit, sue, report to authorities)
   - Physical threats (come to your office, make you regret)
   - Implied harm (you better watch out)
   
3. **harassment**: Flag personal attacks or insults
   Examples: you're an idiot, you're incompetent, name-calling, belittling
   
4. **sexual**: Flag sexual content or inappropriate advances
   
5. **hate_speech**: Flag discriminatory language based on race, nationality, religion, gender, etc.

SEVERITY LEVELS:
- **Low (1-3)**: Mild profanity (damn, crap, hell), frustrated language
- **Medium (4-6)**: Direct insults, moderate profanity (bullshit, ass), legal threats
- **High (7-10)**: Severe profanity (fuck, shit), physical threats, hate speech

IMPORTANT: You are flagging content for REVIEW, not making final decisions. When in doubt, FLAG IT.
Normal frustration ("I'm very upset", "This is unacceptable") is NOT abuse unless it includes profanity, threats, or personal attacks.

OUTPUT FORMAT for each abuse found:
TYPE: [profanity|threat|harassment|sexual|hate_speech]
SEVERITY: [number 1-10]
TEXT: "[exact quote from transcript]"
CONTEXT: [brief explanation]

If absolutely NO abuse is detected, respond with: "NO_ABUSE_DETECTED"
"""),
            ("human", """Analyze this call transcript for abusive content:

{transcript}

List any abuse detected:""")
        ])

        self.chain = self.prompt | self.llm

    def _parse_abuse_response(self, response_text: str) -> List[AbuseFlag]:
        """Parse LLM response into AbuseFlag objects"""
        
        if "NO_ABUSE_DETECTED" in response_text:
            return []
        
        abuse_flags = []
        
        # Find all abuse entries by matching TYPE: pattern
        type_pattern = r'TYPE:\s*(\w+)'
        severity_pattern = r'SEVERITY:\s*(\d+)'
        text_pattern = r'TEXT:\s*["\'](.+?)["\']'
        context_pattern = r'CONTEXT:\s*(.+?)(?=TYPE:|$)'
        
        # Split response into potential abuse entries
        entries = re.split(r'(?=TYPE:)', response_text.strip())
        
        for entry in entries:
            if not entry.strip() or 'TYPE:' not in entry:
                continue
                
            try:
                # Extract fields using regex
                type_match = re.search(type_pattern, entry, re.IGNORECASE)
                severity_match = re.search(severity_pattern, entry)
                text_match = re.search(text_pattern, entry, re.DOTALL)
                context_match = re.search(context_pattern, entry, re.DOTALL)
                
                if not type_match:
                    continue
                
                abuse_type_str = type_match.group(1).lower().strip()
                severity_num = int(severity_match.group(1)) if severity_match else 5
                quoted_text = text_match.group(1).strip() if text_match else ""
                context = context_match.group(1).strip() if context_match else ""
                
                # Map to enum
                abuse_type_map = {
                    'profanity': AbuseType.PROFANITY,
                    'threat': AbuseType.THREAT,
                    'harassment': AbuseType.HARASSMENT,
                    'sexual': AbuseType.DISCRIMINATION,
                    'hate_speech': AbuseType.DISCRIMINATION,
                    'discrimination': AbuseType.DISCRIMINATION
                }
                
                abuse_type = abuse_type_map.get(abuse_type_str, AbuseType.PROFANITY)
                
                # Map severity
                if severity_num <= 3:
                    severity = AbuseSeverity.LOW
                elif severity_num <= 6:
                    severity = AbuseSeverity.MEDIUM
                else:
                    severity = AbuseSeverity.HIGH
                
                abuse_flag = AbuseFlag(
                    detected=True,
                    speaker="customer",  # Assume customer for now
                    abuse_type=[abuse_type],  # Must be a list
                    severity=severity,
                    evidence=[quoted_text] if quoted_text else [],
                    recommended_action=context
                )
                
                abuse_flags.append(abuse_flag)
                
            except Exception as e:
                # If parsing fails, skip this entry
                continue
        
        return abuse_flags

    def run(self, state: AgentState) -> AgentState:
        """Detect abusive content in the transcript"""
        
        if not state.transcript:
            state.execution_path.append("abuse_detection")
            state.models_used.append(self.model_name)
            return state

        # Get LLM response
        response = self.chain.invoke({
            "transcript": state.transcript.full_text
        })
        
        # Parse response into abuse flags
        abuse_flags = self._parse_abuse_response(response.content)
        
        # Update state
        state.abuse_flags = abuse_flags
        state.execution_path.append("abuse_detection")
        state.models_used.append(self.model_name)
        
        return state

    async def arun(self, state: AgentState) -> AgentState:
        """Async version"""
        if not state.transcript:
            state.execution_path.append("abuse_detection")
            state.models_used.append(self.model_name)
            return state

        response = await self.chain.ainvoke({
            "transcript": state.transcript.full_text
        })
        
        abuse_flags = self._parse_abuse_response(response.content)
        
        state.abuse_flags = abuse_flags
        state.execution_path.append("abuse_detection")
        state.models_used.append(self.model_name)
        
        return state
