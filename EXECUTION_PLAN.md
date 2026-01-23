# AI Call Center Assistant - Detailed Execution Plan

> **Approach**: Deploy First, Build Incrementally
> **Deployment Target**: Hugging Face Spaces (Docker)
> **Last Updated**: 2026-01-22

---

## Philosophy

```
❌ OLD WAY: Build everything locally → Deploy at end → Hundreds of issues

✅ NEW WAY: Deploy skeleton first → Verify it works → Add features incrementally
```

**Every phase ends with a working deployment on HF Spaces.**

---

## Pre-Requisites Checklist

Before starting, ensure you have:

- [ ] Hugging Face account (https://huggingface.co)
- [ ] OpenAI API key
- [ ] Anthropic API key
- [ ] LangSmith account and API key
- [ ] Git installed locally
- [ ] Docker installed locally (for testing)
- [ ] Python 3.11+ installed

---

## Phase Overview

| Phase | Goal | Key Deliverable |
|-------|------|-----------------|
| **Phase 0** | First deployment | Empty app running on HF Spaces |
| **Phase 1** | Dependencies verified | All imports working on HF Spaces |
| **Phase 2** | Single agent | Summarization working end-to-end |
| **Phase 3** | Linear pipeline | 4 agents in sequence |
| **Phase 4** | True multi-agent | Supervisor + Critic with loops |
| **Phase 5** | Guardrails | Input validation + abuse detection |
| **Phase 6** | Animation | n8n-style workflow visualization |
| **Phase 7** | Polish | Evaluation, docs, demo |

---

# Phase 0: First Deployment to HF Spaces

## Goal
Get a "Hello World" Streamlit app deployed to Hugging Face Spaces.

## Step 0.1: Create Project Directory

```bash
cd /Users/pushkar/IK_Agentic_AI/call_center_assistant

# Create initial structure
mkdir -p data/sample_transcripts
```

## Step 0.2: Create Minimal Streamlit App

**File: `app.py`**
```python
import streamlit as st

st.set_page_config(
    page_title="Call Center Assistant",
    page_icon="📞",
    layout="wide"
)

st.title("📞 AI Call Center Assistant")
st.markdown("**Phase 0**: Deployment Verification")

st.divider()

# Simple health check display
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Status", "Online", delta="Healthy")

with col2:
    st.metric("Phase", "0", delta="Initial")

with col3:
    st.metric("Platform", "HF Spaces")

st.divider()

st.success("✅ App successfully deployed to Hugging Face Spaces!")

st.info("""
**Next Steps (Phase 1):**
- Install all dependencies
- Verify LangChain, LangGraph, Whisper imports
- Create UI skeleton
""")

# Footer
st.divider()
st.caption("AI Call Center Assistant | Capstone Project | Phase 0")
```

## Step 0.3: Create Minimal Requirements

**File: `requirements.txt`**
```
streamlit==1.31.0
```

## Step 0.4: Create Dockerfile for HF Spaces

**File: `Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# HF Spaces expects port 7860
EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
```

## Step 0.5: Create README for HF Spaces

**File: `README.md`**
```markdown
---
title: AI Call Center Assistant
emoji: 📞
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# AI Call Center Assistant

A multi-agent system for analyzing call center recordings and transcripts.

## Features (Coming Soon)
- Audio transcription (Whisper)
- Call summarization (GPT-4)
- Quality scoring (Multi-LLM)
- Abuse detection
- Workflow visualization

## Current Phase: 0 - Deployment Verification
```

## Step 0.6: Create .gitignore

**File: `.gitignore`**
```
# Python
__pycache__/
*.py[cod]
*$py.class
.Python
venv/
.env

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Project specific
data/uploads/
*.wav
*.mp3
*.m4a
```

## Step 0.7: Test Locally

```bash
# Test locally first
cd /Users/pushkar/IK_Agentic_AI/call_center_assistant
streamlit run app.py --server.port=7860

# Or test with Docker
docker build -t call-center-assistant .
docker run -p 7860:7860 call-center-assistant
```

Open http://localhost:7860 and verify the app loads.

## Step 0.8: Create HF Space and Deploy

### Option A: Via HF Website
1. Go to https://huggingface.co/new-space
2. Enter Space name: `call-center-assistant`
3. Select **Docker** as SDK
4. Choose visibility (public or private)
5. Click "Create Space"

### Option B: Via Git
```bash
# Clone empty space (replace YOUR_USERNAME)
git clone https://huggingface.co/spaces/YOUR_USERNAME/call-center-assistant
cd call-center-assistant

# Copy your files
cp /Users/pushkar/IK_Agentic_AI/call_center_assistant/* .

# Push to HF
git add .
git commit -m "Phase 0: Initial deployment"
git push
```

## Step 0.9: Verify Deployment

1. Go to your Space URL: `https://huggingface.co/spaces/YOUR_USERNAME/call-center-assistant`
2. Wait for build to complete (check "Logs" tab if issues)
3. Verify you see "✅ App successfully deployed to Hugging Face Spaces!"

## Phase 0 Exit Criteria

- [ ] App shows Phase 0 UI on HF Spaces
- [ ] Build completes without errors
- [ ] Page loads in under 30 seconds
- [ ] Local Docker build works

---

# Phase 1: All Dependencies + UI Skeleton

## Goal
Install ALL project dependencies upfront and verify they work on HF Spaces.

## Step 1.1: Update Requirements with All Dependencies

**File: `requirements.txt`**
```
# ===================
# Core Framework
# ===================
streamlit==1.31.0
python-dotenv==1.0.0
pydantic==2.6.0

# ===================
# LangChain Ecosystem
# ===================
langchain==0.1.20
langchain-openai==0.1.6
langchain-anthropic==0.1.11
langchain-community==0.0.38
langgraph==0.0.55

# ===================
# LLM Routing
# ===================
litellm==1.34.0

# ===================
# Audio Processing
# ===================
openai==1.12.0
pydub==0.25.1

# ===================
# Visualization
# ===================
streamlit-flow-component==0.1.0

# ===================
# Utilities
# ===================
httpx==0.27.0
tenacity==8.2.3
redis==5.0.1
```

**Note**: We're using OpenAI's Whisper API instead of local whisper to avoid heavy dependencies on HF Spaces.

## Step 1.2: Update Dockerfile with System Dependencies

**File: `Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# HF Spaces expects port 7860
EXPOSE 7860

# Health check
HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
```

## Step 1.3: Create Project Structure

```bash
cd /Users/pushkar/IK_Agentic_AI/call_center_assistant

# Create directory structure
mkdir -p agents
mkdir -p graph
mkdir -p models
mkdir -p guardrails
mkdir -p config
mkdir -p ui/components
mkdir -p evaluation/datasets
mkdir -p evaluation/evaluators
mkdir -p data/sample_transcripts
mkdir -p tests

# Create __init__.py files
touch agents/__init__.py
touch graph/__init__.py
touch models/__init__.py
touch guardrails/__init__.py
touch config/__init__.py
touch ui/__init__.py
touch ui/components/__init__.py
touch evaluation/__init__.py
touch evaluation/evaluators/__init__.py
touch tests/__init__.py
```

## Step 1.4: Create Configuration Module

**File: `config/settings.py`**
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""

    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # LangSmith
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "call-center-assistant")

    # App Settings
    MAX_AUDIO_DURATION_SECONDS: int = 3600  # 1 hour
    MIN_AUDIO_DURATION_SECONDS: int = 10
    MAX_REVISION_COUNT: int = 3

    @classmethod
    def validate(cls) -> dict:
        """Check which settings are configured"""
        return {
            "openai": bool(cls.OPENAI_API_KEY),
            "anthropic": bool(cls.ANTHROPIC_API_KEY),
            "langsmith": bool(cls.LANGCHAIN_API_KEY),
        }

settings = Settings()
```

## Step 1.5: Create Pydantic Schemas (Stub)

**File: `models/schemas.py`**
```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List
from datetime import datetime

# ===================
# Enums
# ===================

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class ResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    ESCALATED = "escalated"

class AbuseType(str, Enum):
    PROFANITY = "profanity"
    THREAT = "threat"
    HARASSMENT = "harassment"
    DISCRIMINATION = "discrimination"
    NONE = "none"

class AbuseSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    NONE = "none"

# ===================
# Data Models
# ===================

class CallMetadata(BaseModel):
    """Metadata extracted by Intake Agent"""
    call_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    duration_seconds: Optional[float] = None
    input_type: str  # "audio" | "transcript"
    file_name: Optional[str] = None

class TranscriptSegment(BaseModel):
    """Single segment of a transcript"""
    speaker: str
    text: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class TranscriptData(BaseModel):
    """Full transcript data"""
    segments: List[TranscriptSegment] = []
    full_text: str
    language: str = "en"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class CallSummary(BaseModel):
    """Summary generated by Summarization Agent"""
    brief_summary: str = Field(description="2-3 sentence overview")
    key_points: List[str] = Field(description="3-5 bullet points")
    action_items: List[str] = Field(default=[], description="Follow-up tasks")
    customer_intent: str = Field(description="What the customer wanted")
    resolution_status: ResolutionStatus
    topics: List[str] = Field(description="Main topics discussed")
    sentiment: Sentiment

class QAScores(BaseModel):
    """Quality scores from QA Scoring Agent"""
    empathy: float = Field(ge=0, le=10)
    professionalism: float = Field(ge=0, le=10)
    resolution: float = Field(ge=0, le=10)
    tone: float = Field(ge=0, le=10)
    comments: str = ""

    @property
    def overall(self) -> float:
        return round((self.empathy + self.professionalism + self.resolution + self.tone) / 4, 1)

class SummaryCritique(BaseModel):
    """Critique from Summary Critic Agent"""
    faithfulness_score: int = Field(ge=1, le=10)
    completeness_score: int = Field(ge=1, le=10)
    conciseness_score: int = Field(ge=1, le=10)
    needs_revision: bool
    revision_instructions: Optional[str] = None
    feedback: str

class AbuseFlag(BaseModel):
    """Abuse detection result"""
    detected: bool = False
    speaker: Optional[str] = None  # "customer" | "agent" | "both"
    abuse_type: List[AbuseType] = [AbuseType.NONE]
    severity: AbuseSeverity = AbuseSeverity.NONE
    evidence: List[str] = []
    recommended_action: str = ""
    requires_escalation: bool = False

class InputValidationResult(BaseModel):
    """Result from input validation guardrail"""
    is_valid: bool
    confidence: float = Field(ge=0.0, le=1.0)
    input_type_detected: str
    issues: List[str] = []
    requires_user_confirmation: bool = False
    rejection_reason: Optional[str] = None

# ===================
# Agent State
# ===================

class AgentState(BaseModel):
    """State passed between agents in LangGraph"""

    # Input
    input_file_path: Optional[str] = None
    input_type: str = "transcript"  # "audio" | "transcript"
    raw_input: Optional[str] = None

    # Validation
    validation_result: Optional[InputValidationResult] = None
    user_confirmed: bool = False

    # Processing outputs
    metadata: Optional[CallMetadata] = None
    transcript: Optional[TranscriptData] = None
    summary: Optional[CallSummary] = None
    summary_critique: Optional[SummaryCritique] = None
    qa_scores: Optional[QAScores] = None
    abuse_flags: List[AbuseFlag] = []

    # Control flow
    current_agent: str = "supervisor"
    needs_revision: bool = False
    revision_count: int = 0
    execution_path: List[str] = []
    models_used: List[str] = []
    errors: List[str] = []

    class Config:
        arbitrary_types_allowed = True
```

## Step 1.6: Update App with Dependency Verification + UI Skeleton

**File: `app.py`**
```python
import streamlit as st

st.set_page_config(
    page_title="Call Center Assistant",
    page_icon="📞",
    layout="wide"
)

st.title("📞 AI Call Center Assistant")
st.markdown("**Phase 1**: Dependency Verification + UI Skeleton")

# ===================
# Dependency Check
# ===================
st.header("1. Dependency Verification")

with st.status("Checking dependencies...", expanded=True) as status:
    all_ok = True

    # Test core imports
    try:
        st.write("Checking Streamlit...")
        import streamlit
        st.write(f"  ✅ streamlit {streamlit.__version__}")
    except Exception as e:
        st.write(f"  ❌ streamlit: {e}")
        all_ok = False

    try:
        st.write("Checking Pydantic...")
        import pydantic
        st.write(f"  ✅ pydantic {pydantic.__version__}")
    except Exception as e:
        st.write(f"  ❌ pydantic: {e}")
        all_ok = False

    try:
        st.write("Checking LangChain...")
        import langchain
        st.write(f"  ✅ langchain {langchain.__version__}")
    except Exception as e:
        st.write(f"  ❌ langchain: {e}")
        all_ok = False

    try:
        st.write("Checking LangChain-OpenAI...")
        from langchain_openai import ChatOpenAI
        st.write("  ✅ langchain-openai")
    except Exception as e:
        st.write(f"  ❌ langchain-openai: {e}")
        all_ok = False

    try:
        st.write("Checking LangChain-Anthropic...")
        from langchain_anthropic import ChatAnthropic
        st.write("  ✅ langchain-anthropic")
    except Exception as e:
        st.write(f"  ❌ langchain-anthropic: {e}")
        all_ok = False

    try:
        st.write("Checking LangGraph...")
        from langgraph.graph import StateGraph
        st.write("  ✅ langgraph")
    except Exception as e:
        st.write(f"  ❌ langgraph: {e}")
        all_ok = False

    try:
        st.write("Checking LiteLLM...")
        import litellm
        st.write(f"  ✅ litellm {litellm.__version__}")
    except Exception as e:
        st.write(f"  ❌ litellm: {e}")
        all_ok = False

    try:
        st.write("Checking OpenAI...")
        import openai
        st.write(f"  ✅ openai {openai.__version__}")
    except Exception as e:
        st.write(f"  ❌ openai: {e}")
        all_ok = False

    try:
        st.write("Checking streamlit-flow...")
        from streamlit_flow import streamlit_flow
        st.write("  ✅ streamlit-flow")
    except Exception as e:
        st.write(f"  ❌ streamlit-flow: {e}")
        all_ok = False

    try:
        st.write("Checking project modules...")
        from config.settings import settings
        from models.schemas import CallSummary, QAScores, AgentState
        st.write("  ✅ project modules")
    except Exception as e:
        st.write(f"  ❌ project modules: {e}")
        all_ok = False

    if all_ok:
        status.update(label="All dependencies verified!", state="complete")
    else:
        status.update(label="Some dependencies failed!", state="error")

# ===================
# Configuration Check
# ===================
st.header("2. Configuration Status")

try:
    from config.settings import settings
    config_status = settings.validate()

    col1, col2, col3 = st.columns(3)
    with col1:
        if config_status["openai"]:
            st.success("✅ OpenAI API Key")
        else:
            st.warning("⚠️ OpenAI API Key not set")

    with col2:
        if config_status["anthropic"]:
            st.success("✅ Anthropic API Key")
        else:
            st.warning("⚠️ Anthropic API Key not set")

    with col3:
        if config_status["langsmith"]:
            st.success("✅ LangSmith API Key")
        else:
            st.warning("⚠️ LangSmith API Key not set")
except Exception as e:
    st.error(f"Configuration error: {e}")

# ===================
# UI Skeleton
# ===================
st.header("3. UI Skeleton")

st.divider()

# Two-column layout
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("📤 Upload")
    uploaded_file = st.file_uploader(
        "Upload audio or transcript",
        type=["wav", "mp3", "m4a", "txt", "json"],
        help="Supported formats: WAV, MP3, M4A (audio) or TXT, JSON (transcript)"
    )

    if uploaded_file:
        st.info(f"File: {uploaded_file.name} ({uploaded_file.size} bytes)")

    process_btn = st.button("🚀 Process Call", type="primary", disabled=not uploaded_file)

    if process_btn:
        st.info("Processing will be implemented in Phase 2")

with col_right:
    st.subheader("🔄 Workflow")
    st.info("Workflow animation will be implemented in Phase 6")

    # Placeholder for workflow visualization
    st.markdown("""
    ```
    ┌────────────┐     ┌──────────────┐     ┌─────────────┐
    │  Intake    │────▶│ Transcribe   │────▶│  Summarize  │
    │  Agent     │     │    Agent     │     │    Agent    │
    └────────────┘     └──────────────┘     └─────────────┘
                                                   │
                                                   ▼
                                           ┌─────────────┐
                                           │  QA Score   │
                                           │    Agent    │
                                           └─────────────┘
    ```
    """)

st.divider()

# Results tabs
st.subheader("📊 Results")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Transcript",
    "Summary",
    "QA Scores",
    "Abuse Flags",
    "Debug"
])

with tab1:
    st.markdown("*Transcript will appear here after processing...*")

with tab2:
    st.markdown("*Summary will appear here after processing...*")

    # Preview of what summary will look like
    with st.expander("Preview: Summary Format"):
        st.markdown("""
        **Brief Summary**
        > Customer called about billing issue. Agent resolved by applying credit.

        **Key Points**
        - Customer charged $150 instead of $99
        - Setup fee was not communicated
        - Agent credited $50 back

        **Action Items**
        - None

        **Sentiment**: Positive | **Resolution**: Resolved
        """)

with tab3:
    st.markdown("*QA Scores will appear here after processing...*")

    # Preview of what scores will look like
    with st.expander("Preview: QA Scores Format"):
        cols = st.columns(4)
        cols[0].metric("Empathy", "8.5", delta="Good")
        cols[1].metric("Professionalism", "9.0", delta="Excellent")
        cols[2].metric("Resolution", "8.0", delta="Good")
        cols[3].metric("Tone", "8.5", delta="Good")

with tab4:
    st.markdown("*Abuse flags will appear here if detected...*")

with tab5:
    st.markdown("*Debug info will appear here after processing...*")

    with st.expander("Preview: Debug Info"):
        st.json({
            "execution_path": ["supervisor", "intake", "transcription", "summarization", "qa_scoring"],
            "models_used": ["gpt-4o-mini", "whisper-1", "gpt-4", "gpt-4"],
            "revision_count": 0,
            "total_time_ms": 3500,
            "langsmith_trace_url": "https://smith.langchain.com/..."
        })

# ===================
# Footer
# ===================
st.divider()
st.caption("AI Call Center Assistant | Capstone Project | Phase 1")
```

## Step 1.7: Create .env.example

**File: `.env.example`**
```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=call-center-assistant
```

## Step 1.8: Test Locally

```bash
cd /Users/pushkar/IK_Agentic_AI/call_center_assistant

# Create .env file from example
cp .env.example .env
# Edit .env with your actual keys

# Test with streamlit
streamlit run app.py --server.port=7860

# Test with Docker
docker build -t call-center-assistant .
docker run -p 7860:7860 --env-file .env call-center-assistant
```

## Step 1.9: Add Secrets to HF Space

1. Go to your Space: `https://huggingface.co/spaces/YOUR_USERNAME/call-center-assistant`
2. Click Settings → Repository secrets
3. Add each secret:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `LANGCHAIN_API_KEY`
   - `LANGCHAIN_TRACING_V2` = `true`
   - `LANGCHAIN_PROJECT` = `call-center-assistant`

## Step 1.10: Deploy to HF Spaces

```bash
git add .
git commit -m "Phase 1: All dependencies + UI skeleton"
git push
```

## Step 1.11: Verify Deployment

1. Wait for build to complete (may take 5-10 minutes due to dependencies)
2. Check all dependency verifications show ✅
3. Check configuration status shows API keys detected
4. Verify UI skeleton renders correctly
5. Test file uploader (file should show, processing won't work yet)

## Phase 1 Exit Criteria

- [ ] All dependency checks show ✅
- [ ] Configuration shows all API keys detected
- [ ] UI skeleton renders correctly
- [ ] File uploader works
- [ ] Build completes without errors
- [ ] Build time noted: ______ minutes
- [ ] App memory usage acceptable

---

# Phase 2: Single Agent (Summarization)

## Goal
Get ONE agent working end-to-end with real LLM calls.

## Step 2.1: Create Summarization Agent

**File: `agents/summarization_agent.py`**
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import CallSummary
import os

class SummarizationAgent:
    """Agent that generates structured summaries from call transcripts"""

    def __init__(self, model: str = "gpt-4"):
        self.model_name = model
        self.llm = ChatOpenAI(
            model=model,
            api_key=os.getenv("OPENAI_API_KEY")
        ).with_structured_output(CallSummary)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert call center analyst. Analyze the following call transcript and provide a structured summary.

Your task:
1. Write a brief 2-3 sentence summary of the call
2. Extract 3-5 key points discussed
3. List any action items or follow-ups needed
4. Identify what the customer wanted (their intent)
5. Determine if the issue was resolved, unresolved, or escalated
6. List the main topics discussed
7. Assess the overall sentiment (positive, neutral, or negative)

Be concise but thorough. Focus on facts from the transcript."""),
            ("human", """Please analyze this call transcript:

{transcript}""")
        ])

        self.chain = self.prompt | self.llm

    def run(self, transcript: str) -> CallSummary:
        """Generate a summary from the transcript"""
        return self.chain.invoke({"transcript": transcript})

    async def arun(self, transcript: str) -> CallSummary:
        """Async version"""
        return await self.chain.ainvoke({"transcript": transcript})
```

## Step 2.2: Create Sample Test Data

**File: `data/sample_transcripts/billing_inquiry.txt`**
```
Agent: Thank you for calling TechSupport, my name is Sarah. How can I help you today?

Customer: Hi Sarah, I'm calling about my bill. I was charged $150 but my plan is supposed to be $99 per month.

Agent: I understand your concern about the billing discrepancy. Let me pull up your account. Can I have your account number please?

Customer: Sure, it's 12345678.

Agent: Thank you. I can see your account now. It looks like there was a one-time setup fee of $50 added to your first bill, plus your regular $99 plan charge. That's why the total is $150.

Customer: Oh, I wasn't told about any setup fee when I signed up online. The website didn't mention it.

Agent: I apologize for the confusion. That's definitely not the experience we want you to have. Let me check if we can waive that fee for you... Yes, I've gone ahead and credited the $50 setup fee back to your account. You'll see this credit on your next statement.

Customer: That's great, thank you so much Sarah! I really appreciate you taking care of this.

Agent: You're welcome! I'm glad I could help. Is there anything else I can assist you with today?

Customer: No, that's all I needed. Thanks again!

Agent: Thank you for calling TechSupport. Have a wonderful day!

Customer: You too, bye!

Agent: Goodbye!
```

**File: `data/sample_transcripts/tech_support_unresolved.txt`**
```
Agent: Thank you for calling TechSupport, this is Mike. How can I assist you?

Customer: Hi Mike, my internet has been cutting out constantly for the past three days. It's really frustrating because I work from home.

Agent: I'm sorry to hear that. Let me look into this for you. Can I get your account number?

Customer: It's 87654321.

Agent: Thank you. I can see your account. Let me check the network status in your area... It looks like there have been some intermittent outages reported in your neighborhood.

Customer: That's what I figured. When is it going to be fixed?

Agent: Our technicians are currently working on the issue. Unfortunately, I don't have an exact timeline for when it will be resolved.

Customer: That's not acceptable. I've been paying for service I'm not receiving. I need this fixed today.

Agent: I completely understand your frustration. What I can do is escalate this to our priority support team and schedule a technician visit for tomorrow morning. Would that work for you?

Customer: Tomorrow? I need it fixed now. I have important meetings today.

Agent: I apologize, but the earliest available appointment is tomorrow between 8 AM and 12 PM. I can also apply a credit to your account for the days of service interruption.

Customer: Fine, schedule the appointment. But I expect a full credit for this month.

Agent: I've scheduled the appointment and added a note about the service credit request. A supervisor will review it and follow up with you.

Customer: Alright. Is there anything else I should do?

Agent: For now, try restarting your modem. Sometimes that can help with intermittent issues. If the technician visit doesn't resolve it, please call us back.

Customer: Okay, thanks.

Agent: Thank you for your patience. Is there anything else I can help with?

Customer: No, that's it.

Agent: Thank you for calling TechSupport. We'll get this resolved for you. Have a good day.
```

**File: `data/sample_transcripts/complaint_with_frustration.txt`**
```
Agent: Thank you for calling, this is Jennifer. How may I help you?

Customer: Yeah, I need to speak to a manager right now. I've called three times about the same issue and nothing has been done!

Agent: I'm sorry to hear you've had to call multiple times. I'd be happy to help you today. Can you tell me what the issue is?

Customer: My package was supposed to arrive two weeks ago. I keep getting told it's "on the way" but nothing ever shows up. This is ridiculous!

Agent: I completely understand your frustration. That's not acceptable service. Let me look into this immediately. Can I have your order number?

Customer: It's ORD-98765. And before you tell me it's "in transit" again, I've already checked the tracking. It's been stuck at the same location for 10 days!

Agent: You're absolutely right. I can see the package has been stuck at our distribution center. I'm so sorry for this. It appears there was a labeling error that caused it to be misdirected.

Customer: A labeling error? How does that even happen? This is completely unprofessional.

Agent: You're right to be upset. This shouldn't have happened, and I apologize. Here's what I'm going to do: I'm issuing a full refund to your original payment method right now, and I'm also sending you a replacement package with expedited shipping at no charge. You should receive it within 2-3 business days.

Customer: Okay... that's actually more than I expected. Thank you.

Agent: It's the least we can do. I've also flagged your account for priority handling on any future orders. Is there anything else I can help you with today?

Customer: No, that covers it. I appreciate you actually doing something about this.

Agent: Of course. Again, I apologize for the inconvenience. You'll receive an email confirmation of the refund and the new shipment tracking within the hour.

Customer: Alright, thank you Jennifer.

Agent: Thank you for your patience. Have a great day!
```

## Step 2.3: Update App with Working Summarization

**File: `app.py`** (replace existing)
```python
import streamlit as st
import os
from pathlib import Path

st.set_page_config(
    page_title="Call Center Assistant",
    page_icon="📞",
    layout="wide"
)

# ===================
# Initialize
# ===================
st.title("📞 AI Call Center Assistant")
st.markdown("**Phase 2**: Single Agent (Summarization)")

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ OPENAI_API_KEY not set. Please add it to your environment or HF Spaces secrets.")
    st.stop()

# Import after env check
from agents.summarization_agent import SummarizationAgent
from models.schemas import CallSummary

# Initialize agent (cached)
@st.cache_resource
def get_summarization_agent():
    return SummarizationAgent(model="gpt-4")

agent = get_summarization_agent()

# ===================
# Sidebar - Sample Data
# ===================
with st.sidebar:
    st.header("📁 Sample Transcripts")

    sample_dir = Path("data/sample_transcripts")
    if sample_dir.exists():
        sample_files = list(sample_dir.glob("*.txt"))
        if sample_files:
            selected_sample = st.selectbox(
                "Load a sample transcript:",
                options=["None"] + [f.name for f in sample_files]
            )
        else:
            selected_sample = "None"
            st.info("No sample files found")
    else:
        selected_sample = "None"
        st.info("Sample directory not found")

    st.divider()
    st.markdown("**Agent Info**")
    st.caption(f"Model: {agent.model_name}")

# ===================
# Main Content
# ===================
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📤 Input")

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload transcript (.txt)",
        type=["txt"],
        help="Upload a text file containing a call transcript"
    )

    # Text area for transcript
    if uploaded_file:
        transcript_text = uploaded_file.read().decode("utf-8")
    elif selected_sample != "None":
        sample_path = Path("data/sample_transcripts") / selected_sample
        transcript_text = sample_path.read_text()
    else:
        transcript_text = ""

    transcript_input = st.text_area(
        "Transcript",
        value=transcript_text,
        height=400,
        placeholder="Paste or upload a call transcript..."
    )

    # Process button
    process_btn = st.button(
        "🚀 Generate Summary",
        type="primary",
        disabled=not transcript_input.strip()
    )

with col_right:
    st.subheader("📊 Results")

    if process_btn and transcript_input.strip():
        with st.spinner("Analyzing transcript with GPT-4..."):
            try:
                summary = agent.run(transcript_input)
                st.session_state["last_summary"] = summary
                st.session_state["last_transcript"] = transcript_input
            except Exception as e:
                st.error(f"Error generating summary: {e}")
                st.stop()

    # Display results if available
    if "last_summary" in st.session_state:
        summary: CallSummary = st.session_state["last_summary"]

        # Brief Summary
        st.markdown("**Brief Summary**")
        st.info(summary.brief_summary)

        # Key Points
        st.markdown("**Key Points**")
        for point in summary.key_points:
            st.markdown(f"• {point}")

        # Action Items
        if summary.action_items:
            st.markdown("**Action Items**")
            for item in summary.action_items:
                st.markdown(f"☐ {item}")

        # Customer Intent
        st.markdown("**Customer Intent**")
        st.write(summary.customer_intent)

        # Metadata
        st.divider()
        cols = st.columns(3)

        with cols[0]:
            sentiment_colors = {
                "positive": "🟢",
                "neutral": "🟡",
                "negative": "🔴"
            }
            st.metric(
                "Sentiment",
                f"{sentiment_colors.get(summary.sentiment.value, '⚪')} {summary.sentiment.value.title()}"
            )

        with cols[1]:
            resolution_colors = {
                "resolved": "✅",
                "unresolved": "⏳",
                "escalated": "⬆️"
            }
            st.metric(
                "Resolution",
                f"{resolution_colors.get(summary.resolution_status.value, '❓')} {summary.resolution_status.value.title()}"
            )

        with cols[2]:
            st.metric("Topics", len(summary.topics))

        # Topics
        with st.expander("Topics Discussed"):
            for topic in summary.topics:
                st.markdown(f"• {topic}")

        # Raw JSON
        with st.expander("Raw JSON Output"):
            st.json(summary.model_dump())

    else:
        st.info("Upload or select a transcript, then click 'Generate Summary' to see results.")

# ===================
# Footer
# ===================
st.divider()
st.caption("AI Call Center Assistant | Capstone Project | Phase 2 - Single Agent")
```

## Step 2.4: Test Locally

```bash
cd /Users/pushkar/IK_Agentic_AI/call_center_assistant

# Make sure .env has OPENAI_API_KEY
streamlit run app.py --server.port=7860
```

1. Select a sample transcript from the sidebar
2. Click "Generate Summary"
3. Verify summary is generated with all fields
4. Check LangSmith for the trace

## Step 2.5: Deploy and Test on HF Spaces

```bash
git add .
git commit -m "Phase 2: Summarization agent working"
git push
```

Verify:
1. Sample transcripts load
2. Summary generation works
3. All Pydantic fields are populated
4. LangSmith shows traces

## Phase 2 Exit Criteria

- [ ] Summarization agent generates structured output
- [ ] Sample transcripts work
- [ ] All Pydantic fields populated correctly
- [ ] LangSmith shows traces
- [ ] Works on HF Spaces (not just locally)

---

# Phase 3: Linear Multi-Agent Pipeline

## Goal
Chain 4 agents in sequence: Intake → Transcription → Summarization → QA Scoring

## Step 3.1: Create Intake Agent

**File: `agents/intake_agent.py`**
```python
from models.schemas import CallMetadata, AgentState
from datetime import datetime
import uuid
import os

class IntakeAgent:
    """Agent that validates input and extracts metadata"""

    def __init__(self):
        self.model_name = "rule-based"  # No LLM needed for basic intake

    def run(self, state: AgentState) -> AgentState:
        """Extract metadata from input"""

        # Generate call ID
        call_id = f"CALL-{uuid.uuid4().hex[:8].upper()}"

        # Determine input type
        input_type = state.input_type

        # Calculate approximate duration (rough estimate from text length)
        if state.raw_input:
            # Rough estimate: ~150 words per minute of conversation
            word_count = len(state.raw_input.split())
            estimated_duration = (word_count / 150) * 60  # seconds
        else:
            estimated_duration = None

        # Create metadata
        metadata = CallMetadata(
            call_id=call_id,
            timestamp=datetime.now(),
            duration_seconds=estimated_duration,
            input_type=input_type,
            file_name=state.input_file_path
        )

        # Update state
        state.metadata = metadata
        state.execution_path.append("intake")
        state.models_used.append(self.model_name)

        return state
```

## Step 3.2: Create Transcription Agent

**File: `agents/transcription_agent.py`**
```python
from models.schemas import TranscriptData, TranscriptSegment, AgentState
from openai import OpenAI
import os

class TranscriptionAgent:
    """Agent that handles transcription (pass-through for text, Whisper for audio)"""

    def __init__(self):
        self.model_name = "whisper-1"
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def run(self, state: AgentState) -> AgentState:
        """Transcribe audio or pass through text"""

        if state.input_type == "transcript":
            # Text input - create transcript structure from raw text
            transcript = TranscriptData(
                segments=[],  # No speaker diarization for plain text
                full_text=state.raw_input,
                language="en",
                confidence=1.0
            )
            state.models_used.append("pass-through")

        elif state.input_type == "audio":
            # Audio input - use Whisper API
            # Note: In real implementation, you'd read the audio file
            # For now, we'll handle this in a future phase
            transcript = TranscriptData(
                segments=[],
                full_text=state.raw_input or "",
                language="en",
                confidence=0.95
            )
            state.models_used.append(self.model_name)

        else:
            raise ValueError(f"Unknown input type: {state.input_type}")

        state.transcript = transcript
        state.execution_path.append("transcription")

        return state
```

## Step 3.3: Create QA Scoring Agent

**File: `agents/qa_scoring_agent.py`**
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import QAScores, AgentState
import os

class QAScoringAgent:
    """Agent that evaluates call quality using a rubric"""

    def __init__(self, model: str = "gpt-4"):
        self.model_name = model
        self.llm = ChatOpenAI(
            model=model,
            api_key=os.getenv("OPENAI_API_KEY")
        ).with_structured_output(QAScores)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a call center quality assurance specialist. Evaluate the following call transcript using these criteria:

**Empathy (0-10)**
- 9-10: Actively acknowledges feelings, uses empathetic language, shows genuine concern
- 7-8: Shows understanding, uses appropriate tone
- 5-6: Neutral, task-focused but not cold
- 3-4: Dismissive or rushed
- 0-2: Cold, robotic, or antagonistic

**Professionalism (0-10)**
- 9-10: Polite, clear communication, proper greeting/closing
- 7-8: Professional throughout, minor lapses
- 5-6: Adequate but room for improvement
- 3-4: Unprofessional language or behavior
- 0-2: Rude, inappropriate, or offensive

**Resolution (0-10)**
- 9-10: Issue fully resolved, customer satisfied
- 7-8: Issue mostly resolved, clear next steps
- 5-6: Partial resolution, some ambiguity
- 3-4: Issue unresolved, poor guidance
- 0-2: Made situation worse or no attempt to help

**Tone (0-10)**
- 9-10: Warm, engaging, builds rapport
- 7-8: Pleasant and appropriate
- 5-6: Neutral, neither positive nor negative
- 3-4: Terse, impatient, or condescending
- 0-2: Hostile or aggressive

Provide scores and brief comments explaining your evaluation."""),
            ("human", """Please evaluate this call transcript:

{transcript}""")
        ])

        self.chain = self.prompt | self.llm

    def run(self, state: AgentState) -> AgentState:
        """Generate QA scores for the transcript"""

        transcript_text = state.transcript.full_text if state.transcript else state.raw_input

        qa_scores = self.chain.invoke({"transcript": transcript_text})

        state.qa_scores = qa_scores
        state.execution_path.append("qa_scoring")
        state.models_used.append(self.model_name)

        return state
```

## Step 3.4: Update Summarization Agent for State

**File: `agents/summarization_agent.py`** (update)
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import CallSummary, AgentState
import os

class SummarizationAgent:
    """Agent that generates structured summaries from call transcripts"""

    def __init__(self, model: str = "gpt-4"):
        self.model_name = model
        self.llm = ChatOpenAI(
            model=model,
            api_key=os.getenv("OPENAI_API_KEY")
        ).with_structured_output(CallSummary)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert call center analyst. Analyze the following call transcript and provide a structured summary.

Your task:
1. Write a brief 2-3 sentence summary of the call
2. Extract 3-5 key points discussed
3. List any action items or follow-ups needed
4. Identify what the customer wanted (their intent)
5. Determine if the issue was resolved, unresolved, or escalated
6. List the main topics discussed
7. Assess the overall sentiment (positive, neutral, or negative)

Be concise but thorough. Focus on facts from the transcript."""),
            ("human", """Please analyze this call transcript:

{transcript}""")
        ])

        self.chain = self.prompt | self.llm

    def run(self, state: AgentState) -> AgentState:
        """Generate a summary from the transcript"""

        transcript_text = state.transcript.full_text if state.transcript else state.raw_input

        summary = self.chain.invoke({"transcript": transcript_text})

        state.summary = summary
        state.execution_path.append("summarization")
        state.models_used.append(self.model_name)

        return state

    # Keep backward compatibility
    def run_simple(self, transcript: str) -> CallSummary:
        """Simple run without state (for backward compatibility)"""
        return self.chain.invoke({"transcript": transcript})
```

## Step 3.5: Create Linear LangGraph Workflow

**File: `graph/workflow.py`**
```python
from langgraph.graph import StateGraph, END
from models.schemas import AgentState
from agents.intake_agent import IntakeAgent
from agents.transcription_agent import TranscriptionAgent
from agents.summarization_agent import SummarizationAgent
from agents.qa_scoring_agent import QAScoringAgent

def build_linear_workflow():
    """Build a simple linear workflow without conditional routing"""

    # Initialize agents
    intake_agent = IntakeAgent()
    transcription_agent = TranscriptionAgent()
    summarization_agent = SummarizationAgent(model="gpt-4")
    qa_scoring_agent = QAScoringAgent(model="gpt-4")

    # Create graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("intake", intake_agent.run)
    graph.add_node("transcription", transcription_agent.run)
    graph.add_node("summarization", summarization_agent.run)
    graph.add_node("qa_scoring", qa_scoring_agent.run)

    # Linear edges
    graph.set_entry_point("intake")
    graph.add_edge("intake", "transcription")
    graph.add_edge("transcription", "summarization")
    graph.add_edge("summarization", "qa_scoring")
    graph.add_edge("qa_scoring", END)

    # Compile
    return graph.compile()

# Create singleton instance
workflow = build_linear_workflow()
```

## Step 3.6: Update App for Pipeline

**File: `app.py`** (update)
```python
import streamlit as st
import os
from pathlib import Path
import time

st.set_page_config(
    page_title="Call Center Assistant",
    page_icon="📞",
    layout="wide"
)

# ===================
# Initialize
# ===================
st.title("📞 AI Call Center Assistant")
st.markdown("**Phase 3**: Linear Multi-Agent Pipeline")

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ OPENAI_API_KEY not set. Please add it to your environment or HF Spaces secrets.")
    st.stop()

# Import after env check
from graph.workflow import workflow
from models.schemas import AgentState

# ===================
# Sidebar - Sample Data
# ===================
with st.sidebar:
    st.header("📁 Sample Transcripts")

    sample_dir = Path("data/sample_transcripts")
    if sample_dir.exists():
        sample_files = list(sample_dir.glob("*.txt"))
        if sample_files:
            selected_sample = st.selectbox(
                "Load a sample transcript:",
                options=["None"] + [f.name for f in sample_files]
            )
        else:
            selected_sample = "None"
    else:
        selected_sample = "None"

    st.divider()
    st.markdown("**Pipeline Info**")
    st.caption("Intake → Transcription → Summarization → QA Scoring")

# ===================
# Main Content
# ===================
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📤 Input")

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload transcript (.txt)",
        type=["txt"],
    )

    # Text area for transcript
    if uploaded_file:
        transcript_text = uploaded_file.read().decode("utf-8")
    elif selected_sample != "None":
        sample_path = Path("data/sample_transcripts") / selected_sample
        transcript_text = sample_path.read_text()
    else:
        transcript_text = ""

    transcript_input = st.text_area(
        "Transcript",
        value=transcript_text,
        height=300,
        placeholder="Paste or upload a call transcript..."
    )

    # Process button
    process_btn = st.button(
        "🚀 Run Pipeline",
        type="primary",
        disabled=not transcript_input.strip()
    )

with col_right:
    st.subheader("🔄 Pipeline Status")

    if process_btn and transcript_input.strip():
        # Create initial state
        initial_state = AgentState(
            input_type="transcript",
            raw_input=transcript_input
        )

        # Show pipeline progress
        progress_placeholder = st.empty()

        with progress_placeholder.container():
            with st.status("Running pipeline...", expanded=True) as status:
                st.write("📥 Starting Intake Agent...")
                time.sleep(0.5)

                st.write("📝 Starting Transcription Agent...")
                time.sleep(0.5)

                st.write("📊 Starting Summarization Agent...")
                st.write("🎯 Starting QA Scoring Agent...")

                try:
                    # Run the workflow
                    start_time = time.time()
                    final_state = workflow.invoke(initial_state)
                    elapsed_time = time.time() - start_time

                    st.session_state["last_state"] = final_state
                    st.session_state["elapsed_time"] = elapsed_time

                    status.update(label=f"Pipeline complete! ({elapsed_time:.1f}s)", state="complete")
                except Exception as e:
                    status.update(label=f"Pipeline failed: {e}", state="error")
                    st.error(str(e))
                    st.stop()

    # Show execution path
    if "last_state" in st.session_state:
        state = st.session_state["last_state"]

        st.markdown("**Execution Path**")
        path_str = " → ".join(state.execution_path)
        st.code(path_str)

        st.markdown("**Models Used**")
        for agent, model in zip(state.execution_path, state.models_used):
            st.caption(f"• {agent}: {model}")

# ===================
# Results Tabs
# ===================
st.divider()
st.subheader("📊 Results")

if "last_state" in st.session_state:
    state = st.session_state["last_state"]

    tab1, tab2, tab3, tab4 = st.tabs(["Summary", "QA Scores", "Metadata", "Debug"])

    with tab1:
        if state.summary:
            st.markdown("**Brief Summary**")
            st.info(state.summary.brief_summary)

            st.markdown("**Key Points**")
            for point in state.summary.key_points:
                st.markdown(f"• {point}")

            if state.summary.action_items:
                st.markdown("**Action Items**")
                for item in state.summary.action_items:
                    st.markdown(f"☐ {item}")

            st.markdown("**Customer Intent**")
            st.write(state.summary.customer_intent)

            cols = st.columns(3)
            with cols[0]:
                sentiment_emoji = {"positive": "🟢", "neutral": "🟡", "negative": "🔴"}
                st.metric("Sentiment", f"{sentiment_emoji.get(state.summary.sentiment.value, '⚪')} {state.summary.sentiment.value.title()}")
            with cols[1]:
                resolution_emoji = {"resolved": "✅", "unresolved": "⏳", "escalated": "⬆️"}
                st.metric("Resolution", f"{resolution_emoji.get(state.summary.resolution_status.value, '❓')} {state.summary.resolution_status.value.title()}")
            with cols[2]:
                st.metric("Topics", len(state.summary.topics))

    with tab2:
        if state.qa_scores:
            cols = st.columns(4)
            cols[0].metric("Empathy", f"{state.qa_scores.empathy}/10")
            cols[1].metric("Professionalism", f"{state.qa_scores.professionalism}/10")
            cols[2].metric("Resolution", f"{state.qa_scores.resolution}/10")
            cols[3].metric("Tone", f"{state.qa_scores.tone}/10")

            st.divider()
            st.metric("Overall Score", f"{state.qa_scores.overall}/10")

            st.markdown("**Comments**")
            st.write(state.qa_scores.comments)

    with tab3:
        if state.metadata:
            st.json(state.metadata.model_dump(mode="json"))

    with tab4:
        st.json({
            "execution_path": state.execution_path,
            "models_used": state.models_used,
            "revision_count": state.revision_count,
            "elapsed_time": st.session_state.get("elapsed_time", 0),
            "errors": state.errors
        })

        with st.expander("Full State"):
            st.json(state.model_dump(mode="json"))

else:
    st.info("Run the pipeline to see results.")

# ===================
# Footer
# ===================
st.divider()
st.caption("AI Call Center Assistant | Capstone Project | Phase 3 - Linear Pipeline")
```

## Step 3.7: Test Locally

```bash
streamlit run app.py --server.port=7860
```

1. Select a sample transcript
2. Click "Run Pipeline"
3. Verify all 4 agents run in sequence
4. Check Summary and QA Scores tabs
5. Verify LangSmith shows the full trace

## Step 3.8: Deploy to HF Spaces

```bash
git add .
git commit -m "Phase 3: Linear multi-agent pipeline"
git push
```

## Phase 3 Exit Criteria

- [ ] All 4 agents run in sequence
- [ ] Execution path shows: intake → transcription → summarization → qa_scoring
- [ ] Summary generated correctly
- [ ] QA Scores generated with rubric
- [ ] LangSmith shows full pipeline trace
- [ ] Works on HF Spaces

---

# Phase 4: True Multi-Agent (Supervisor + Critic)

## Goal
Add Supervisor Agent for dynamic routing and Summary Critic for self-correction loops.

## Step 4.1: Create Supervisor Agent

**File: `agents/supervisor_agent.py`**
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import AgentState
from pydantic import BaseModel
from typing import Literal
import os

class SupervisorDecision(BaseModel):
    """Structured output for supervisor decisions"""
    next_agent: Literal[
        "intake",
        "transcription",
        "summarization",
        "summary_critic",
        "qa_scoring",
        "COMPLETE"
    ]
    reasoning: str

class SupervisorAgent:
    """Agent that orchestrates the workflow by deciding which agent to call next"""

    def __init__(self, model: str = "gpt-4"):
        self.model_name = model
        self.llm = ChatOpenAI(
            model=model,
            api_key=os.getenv("OPENAI_API_KEY")
        ).with_structured_output(SupervisorDecision)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a workflow orchestrator for a call center analysis system.

Based on the current state, decide which agent should run next.

**Available Agents:**
1. intake - Extract metadata from input (run first if metadata is missing)
2. transcription - Convert audio to text or structure text input (run if transcript is missing)
3. summarization - Generate call summary (run if summary is missing)
4. summary_critic - Review summary quality (run after summarization)
5. qa_scoring - Score call quality (run after summary is approved)
6. COMPLETE - Finish processing (when all tasks are done)

**Rules:**
1. Always run intake first if metadata is None
2. Run transcription after intake if transcript is None
3. Run summarization after transcription if summary is None
4. Run summary_critic after summarization to review quality
5. If summary_critic says needs_revision=true AND revision_count < 3, run summarization again
6. Run qa_scoring after summary is approved (needs_revision=false)
7. Return COMPLETE when summary and qa_scores exist and summary is approved

Analyze the state and decide the next step."""),
            ("human", """Current State:
- metadata: {has_metadata}
- transcript: {has_transcript}
- summary: {has_summary}
- summary_critique: {has_critique}
- needs_revision: {needs_revision}
- revision_count: {revision_count}
- qa_scores: {has_qa_scores}

What should be the next agent?""")
        ])

        self.chain = self.prompt | self.llm

    def run(self, state: AgentState) -> SupervisorDecision:
        """Decide which agent to run next"""

        decision = self.chain.invoke({
            "has_metadata": state.metadata is not None,
            "has_transcript": state.transcript is not None,
            "has_summary": state.summary is not None,
            "has_critique": state.summary_critique is not None,
            "needs_revision": state.needs_revision,
            "revision_count": state.revision_count,
            "has_qa_scores": state.qa_scores is not None
        })

        return decision
```

## Step 4.2: Create Summary Critic Agent

**File: `agents/summary_critic_agent.py`**
```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import SummaryCritique, AgentState
import os

class SummaryCriticAgent:
    """Agent that reviews summaries and requests revisions if needed.

    Uses Claude (different from GPT-4 summarization) for independent judgment.
    """

    def __init__(self, model: str = "claude-3-sonnet-20240229"):
        self.model_name = model
        self.llm = ChatAnthropic(
            model=model,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        ).with_structured_output(SummaryCritique)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a quality assurance reviewer for call center summaries.

Your job is to evaluate summaries for:

1. **Faithfulness (1-10)**: Does the summary accurately reflect the transcript without hallucinations?
   - 9-10: Perfectly accurate, no made-up information
   - 7-8: Mostly accurate, minor omissions
   - 5-6: Some inaccuracies or missing context
   - Below 5: Significant errors or hallucinations

2. **Completeness (1-10)**: Are all key points, action items, and customer concerns captured?
   - 9-10: All important information included
   - 7-8: Most information included
   - 5-6: Missing some key points
   - Below 5: Major omissions

3. **Conciseness (1-10)**: Is it appropriately brief without losing important details?
   - 9-10: Perfect length, no fluff
   - 7-8: Slightly verbose or brief
   - 5-6: Too long or too short
   - Below 5: Significantly off

**Decision Rules:**
- If ANY score is below 7, set needs_revision=true
- If all scores are 7+, set needs_revision=false
- Provide specific revision instructions if revision is needed"""),
            ("human", """Review this summary against the original transcript:

**TRANSCRIPT:**
{transcript}

**SUMMARY:**
{summary}

Evaluate the summary quality.""")
        ])

        self.chain = self.prompt | self.llm

    def run(self, state: AgentState) -> AgentState:
        """Review the summary and decide if revision is needed"""

        critique = self.chain.invoke({
            "transcript": state.transcript.full_text if state.transcript else state.raw_input,
            "summary": state.summary.model_dump_json() if state.summary else ""
        })

        state.summary_critique = critique
        state.needs_revision = critique.needs_revision

        if critique.needs_revision:
            state.revision_count += 1

        state.execution_path.append("summary_critic")
        state.models_used.append(self.model_name)

        return state
```

## Step 4.3: Update Summarization Agent to Handle Revisions

**File: `agents/summarization_agent.py`** (update)
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import CallSummary, AgentState
import os

class SummarizationAgent:
    """Agent that generates structured summaries from call transcripts"""

    def __init__(self, model: str = "gpt-4"):
        self.model_name = model
        self.llm = ChatOpenAI(
            model=model,
            api_key=os.getenv("OPENAI_API_KEY")
        ).with_structured_output(CallSummary)

        self.initial_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert call center analyst. Analyze the following call transcript and provide a structured summary.

Your task:
1. Write a brief 2-3 sentence summary of the call
2. Extract 3-5 key points discussed
3. List any action items or follow-ups needed
4. Identify what the customer wanted (their intent)
5. Determine if the issue was resolved, unresolved, or escalated
6. List the main topics discussed
7. Assess the overall sentiment (positive, neutral, or negative)

Be concise but thorough. Focus on facts from the transcript."""),
            ("human", """Please analyze this call transcript:

{transcript}""")
        ])

        self.revision_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert call center analyst. Your previous summary needs revision based on feedback.

Carefully address the feedback and create an improved summary."""),
            ("human", """TRANSCRIPT:
{transcript}

PREVIOUS SUMMARY:
{previous_summary}

FEEDBACK:
{feedback}

REVISION INSTRUCTIONS:
{instructions}

Please create an improved summary addressing the feedback.""")
        ])

    def run(self, state: AgentState) -> AgentState:
        """Generate or revise a summary"""

        transcript_text = state.transcript.full_text if state.transcript else state.raw_input

        if state.needs_revision and state.summary_critique:
            # Revision mode
            chain = self.revision_prompt | self.llm
            summary = chain.invoke({
                "transcript": transcript_text,
                "previous_summary": state.summary.model_dump_json() if state.summary else "",
                "feedback": state.summary_critique.feedback,
                "instructions": state.summary_critique.revision_instructions or "Improve based on feedback"
            })
        else:
            # Initial summarization
            chain = self.initial_prompt | self.llm
            summary = chain.invoke({"transcript": transcript_text})

        state.summary = summary
        state.needs_revision = False  # Reset after generating new summary
        state.execution_path.append("summarization")
        state.models_used.append(self.model_name)

        return state
```

## Step 4.4: Create Multi-Agent Workflow with Supervisor

**File: `graph/workflow.py`** (update)
```python
from langgraph.graph import StateGraph, END
from models.schemas import AgentState
from agents.intake_agent import IntakeAgent
from agents.transcription_agent import TranscriptionAgent
from agents.summarization_agent import SummarizationAgent
from agents.summary_critic_agent import SummaryCriticAgent
from agents.qa_scoring_agent import QAScoringAgent
from agents.supervisor_agent import SupervisorAgent

def build_multi_agent_workflow():
    """Build a true multi-agent workflow with supervisor routing"""

    # Initialize agents
    supervisor = SupervisorAgent(model="gpt-4")
    intake_agent = IntakeAgent()
    transcription_agent = TranscriptionAgent()
    summarization_agent = SummarizationAgent(model="gpt-4")
    summary_critic_agent = SummaryCriticAgent(model="claude-3-sonnet-20240229")  # Different model!
    qa_scoring_agent = QAScoringAgent(model="gpt-4")

    # Define the supervisor routing function
    def route_from_supervisor(state: AgentState) -> str:
        decision = supervisor.run(state)
        state.execution_path.append(f"supervisor({decision.next_agent})")
        state.models_used.append(supervisor.model_name)
        return decision.next_agent

    # Create graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("intake", intake_agent.run)
    graph.add_node("transcription", transcription_agent.run)
    graph.add_node("summarization", summarization_agent.run)
    graph.add_node("summary_critic", summary_critic_agent.run)
    graph.add_node("qa_scoring", qa_scoring_agent.run)

    # Entry point goes to supervisor decision
    graph.set_entry_point("supervisor_route")

    # Supervisor routing node
    graph.add_node("supervisor_route", lambda state: state)  # Pass-through, routing handled by edges

    # Conditional edges from supervisor
    graph.add_conditional_edges(
        "supervisor_route",
        route_from_supervisor,
        {
            "intake": "intake",
            "transcription": "transcription",
            "summarization": "summarization",
            "summary_critic": "summary_critic",
            "qa_scoring": "qa_scoring",
            "COMPLETE": END
        }
    )

    # All agents return to supervisor for next decision
    graph.add_edge("intake", "supervisor_route")
    graph.add_edge("transcription", "supervisor_route")
    graph.add_edge("summarization", "supervisor_route")
    graph.add_edge("summary_critic", "supervisor_route")
    graph.add_edge("qa_scoring", "supervisor_route")

    # Compile
    return graph.compile()

# Create singleton instance
workflow = build_multi_agent_workflow()

# Keep backward compatibility
def build_linear_workflow():
    """Simple linear workflow for testing"""
    return build_multi_agent_workflow()
```

## Step 4.5: Update App for Multi-Agent Display

Update `app.py` to show the Supervisor decisions and revision loops in the execution path.

## Step 4.6: Test with Revision-Triggering Transcript

Create a test transcript that produces a summary that will fail the critic review, triggering a revision loop.

## Step 4.7: Deploy and Test

```bash
git add .
git commit -m "Phase 4: True multi-agent with Supervisor and Critic"
git push
```

## Phase 4 Exit Criteria

- [ ] Supervisor decides routing (visible in execution path)
- [ ] Summary Critic uses Claude (different from GPT-4 Summarization)
- [ ] Revision loop works when critique fails
- [ ] Max 3 revisions enforced
- [ ] Execution path shows full journey including loops
- [ ] LangSmith shows supervisor decisions
- [ ] Works on HF Spaces

---

# Phases 5-7: Summary

## Phase 5: Guardrails + Abuse Detection
- Implement input validation (file type, audio classification)
- Add abuse detection (OpenAI Moderation + LLM analysis)
- User confirmation flow for uncertain inputs
- Abuse Review Agent for high-severity cases

## Phase 6: Workflow Animation
- Implement `streamlit-flow-component` visualization
- Real-time node status updates
- Animated edges showing data flow
- Loop visualization for revisions

## Phase 7: Evaluation + Polish
- Create LangSmith evaluation dataset (10-15 examples)
- Implement evaluators (faithfulness, completeness, etc.)
- Run evaluation pipeline
- Polish UI and documentation
- Record demo video

---

# Quick Reference

## Commands

```bash
# Local development
streamlit run app.py --server.port=7860

# Docker build/run
docker build -t call-center-assistant .
docker run -p 7860:7860 --env-file .env call-center-assistant

# Deploy to HF Spaces
git add .
git commit -m "Phase X: Description"
git push
```

## Project Files Changed by Phase

| Phase | Files Created/Modified |
|-------|------------------------|
| 0 | `app.py`, `Dockerfile`, `requirements.txt`, `README.md` |
| 1 | `config/settings.py`, `models/schemas.py`, full project structure |
| 2 | `agents/summarization_agent.py`, sample transcripts |
| 3 | `agents/intake_agent.py`, `agents/transcription_agent.py`, `agents/qa_scoring_agent.py`, `graph/workflow.py` |
| 4 | `agents/supervisor_agent.py`, `agents/summary_critic_agent.py`, updated workflow |
| 5 | `guardrails/` modules |
| 6 | `ui/components/flow_visualizer.py` |
| 7 | `evaluation/` modules |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-22 | Initial execution plan |
| 2.0 | 2026-01-22 | Detailed step-by-step instructions for Phases 0-4 |
