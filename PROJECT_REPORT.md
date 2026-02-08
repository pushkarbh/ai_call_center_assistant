# AI Call Center Assistant
## Technical Project Report

> **Project Type**: Multi-Agent AI System  
> **Version**: 1.0 (Phase 5 Complete)  
> **Last Updated**: January 25, 2026  
> **Deployment**: Hugging Face Spaces (Docker)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [LangGraph Workflow Design](#3-langgraph-workflow-design)
4. [Agent Specifications](#4-agent-specifications)
5. [Inter-Agent Communication & Collaboration](#5-inter-agent-communication--collaboration)
6. [Graph State Management](#6-graph-state-management)
7. [Guardrails & Safety Mechanisms](#7-guardrails--safety-mechanisms)
8. [Technology Stack](#8-technology-stack)
9. [Evaluation Framework](#9-evaluation-framework)
10. [Deployment Architecture](#10-deployment-architecture)
11. [Future Roadmap](#11-future-roadmap)

---

## 1. Executive Summary

### Problem Statement

In modern call centers, crucial insights from customer conversations remain trapped in lengthy transcripts and voice recordings. Manual analysis and quality assessments are:
- **Time-consuming**: Analysts spend hours reviewing calls
- **Inconsistent**: Quality varies between reviewers
- **Reactive**: Issues are identified after the fact
- **Unscalable**: Cannot keep pace with call volume

### Solution

The **AI Call Center Assistant** is a **true multi-agent AI system** that automatically converts call recordings and transcripts into structured insights and quality assessments. The system employs:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AI CALL CENTER ASSISTANT                             │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │   INPUT     │ ─▶ │  MULTI-AGENT│ ─▶ │  QUALITY    │ ─▶ │  STRUCTURED │   │
│  │  (Audio/    │    │  ANALYSIS   │    │  GUARDRAILS │    │   INSIGHTS  │   │
│  │  Transcript)│    │  PIPELINE   │    │  & SAFETY   │    │   OUTPUT    │   │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘   │
│                                                                             │
│  Features:                                                                  │
│  ✓ 7 Specialized AI Agents    ✓ Self-Correction Loops                       │
│  ✓ Dynamic Routing            ✓ Abuse Detection                             │
│  ✓ Input Validation           ✓ Production Observability                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Business Value

| Capability | Business Impact |
|------------|-----------------|
| **Automated Insight Extraction** | 90% reduction in manual review time |
| **QA Monitoring at Scale** | Consistent quality scoring across all interactions |
| **Abuse Detection** | Protect staff, flag problematic interactions in real-time |
| **Self-Correction** | Higher quality outputs through agent collaboration |
| **Compliance & Consistency** | Standardized evaluations across all interactions |
| **Voice-to-Insights Pipeline** | Convert audio into actionable data |

---

## 2. System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              SYSTEM ARCHITECTURE                                    │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                              PRESENTATION LAYER                              │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │    │
│  │  │   Streamlit     │  │   File Upload   │  │   Results Dashboard         │  │    │
│  │  │   Web Interface │  │   (.txt/.wav)   │  │   (Summary, QA, Abuse)      │  │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                       │                                             │
│                                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                           ORCHESTRATION LAYER                                │   │
│  │                                                                              │   │
│  │    ┌──────────────────────────────────────────────────────────────────┐     │    │
│  │    │                     LangGraph StateGraph                          │     │   │
│  │    │                                                                   │     │   │
│  │    │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐ │     │    │
│  │    │   │Validation│─▶│ Intake  │─▶│Transcrip│─▶│ Abuse   │─▶│Summari-│ │     │   │
│  │    │   │  Agent  │  │  Agent  │  │  Agent  │  │Detection│  │ zation │ │     │    │
│  │    │   └─────────┘  └─────────┘  └─────────┘  └─────────┘  └───┬────┘ │     │    │
│  │    │                                                           │      │     │    │
│  │    │                          ┌─────────┐        ┌─────────┐   │      │     │    │
│  │    │                          │   QA    │◀───────│  Critic │◀──┘      │     │    │
│  │    │                          │ Scoring │        │  Agent  │──────────│     │    │
│  │    │                          └─────────┘        └────┬────┘ Revision │     │    │
│  │    │                                                  └─────Loop──────┘     │    │
│  │    └──────────────────────────────────────────────────────────────────┘     │    │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                       │                                             │
│                                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                              AI/LLM LAYER                                    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │    │
│  │  │  GPT-4o-mini│  │  GPT-4o     │  │  Claude     │  │  Whisper API        │ │    │
│  │  │  (Summaries)│  │  (Critical) │  │  (Abuse)    │  │  (Transcription)    │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                       │                                             │
│                                       ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                          OBSERVABILITY LAYER                                 │   │
│  │  ┌─────────────────────────┐  ┌─────────────────────────┐                   │    │
│  │  │     LangSmith           │  │     LiteLLM             │                   │    │
│  │  │  • Tracing & Debugging  │  │  • Model Routing        │                   │    │
│  │  │  • Evaluation           │  │  • Cost Management      │                   │    │
│  │  │  • Monitoring           │  │  • Fallback Chains      │                   │    │
│  │  └─────────────────────────┘  └─────────────────────────┘                   │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Component Overview

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| **Presentation** | Streamlit UI | User interface, file upload, results display |
| **Orchestration** | LangGraph | Multi-agent workflow, state management, conditional routing |
| **Agent** | 7 Specialized Agents | Individual task execution (validation, summarization, QA, etc.) |
| **AI/LLM** | OpenAI, Anthropic | Language model inference for various tasks |
| **Observability** | LangSmith, LiteLLM | Tracing, debugging, cost management |

---

## 3. LangGraph Workflow Design

### What is LangGraph?

LangGraph is a framework for building stateful, multi-actor applications with LLMs. It enables:
- **Directed Graph Workflows**: Define agents as nodes, transitions as edges
- **State Management**: Pass structured state between agents
- **Conditional Routing**: Dynamic decisions based on state
- **Cycles & Loops**: Enable revision and self-correction patterns

### Complete Workflow Graph Visualization

```
                            ┌─────────────────────────────────────────────────────┐
                            │              PHASE 5 WORKFLOW                        │
                            │          (Guardrails + Revision Loop)                │
                            └─────────────────────────────────────────────────────┘

                                              START
                                                │
                                                ▼
                                    ┌─────────────────────┐
                                    │   🛡️ VALIDATION     │  Input Quality Check
                                    │       AGENT         │  (Word count, structure,
                                    │   [Rule-based]      │   spam detection)
                                    └──────────┬──────────┘
                                               │
                               ┌───────────────┴───────────────┐
                               │    is_valid?                   │
                               ▼                               ▼
                          [YES ✓]                         [NO ✗]
                               │                               │
                               ▼                               ▼
                    ┌─────────────────────┐             ┌───────────┐
                    │    📥 INTAKE        │             │    END    │
                    │       AGENT         │             │  (Reject) │
                    │   [Rule-based]      │             └───────────┘
                    │ Generate Call ID    │
                    │ Extract Metadata    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   📝 TRANSCRIPTION  │
                    │       AGENT         │  Text pass-through or
                    │  [pass-through/     │  Whisper API (future)
                    │   whisper-1]        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  🚨 ABUSE DETECTION │  Detect profanity,
                    │       AGENT         │  threats, harassment,
                    │   [gpt-4o-mini]     │  hate speech
                    └──────────┬──────────┘
                               │
                               ▼
         ┌────────────────────────────────────────────────────┐
         │                                                    │
         │  ┌─────────────────────┐                           │
         │  │  📋 SUMMARIZATION   │◀──────────────────────────┤
         │  │       AGENT         │         Revision          │
         │  │   [gpt-4o-mini]     │          Loop             │
         │  │                     │     (max 3 attempts)      │
         │  │ • Brief summary     │                           │
         │  │ • Key points        │                           │
         │  │ • Action items      │                           │
         │  │ • Customer intent   │                           │
         │  │ • Sentiment         │                           │
         │  │ • Resolution status │                           │
         │  └──────────┬──────────┘                           │
         │             │                                      │
         │             ▼                                      │
         │  ┌─────────────────────┐                           │
         │  │   🔍 CRITIC         │                           │
         │  │       AGENT         │                           │
         │  │   [gpt-4o-mini]     │                           │
         │  │                     │                           │
         │  │ • Faithfulness (1-10)                           │
         │  │ • Completeness (1-10)                           │
         │  │ • Conciseness (1-10)                            │
         │  └──────────┬──────────┘                           │
         │             │                                      │
         │             │   needs_revision?                    │
         │             │   && revision_count < 3              │
         │             │                                      │
         │     ┌───────┴───────┐                              │
         │     ▼               ▼                              │
         │ [YES ✓]         [NO ✗]                             │
         │     │               │                              │
         │     └───────────────┼──────────────────────────────┘
         │                     │
         └─────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   📊 QA SCORING     │
                    │       AGENT         │  Evaluate agent
                    │   [gpt-4o-mini]     │  performance
                    │                     │
                    │ • Empathy (0-10)    │
                    │ • Professionalism   │
                    │ • Resolution        │
                    │ • Tone              │
                    └──────────┬──────────┘
                               │
                               ▼
                            ┌─────┐
                            │ END │
                            └─────┘
```

### LangGraph Implementation Code

```python
from langgraph.graph import StateGraph, END
from models.schemas import AgentState

def create_phase5_workflow():
    """Create Phase 5 workflow with Guardrails"""
    
    # Initialize all agents
    validation_agent = InputValidationAgent()
    intake_agent = IntakeAgent()
    transcription_agent = TranscriptionAgent()
    abuse_detection_agent = AbuseDetectionAgent()
    summarization_agent = SummarizationAgent()
    critic_agent = CriticAgent()
    qa_agent = QAScoringAgent()

    # Create workflow graph with Pydantic state
    workflow = StateGraph(AgentState)

    # Add agent nodes
    workflow.add_node("validation", validation_agent.run)
    workflow.add_node("intake", intake_agent.run)
    workflow.add_node("transcription", transcription_agent.run)
    workflow.add_node("abuse_detection", abuse_detection_agent.run)
    workflow.add_node("summarization", summarization_agent.run)
    workflow.add_node("critic", critic_agent.run)
    workflow.add_node("qa_scoring", qa_agent.run)

    # Set entry point (first node)
    workflow.set_entry_point("validation")
    
    # Conditional routing after validation
    workflow.add_conditional_edges(
        "validation",
        should_continue_after_validation,
        {"intake": "intake", "END": END}
    )
    
    # Linear edges
    workflow.add_edge("intake", "transcription")
    workflow.add_edge("transcription", "abuse_detection")
    workflow.add_edge("abuse_detection", "summarization")
    workflow.add_edge("summarization", "critic")
    
    # Revision loop conditional edge
    workflow.add_conditional_edges(
        "critic",
        should_continue_after_critic,
        {"summarization": "summarization", "qa_scoring": "qa_scoring"}
    )
    
    # Final edge
    workflow.add_edge("qa_scoring", END)

    return workflow.compile()
```

### Conditional Routing Functions

```python
def should_continue_after_validation(state: AgentState) -> str:
    """Stop if validation fails, otherwise continue"""
    if not state.validation_result or not state.validation_result.is_valid:
        return "END"
    return "intake"

def should_continue_after_critic(state: AgentState) -> str:
    """Decide whether to revise summary or continue to QA"""
    if state.needs_revision and state.revision_count < 3:
        return "summarization"  # Send back for revision
    else:
        return "qa_scoring"  # Continue forward
```

### Graph Edge Types

| Edge Type | Description | Example |
|-----------|-------------|---------|
| **Linear Edge** | Always follows this path | `intake` → `transcription` |
| **Conditional Edge** | Decision point based on state | `validation` → `intake` OR `END` |
| **Loop Edge** | Returns to previous node | `critic` → `summarization` (revision) |
| **Terminal Edge** | Ends the workflow | `qa_scoring` → `END` |

---

## 4. Agent Specifications

### Agent Overview Matrix

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│                              AGENT ECOSYSTEM                                       │
├────────────────────┬────────────────┬──────────────┬───────────────────────────────┤
│      Agent         │     Type       │    Model     │         Responsibility        │
├────────────────────┼────────────────┼──────────────┼───────────────────────────────┤
│ Input Validation   │   Guardrail    │  Rule-based  │ Input quality validation      │
│ Intake             │   Worker       │  Rule-based  │ Metadata extraction           │
│ Transcription      │   Worker       │  Pass-through│ Text/audio handling           │
│ Abuse Detection    │   Guardrail    │  GPT-4o-mini │ Content moderation            │
│ Summarization      │   Worker       │  GPT-4o-mini │ Call content analysis         │
│ Critic             │   Reviewer     │  GPT-4o-mini │ Quality evaluation            │
│ QA Scoring         │   Worker       │  GPT-4o-mini │ Agent performance scoring     │
└────────────────────┴────────────────┴──────────────┴───────────────────────────────┘
```

---

### 4.1 Input Validation Agent

**Purpose**: Validates input quality before processing to ensure downstream agents receive clean data.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INPUT VALIDATION AGENT                           │
├─────────────────────────────────────────────────────────────────────┤
│  Type: Guardrail (Rule-based)                                       │
│  Model: None (deterministic rules)                                  │
│  File: agents/input_validation_agent.py                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  INPUT                         OUTPUT                               │
│  ─────                         ──────                               │
│  • raw_input (string)    ───▶  • InputValidationResult              │
│  • input_type                   ├── is_valid: bool                  │
│                                 ├── confidence: float               │
│                                 ├── input_type_detected: str        │
│                                 ├── issues: List[str]               │
│                                 ├── warnings: List[str]             │
│                                 └── rejection_reason: str?          │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  VALIDATION CHECKS:                                                 │
│                                                                     │
│  1. Word Count                                                      │
│     ├── Minimum: 10 words                                           │
│     └── Maximum: 5000 words                                         │
│                                                                     │
│  2. Conversation Structure                                          │
│     └── Check for speaker labels (Agent:, Customer:)                │
│                                                                     │
│  3. Special Character Ratio                                         │
│     └── Flag if > 10% non-alphanumeric                              │
│                                                                     │
│  4. Vocabulary Diversity                                            │
│     └── Flag spam if < 50% unique words                             │
│                                                                     │
│  5. Dialogue Structure                                              │
│     └── Warn if single-line input > 50 words                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Implementation**:
```python
class InputValidationAgent:
    def __init__(self):
        self.model_name = "input-validator"
        self.min_words = 10
        self.max_words = 5000

    def run(self, state: AgentState) -> AgentState:
        raw_text = state.raw_input.strip()
        issues = []
        warnings = []
        
        # Word count validation
        word_count = len(raw_text.split())
        if word_count < self.min_words:
            issues.append(f"Input too short: {word_count} words")
        
        # Structure validation
        if ":" not in raw_text and word_count > 20:
            warnings.append("No speaker labels detected")
        
        # Spam detection
        words = raw_text.lower().split()
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.5:
            warnings.append("Low vocabulary diversity (possible spam)")
        
        state.validation_result = InputValidationResult(
            is_valid=len(issues) == 0,
            confidence=1.0 - (0.1 * len(warnings)),
            issues=issues,
            warnings=warnings
        )
        return state
```

---

### 4.2 Intake Agent

**Purpose**: Extracts metadata and generates unique identifiers for call tracking.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INTAKE AGENT                                 │
├─────────────────────────────────────────────────────────────────────┤
│  Type: Worker (Rule-based)                                          │
│  Model: None (deterministic)                                        │
│  File: agents/intake_agent.py                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  INPUT                           OUTPUT                             │
│  ─────                           ──────                             │
│  • raw_input              ───▶   • CallMetadata                     │
│  • input_type                     ├── call_id: "CALL-XXXXXXXX"      │
│  • input_file_path                ├── timestamp: datetime           │
│                                   ├── duration_seconds: float       │
│                                   ├── input_type: str               │
│                                   └── file_name: str                │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  PROCESSING:                                                        │
│                                                                     │
│  1. Generate unique Call ID (UUID-based)                            │
│     Format: CALL-{8-hex-chars}                                      │
│     Example: CALL-0A3F7B2E                                          │
│                                                                     │
│  2. Calculate estimated duration                                    │
│     Formula: (word_count / 150) * 60 seconds                        │
│     Based on ~150 words per minute of conversation                  │
│                                                                     │
│  3. Capture timestamp                                               │
│     UTC timestamp of when processing began                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 4.3 Transcription Agent

**Purpose**: Handles text pass-through and audio-to-text conversion.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TRANSCRIPTION AGENT                             │
├─────────────────────────────────────────────────────────────────────┤
│  Type: Worker                                                       │
│  Model: pass-through (text) / whisper-1 (audio)                     │
│  File: agents/transcription_agent.py                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                    ┌──────────────┐                                 │
│                    │    INPUT     │                                 │
│                    │  raw_input   │                                 │
│                    └──────┬───────┘                                 │
│                           │                                         │
│                    ┌──────▼───────┐                                 │
│                    │  Input Type? │                                 │
│                    └──────┬───────┘                                 │
│              ┌────────────┴────────────┐                            │
│              ▼                         ▼                            │
│     ┌─────────────────┐       ┌─────────────────┐                   │
│     │   TRANSCRIPT    │       │     AUDIO       │                   │
│     │  (pass-through) │       │  (Whisper API)  │                   │
│     │  confidence=1.0 │       │  confidence=0.95│                   │
│     └────────┬────────┘       └────────┬────────┘                   │
│              │                         │                            │
│              └────────────┬────────────┘                            │
│                           ▼                                         │
│                  ┌─────────────────┐                                │
│                  │ TranscriptData  │                                │
│                  │ • full_text     │                                │
│                  │ • segments[]    │                                │
│                  │ • language      │                                │
│                  │ • confidence    │                                │
│                  └─────────────────┘                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 4.4 Abuse Detection Agent

**Purpose**: Scans transcripts for abusive content including profanity, threats, harassment, and hate speech.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ABUSE DETECTION AGENT                            │
├─────────────────────────────────────────────────────────────────────┤
│  Type: Guardrail (LLM-based)                                        │
│  Model: GPT-4o-mini (temperature=0)                                 │
│  File: agents/abuse_detection_agent.py                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  DETECTION CATEGORIES:                                              │
│  ─────────────────────                                              │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  PROFANITY  │  │   THREAT    │  │ HARASSMENT  │  │ HATE SPEECH │ │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤  ├─────────────┤ │
│  │ • bullshit  │  │ • lawsuit   │  │ • you idiot │  │ • racial    │ │
│  │ • damn      │  │ • sue you   │  │ • incompe-  │  │   slurs     │ │
│  │ • crap      │  │ • come to   │  │   tent      │  │ • xenophobic│ │
│  │ • f-word    │  │   office    │  │ • personal  │  │ • discrimi- │ │
│  │ • s-word    │  │ • you'll    │  │   attacks   │  │   nation    │ │
│  │             │  │   regret    │  │             │  │             │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  SEVERITY LEVELS:                                                   │
│                                                                     │
│  ┌────────────┬───────────┬─────────────────────────────────────┐   │
│  │  Severity  │  Score    │  Examples                           │   │
│  ├────────────┼───────────┼─────────────────────────────────────┤   │
│  │  🟢 LOW    │   1-3     │  Mild profanity (damn, crap)        │   │
│  │  🟡 MEDIUM │   4-6     │  Direct insults, legal threats      │   │
│  │  🔴 HIGH   │   7-10    │  Severe profanity, physical threats │   │
│  └────────────┴───────────┴─────────────────────────────────────┘   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  OUTPUT SCHEMA:                                                     │
│                                                                     │
│  AbuseFlag:                                                         │
│   ├── detected: bool                                                │
│   ├── speaker: "customer" | "agent" | "both"                        │
│   ├── abuse_type: List[AbuseType]                                   │
│   ├── severity: AbuseSeverity                                       │
│   ├── evidence: List[str]  # Quoted excerpts                        │
│   ├── recommended_action: str                                       │
│   └── requires_escalation: bool                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**LLM Prompt Structure**:
```python
SYSTEM_PROMPT = """
You are a content moderation system for call center transcripts.

DETECTION CRITERIA:
1. profanity: Flag ANY swear words or vulgar language
2. threat: Flag ANY threats (legal, physical, implied harm)
3. harassment: Flag personal attacks or insults
4. hate_speech: Flag discriminatory language

SEVERITY LEVELS:
- Low (1-3): Mild profanity, frustrated language
- Medium (4-6): Direct insults, legal threats
- High (7-10): Severe profanity, physical threats

OUTPUT FORMAT:
TYPE: [profanity|threat|harassment|hate_speech]
SEVERITY: [1-10]
TEXT: "[exact quote]"
CONTEXT: [explanation]
"""
```

---

### 4.5 Summarization Agent

**Purpose**: Generates structured call summaries with sentiment analysis and resolution tracking.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SUMMARIZATION AGENT                              │
├─────────────────────────────────────────────────────────────────────┤
│  Type: Worker (LLM-based)                                           │
│  Model: GPT-4o-mini with structured output                          │
│  File: agents/summarization_agent.py                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  INPUT: TranscriptData.full_text                                    │
│                                                                     │
│                         ┌────────────────┐                          │
│                         │   LLM PROMPT   │                          │
│                         │                │                          │
│                         │ "Analyze this  │                          │
│                         │  call and      │                          │
│                         │  provide..."   │                          │
│                         └───────┬────────┘                          │
│                                 │                                   │
│                                 ▼                                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     CallSummary (Pydantic)                    │  │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │                                                               │  │
│  │  brief_summary: str                                           │  │
│  │  ├── "2-3 sentence overview of the call"                      │  │
│  │                                                               │  │
│  │  key_points: List[str]                                        │  │
│  │  ├── "3-5 bullet points of important information"             │  │
│  │                                                               │  │
│  │  action_items: List[str]                                      │  │
│  │  ├── "Follow-up tasks identified"                             │  │
│  │                                                               │  │
│  │  customer_intent: str                                         │  │
│  │  ├── "What the customer wanted to achieve"                    │  │
│  │                                                               │  │
│  │  sentiment: Sentiment                                         │  │
│  │  ├── POSITIVE | NEUTRAL | NEGATIVE                            │  │
│  │                                                               │  │
│  │  resolution_status: ResolutionStatus                          │  │
│  │  ├── RESOLVED | UNRESOLVED | ESCALATED                        │  │
│  │                                                               │  │
│  │  topics: List[str]                                            │  │
│  │  └── "Main topics discussed during the call"                  │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  REVISION HANDLING:                                                 │
│                                                                     │
│  If revision_count > 0 and summary_critique exists:                 │
│   • Include previous critique feedback in prompt                    │
│   • Add specific revision instructions                              │
│   • Track revision attempt number                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 4.6 Critic Agent

**Purpose**: Evaluates summary quality on three dimensions and decides if revision is needed.

```
┌─────────────────────────────────────────────────────────────────────┐
│                       CRITIC AGENT                                  │
├─────────────────────────────────────────────────────────────────────┤
│  Type: Reviewer (LLM-based)                                         │
│  Model: GPT-4o-mini with structured output                          │
│  File: agents/critic_agent.py                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  EVALUATION DIMENSIONS:                                             │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                                                               │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  │   │
│  │  │  FAITHFULNESS  │  │ COMPLETENESS   │  │  CONCISENESS   │  │   │
│  │  │    (1-10)      │  │    (1-10)      │  │    (1-10)      │  │   │
│  │  ├────────────────┤  ├────────────────┤  ├────────────────┤  │   │
│  │  │ Does summary   │  │ Are all key    │  │ Is it clear &  │  │   │
│  │  │ accurately     │  │ points from    │  │ to-the-point   │  │   │
│  │  │ reflect        │  │ transcript     │  │ without        │  │   │
│  │  │ transcript?    │  │ captured?      │  │ verbosity?     │  │   │
│  │  │                │  │                │  │                │  │   │
│  │  │ 9-10: Perfect  │  │ 9-10: Complete │  │ 9-10: Perfect  │  │   │
│  │  │ 7-8:  Minor    │  │ 7-8:  Most     │  │ 7-8:  Good     │  │   │
│  │  │ 5-6:  Some     │  │ 5-6:  Missing  │  │ 5-6:  Verbose  │  │   │
│  │  │ 1-4:  Major    │  │ 1-4:  Major    │  │ 1-4:  Confusing│  │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘  │   │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  DECISION LOGIC:                                                    │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                                                               │  │
│  │   IF any score < 7:                                           │  │
│  │       needs_revision = True                                   │  │
│  │       Generate revision_instructions                          │  │
│  │                                                               │  │
│  │   IF all scores >= 7:                                         │  │
│  │       needs_revision = False                                  │  │
│  │       Proceed to QA Scoring                                   │  │
│  │                                                               │  │
│  │   Maximum revision attempts: 3                                │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  OUTPUT SCHEMA:                                                     │
│                                                                     │
│  SummaryCritique:                                                   │
│   ├── faithfulness_score: int (1-10)                                │
│   ├── completeness_score: int (1-10)                                │
│   ├── conciseness_score: int (1-10)                                 │
│   ├── needs_revision: bool                                          │
│   ├── revision_instructions: str | None                             │
│   └── feedback: str                                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 4.7 QA Scoring Agent

**Purpose**: Evaluates agent performance on customer service quality dimensions.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     QA SCORING AGENT                                │
├─────────────────────────────────────────────────────────────────────┤
│  Type: Worker (LLM-based)                                           │
│  Model: GPT-4o-mini with structured output                          │
│  File: agents/qa_scoring_agent.py                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SCORING RUBRIC:                                                    │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                                                               │  │
│  │  ┌──────────────┐  ┌──────────────┐                           │  │
│  │  │   EMPATHY    │  │PROFESSIONAL-│                           │   │
│  │  │   (0-10)     │  │  ISM (0-10) │                           │   │
│  │  ├──────────────┤  ├──────────────┤                           │  │
│  │  │ Understanding│  │ Courteous & │                           │   │
│  │  │ & compassion │  │ respectful  │                           │   │
│  │  │ for customer │  │ behavior    │                           │   │
│  │  │ situation    │  │             │                           │   │
│  │  └──────────────┘  └──────────────┘                           │  │
│  │                                                               │  │
│  │  ┌──────────────┐  ┌──────────────┐                           │  │
│  │  │ RESOLUTION   │  │    TONE      │                           │  │
│  │  │   (0-10)     │  │   (0-10)     │                           │  │
│  │  ├──────────────┤  ├──────────────┤                           │  │
│  │  │ Effectiveness│  │ Friendly &  │                           │   │
│  │  │ of issue     │  │ appropriate │                           │   │
│  │  │ resolution   │  │ throughout  │                           │   │
│  │  └──────────────┘  └──────────────┘                           │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  SCORING GUIDE:                                                     │
│                                                                     │
│  9-10: Exceptional                                                  │
│  7-8:  Good                                                         │
│  5-6:  Adequate                                                     │
│  3-4:  Needs Improvement                                            │
│  0-2:  Poor                                                         │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  OUTPUT SCHEMA:                                                     │
│                                                                     │
│  QAScores:                                                          │
│   ├── empathy: float (0-10)                                         │
│   ├── professionalism: float (0-10)                                 │
│   ├── resolution: float (0-10)                                      │
│   ├── tone: float (0-10)                                            │
│   ├── comments: str                                                 │
│   └── overall: float (computed average)                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Inter-Agent Communication & Collaboration

### How Agents Work Together

The agents in this system collaborate through a **shared state pattern** orchestrated by LangGraph. Unlike traditional microservices that communicate via APIs, these agents share a single state object that flows through the pipeline.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         AGENT COLLABORATION PATTERN                                 │
│                                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │                           SHARED STATE (AgentState)                           │  │
│  │                                                                               │  │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │    │
│  │   │ Input   │  │Metadata │  │Transcript│  │ Summary │  │ QA      │           │   │
│  │   │ Data    │  │         │  │ Data    │  │ Data    │  │ Scores  │           │    │
│  │   └────▲────┘  └────▲────┘  └────▲────┘  └────▲────┘  └────▲────┘           │    │
│  │        │            │            │            │            │                  │  │
│  └────────┼────────────┼────────────┼────────────┼────────────┼──────────────────┘  │
│           │            │            │            │            │                     │
│           │ writes     │ writes     │ writes     │ writes     │ writes              │
│           │            │            │            │            │                     │
│     ┌─────┴─────┐┌─────┴─────┐┌─────┴─────┐┌─────┴─────┐┌─────┴─────┐               │
│     │Validation ││  Intake   ││Transcrip- ││Summariza- ││    QA     │               │
│     │  Agent    ││  Agent    ││tion Agent ││tion Agent ││  Scoring  │               │
│     └───────────┘└───────────┘└───────────┘└───────────┘└───────────┘               │
│                                                                                     │
│  DATA FLOW:                                                                         │
│  Each agent:                                                                        │
│   1. Receives full state                                                            │
│   2. Reads what it needs                                                            │
│   3. Writes its output to state                                                     │
│   4. Returns modified state                                                         │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Collaboration Patterns

#### Pattern 1: Sequential Handoff

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SEQUENTIAL HANDOFF                               │
│                                                                     │
│   Validation ─────▶ Intake ─────▶ Transcription ─────▶ Abuse        │
│       │               │               │                   │         │
│       │               │               │                   │         │
│       ▼               ▼               ▼                   ▼         │
│   is_valid      call_id        transcript.         abuse_flags[]    │
│   issues[]      timestamp       full_text                           │
│   warnings[]    duration                                            │
│                                                                     │
│   Each agent adds to state, next agent reads from state             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### Pattern 2: Revision Loop (Critic-Summarization)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    REVISION LOOP PATTERN                            │
│                                                                     │
│                     ┌─────────────────────┐                         │
│                     │   Summarization     │◀────────────┐           │
│                     │      Agent          │             │           │
│                     └──────────┬──────────┘             │           │
│                                │                        │           │
│                     state.summary = CallSummary         │           │
│                                │                        │           │
│                                ▼                        │           │
│                     ┌─────────────────────┐             │           │
│                     │     Critic          │             │           │
│                     │      Agent          │             │           │
│                     └──────────┬──────────┘             │           │
│                                │                        │           │
│               state.summary_critique = SummaryCritique  │           │
│               state.needs_revision = True/False         │           │
│               state.revision_count += 1                 │           │
│                                │                        │           │
│                    ┌───────────┴───────────┐            │           │
│                    ▼                       ▼            │           │
│              needs_revision          !needs_revision    │           │
│              && count < 3            || count >= 3      │           │
│                    │                       │            │           │
│                    │                       ▼            │           │
│                    └───────────────▶  QA Scoring        │           │
│                            │                            │           │
│                            └────────────────────────────┘           │
│                                                                     │
│   The Critic can send work back to Summarization up to 3 times      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### Pattern 3: Conditional Branching (Validation)

```
┌─────────────────────────────────────────────────────────────────────┐
│                   CONDITIONAL BRANCHING                             │
│                                                                     │
│                     ┌─────────────────────┐                         │
│                     │    Validation       │                         │
│                     │      Agent          │                         │
│                     └──────────┬──────────┘                         │
│                                │                                    │
│                   state.validation_result.is_valid                  │
│                                │                                    │
│                    ┌───────────┴───────────┐                        │
│                    ▼                       ▼                        │
│               is_valid=True         is_valid=False                  │
│                    │                       │                        │
│                    ▼                       ▼                        │
│              ┌──────────┐           ┌──────────┐                    │
│              │  Intake  │           │   END    │                    │
│              │  Agent   │           │ (Reject) │                    │
│              └──────────┘           └──────────┘                    │
│                                                                     │
│   Invalid input terminates workflow immediately                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Agent Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           AGENT DEPENDENCIES                                        │
│                                                                                     │
│   AGENT              READS FROM STATE           WRITES TO STATE                     │
│   ─────              ────────────────           ───────────────                     │
│                                                                                     │
│   Validation    ─▶   raw_input              ─▶   validation_result                  │
│                                                  errors[]                           │
│                                                                                     │
│   Intake        ─▶   raw_input              ─▶   metadata                           │
│                      input_type                  (call_id, timestamp)               │
│                      input_file_path                                                │
│                                                                                     │
│   Transcription ─▶   raw_input              ─▶   transcript                         │
│                      input_type                  (full_text, segments)              │
│                                                                                     │
│   Abuse         ─▶   transcript.full_text   ─▶   abuse_flags[]                      │
│   Detection                                                                         │
│                                                                                     │
│   Summarization ─▶   transcript.full_text   ─▶   summary                            │
│                      summary_critique             (if revision)                     │
│                      revision_count                                                 │
│                                                                                     │
│   Critic        ─▶   transcript.full_text   ─▶   summary_critique                   │
│                      summary                      needs_revision                    │
│                                                   revision_count                    │
│                                                                                     │
│   QA Scoring    ─▶   transcript.full_text   ─▶   qa_scores                          │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Graph State Management

### AgentState Schema

The central `AgentState` class is a Pydantic model that defines all data shared between agents:

```python
class AgentState(BaseModel):
    """State passed between agents in LangGraph"""

    # ═══════════════════════════════════════════════════════
    # INPUT SECTION
    # ═══════════════════════════════════════════════════════
    input_file_path: Optional[str] = None
    input_type: str = "transcript"  # "audio" | "transcript"
    raw_input: Optional[str] = None

    # ═══════════════════════════════════════════════════════
    # VALIDATION SECTION
    # ═══════════════════════════════════════════════════════
    validation_result: Optional[InputValidationResult] = None
    user_confirmed: bool = False

    # ═══════════════════════════════════════════════════════
    # PROCESSING OUTPUTS
    # ═══════════════════════════════════════════════════════
    metadata: Optional[CallMetadata] = None
    transcript: Optional[TranscriptData] = None
    summary: Optional[CallSummary] = None
    summary_critique: Optional[SummaryCritique] = None
    qa_scores: Optional[QAScores] = None
    abuse_flags: List[AbuseFlag] = []

    # ═══════════════════════════════════════════════════════
    # CONTROL FLOW
    # ═══════════════════════════════════════════════════════
    current_agent: str = "supervisor"
    needs_revision: bool = False
    revision_count: int = 0
    execution_path: List[str] = []
    models_used: List[str] = []
    errors: List[str] = []

    class Config:
        arbitrary_types_allowed = True
```

### State Lifecycle Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           STATE LIFECYCLE                                           │
│                                                                                     │
│   PHASE 1: INITIALIZATION                                                           │
│   ───────────────────────                                                           │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │  AgentState(                                                                 │  │
│   │      raw_input = "Agent: Hello...",                                          │  │
│   │      input_type = "transcript",                                              │  │
│   │      input_file_path = "billing_inquiry.txt"                                 │  │
│   │  )                                                                           │  │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                            │
│                                        ▼                                            │
│   PHASE 2: VALIDATION                                                               │
│   ───────────────────                                                               │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │  + validation_result = InputValidationResult(                                │  │
│   │        is_valid = True,                                                      │  │
│   │        confidence = 0.9,                                                     │  │
│   │        issues = [],                                                          │  │
│   │        warnings = []                                                         │  │
│   │    )                                                                         │  │
│   │  + execution_path = ["validation"]                                           │  │
│   │  + models_used = ["input-validator"]                                         │  │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                            │
│                                        ▼                                            │
│   PHASE 3: INTAKE                                                                   │
│   ──────────────                                                                    │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │  + metadata = CallMetadata(                                                  │  │
│   │        call_id = "CALL-0A3F7B2E",                                            │  │
│   │        timestamp = 2026-01-25T10:30:00,                                      │  │
│   │        duration_seconds = 180.0                                              │  │
│   │    )                                                                         │  │
│   │  + execution_path = ["validation", "intake"]                                 │  │
│   │  + models_used = ["input-validator", "rule-based"]                           │  │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                            │
│                                        ▼                                            │
│   PHASE 4: TRANSCRIPTION                                                            │
│   ─────────────────────                                                             │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │  + transcript = TranscriptData(                                              │  │
│   │        full_text = "Agent: Hello...",                                        │  │
│   │        language = "en",                                                      │  │
│   │        confidence = 1.0                                                      │  │
│   │    )                                                                         │  │
│   │  + execution_path = ["validation", "intake", "transcription"]                │  │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                            │
│                                        ▼                                            │
│   PHASE 5: ABUSE DETECTION                                                          │
│   ───────────────────────                                                           │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │  + abuse_flags = [                                                           │  │
│   │        AbuseFlag(detected=True, abuse_type=[PROFANITY], severity=LOW)        │  │
│   │    ]  OR  []                                                                 │  │
│   │  + execution_path = [..., "abuse_detection"]                                 │  │
│   │  + models_used = [..., "gpt-4o-mini"]                                        │  │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                            │
│                                        ▼                                            │
│   PHASE 6: SUMMARIZATION (may repeat up to 3x)                                      │
│   ────────────────────────────────────────────                                      │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │  + summary = CallSummary(                                                    │  │
│   │        brief_summary = "Customer called about...",                           │  │
│   │        key_points = [...],                                                   │  │
│   │        sentiment = NEGATIVE,                                                 │  │
│   │        resolution_status = RESOLVED                                          │  │
│   │    )                                                                         │  │
│   │  + execution_path = [..., "summarization"]                                   │  │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                            │
│                                        ▼                                            │
│   PHASE 7: CRITIC                                                                   │
│   ──────────────                                                                    │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │  + summary_critique = SummaryCritique(                                       │  │
│   │        faithfulness_score = 8,                                               │  │
│   │        completeness_score = 9,                                               │  │
│   │        conciseness_score = 7,                                                │  │
│   │        needs_revision = False                                                │  │
│   │    )                                                                         │  │
│   │  + needs_revision = False                                                    │  │
│   │  + revision_count = 0                                                        │  │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                            │
│                                        ▼                                            │
│   PHASE 8: QA SCORING                                                               │
│   ──────────────────                                                                │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │  + qa_scores = QAScores(                                                     │  │
│   │        empathy = 8.0,                                                        │  │
│   │        professionalism = 9.0,                                                │  │
│   │        resolution = 8.5,                                                     │  │
│   │        tone = 8.0,                                                           │  │
│   │        overall = 8.4                                                         │  │
│   │    )                                                                         │  │
│   │  + execution_path = ["validation", "intake", "transcription",                │  │
│   │                      "abuse_detection", "summarization", "critic",           │  │
│   │                      "qa_scoring"]                                           │  │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│   FINAL STATE: Complete state object with all outputs                               │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Pydantic Data Models

All data structures use Pydantic for validation and type safety:

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           PYDANTIC DATA MODELS                                      │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │ ENUMS                                                                        │   │
│  ├─────────────────────────────────────────────────────────────────────────────┤    │
│  │                                                                              │   │
│  │  Sentiment             ResolutionStatus        AbuseType                     │   │
│  │  ──────────            ────────────────        ─────────                     │   │
│  │  • POSITIVE            • RESOLVED              • PROFANITY                   │   │
│  │  • NEUTRAL             • UNRESOLVED            • THREAT                      │   │
│  │  • NEGATIVE            • ESCALATED             • HARASSMENT                  │   │
│  │                                                • DISCRIMINATION              │   │
│  │                                                • NONE                        │   │
│  │                                                                              │   │
│  │  AbuseSeverity                                                               │   │
│  │  ──────────────                                                              │   │
│  │  • LOW • MEDIUM • HIGH • CRITICAL • NONE                                     │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │ DATA MODELS                                                                  │   │
│  ├─────────────────────────────────────────────────────────────────────────────┤    │
│  │                                                                              │   │
│  │  CallMetadata              TranscriptData          CallSummary               │   │
│  │  ────────────              ──────────────          ───────────               │   │
│  │  • call_id: str            • segments: List[]      • brief_summary: str      │   │
│  │  • timestamp: datetime     • full_text: str        • key_points: List[str]   │   │
│  │  • duration_seconds: float • language: str         • action_items: List[str] │   │
│  │  • input_type: str         • confidence: float     • customer_intent: str    │   │
│  │  • file_name: str          (0.0 - 1.0)            • sentiment: Sentiment     │   │
│  │                                                    • resolution_status       │   │
│  │                                                    • topics: List[str]       │   │
│  │                                                                              │   │
│  │  QAScores                  SummaryCritique         AbuseFlag                 │   │
│  │  ────────                  ───────────────         ─────────                 │   │
│  │  • empathy: float          • faithfulness: int     • detected: bool          │   │
│  │  • professionalism: float  • completeness: int     • speaker: str            │   │
│  │  • resolution: float       • conciseness: int      • abuse_type: List[]      │   │
│  │  • tone: float             • needs_revision: bool  • severity: Severity      │   │
│  │  • comments: str           • revision_instructions • evidence: List[str]     │   │
│  │  • overall: float (calc)   • feedback: str         • recommended_action      │   │
│  │                                                    • requires_escalation     │   │
│  │                                                                              │   │
│  │  InputValidationResult                                                       │   │
│  │  ─────────────────────                                                       │   │
│  │  • is_valid: bool                                                            │   │
│  │  • confidence: float                                                         │   │
│  │  • input_type_detected: str                                                  │   │
│  │  • issues: List[str]                                                         │   │
│  │  • warnings: List[str]                                                       │   │
│  │  • rejection_reason: str                                                     │   │
│  │                                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Benefits of Pydantic Integration

| Without Pydantic | With Pydantic |
|------------------|---------------|
| LLM returns `"The call went well"` | LLM returns `{"sentiment": "positive", ...}` |
| QA score might be `"8/10"` or `"eight"` | Always `float` between 0-10 |
| Missing fields crash your app | Validation error before processing |
| Manual JSON parsing everywhere | Automatic serialization |
| No IDE autocomplete | Full type hints and autocomplete |
| Hope LLM follows format | **Enforce** LLM follows format |

---

## 7. Guardrails & Safety Mechanisms

### Guardrails Overview

Guardrails are protective mechanisms that ensure input quality and content safety:

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           GUARDRAILS ARCHITECTURE                                   │
│                                                                                     │
│                              ┌───────────────────┐                                  │
│                              │     USER INPUT    │                                  │
│                              │  (transcript/     │                                  │
│                              │   audio file)     │                                  │
│                              └─────────┬─────────┘                                  │
│                                        │                                            │
│                                        ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                         GUARDRAIL LAYER 1                                    │  │
│   │                      INPUT VALIDATION AGENT                                  │  │
│   │                                                                              │  │
│   │   ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐               │   │
│   │   │   Word     │ │  Structure │ │   Spam     │ │  Special   │               │   │
│   │   │   Count    │ │   Check    │ │ Detection  │ │   Chars    │               │   │
│   │   │  10-5000   │ │  Speaker   │ │  Vocab     │ │  < 10%     │               │   │
│   │   │   words    │ │  Labels    │ │ Diversity  │ │  ratio     │               │   │
│   │   └────────────┘ └────────────┘ └────────────┘ └────────────┘               │   │
│   │                                                                              │  │
│   │   OUTCOME: ✓ PASS → Continue  |  ✗ FAIL → Stop & Return Error               │   │
│   │                                                                              │  │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                            │
│                                   [If valid]                                        │
│                                        ▼                                            │
│                           ┌─────────────────────────┐                               │
│                           │    CORE PROCESSING      │                               │
│                           │  Intake → Transcription │                               │
│                           └────────────┬────────────┘                               │
│                                        │                                            │
│                                        ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                         GUARDRAIL LAYER 2                                    │  │
│   │                      ABUSE DETECTION AGENT                                   │  │
│   │                                                                              │  │
│   │   ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐               │   │
│   │   │ PROFANITY  │ │  THREATS   │ │ HARASSMENT │ │HATE SPEECH │               │   │
│   │   │            │ │            │ │            │ │            │               │   │
│   │   │ Swear words│ │ Legal/     │ │ Personal   │ │ Racial,    │               │   │
│   │   │ Vulgar     │ │ Physical   │ │ attacks,   │ │ Gender,    │               │   │
│   │   │ language   │ │ threats    │ │ Insults    │ │ Religion   │               │   │
│   │   └────────────┘ └────────────┘ └────────────┘ └────────────┘               │   │
│   │                                                                              │  │
│   │   OUTCOME: Flag & Continue (doesn't block) → Abuse info in report           │   │
│   │                                                                              │  │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                            │
│                                        ▼                                            │
│                           ┌─────────────────────────┐                               │
│                           │   CONTINUE PROCESSING   │                               │
│                           │ Summarization → Critic  │                               │
│                           │ → QA Scoring → END      │                               │
│                           └─────────────────────────┘                               │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Input Validation Checks

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         INPUT VALIDATION CHECKS                                     │
│                                                                                     │
│   CHECK              THRESHOLD              ACTION                                  │
│   ─────              ─────────              ──────                                  │
│                                                                                     │
│   Word Count         < 10 words             ❌ HARD REJECT                          │
│   (too short)        "Input too short"      Stop processing                         │
│                                                                                     │
│   Word Count         > 5000 words           ❌ HARD REJECT                          │
│   (too long)         "Input too long"       Stop processing                         │
│                                                                                     │
│   Structure          No ":" characters      ⚠️ WARNING                              │
│   (no speaker        when > 20 words        "No speaker labels detected"            │
│    labels)                                  Continue processing                     │
│                                                                                     │
│   Special Chars      > 10% of text          ⚠️ WARNING                              │
│   (corrupted?)       is special chars       "High special character ratio"          │
│                                             Continue processing                     │
│                                                                                     │
│   Vocabulary         < 50% unique           ⚠️ WARNING                              │
│   Diversity          words                  "Low vocabulary diversity               │
│   (spam?)                                    (possible spam)"                       │
│                                             Continue processing                     │
│                                                                                     │
│   Line Count         Single line with       ⚠️ WARNING                              │
│                      > 50 words             "May not be conversation"               │
│                                             Continue processing                     │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Abuse Detection Categories

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         ABUSE DETECTION MATRIX                                      │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                              │  │
│   │   CATEGORY        EXAMPLES                               SEVERITY RANGE      │  │
│   │   ────────        ────────                               ──────────────      │  │
│   │                                                                              │  │
│   │   PROFANITY       "bullshit", "damn", "crap"             🟡 LOW (1-3)        │  │
│   │                   "f*ck", "sh*t", "a**hole"              🟠 MED (4-6)        │  │
│   │                                                          🔴 HIGH (7-10)      │  │
│   │                                                                              │  │
│   │   THREATS         "I'll report this to authorities"      🟡 LOW (1-3)        │  │
│   │                   "I'll sue you", "get a lawyer"         🟠 MED (4-6)        │  │
│   │                   "I'll come to your office"             🔴 HIGH (7-10)      │  │
│   │                   Physical harm implications                                 │  │
│   │                                                                              │  │
│   │   HARASSMENT      "This is frustrating" (not abuse)      ✓ Not flagged      │   │
│   │                   "You're incompetent"                   🟡 LOW (1-3)        │  │
│   │                   "You're an idiot"                      🟠 MED (4-6)        │  │
│   │                   Repeated personal attacks              🔴 HIGH (7-10)      │  │
│   │                                                                              │  │
│   │   HATE SPEECH     Stereotyping                           🟠 MED (4-6)        │  │
│   │                   Racial/ethnic slurs                    🔴 HIGH (7-10)      │  │
│   │                   Xenophobic comments                    🔴 HIGH (7-10)      │  │
│   │                   Discrimination based on identity       🔴 HIGH (7-10)      │  │
│   │                                                                              │  │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│   IMPORTANT: Normal frustration is NOT abuse                                        │
│   ───────────────────────────────────────────                                       │
│   • "I'm very upset about this" → ✓ Not flagged                                     │
│   • "This is unacceptable service" → ✓ Not flagged                                  │
│   • "I've been waiting for hours" → ✓ Not flagged                                   │
│   • "You people are all the same" → ⚠️ Flagged (harassment)                         │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Guardrail Test Cases

The system includes comprehensive test cases to validate guardrail behavior:

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         GUARDRAIL TEST SUITE                                        │
│                         (test_data/guardrail_tests/)                                │
│                                                                                     │
│   FILE                          EXPECTED RESULT                                     │
│   ────                          ───────────────                                     │
│                                                                                     │
│   INPUT VALIDATION TESTS:                                                           │
│   ───────────────────────                                                           │
│   01_valid_normal.txt           ✅ Pass validation, no abuse flags                  │
│   02_too_short.txt              ❌ FAIL validation (< 10 words)                     │
│   08_spam_repetition.txt        ⚠️ Pass with WARNING (low vocab diversity)          │
│   10_no_structure.txt           ⚠️ Pass with WARNING (no speaker labels)            │
│                                                                                     │
│   ABUSE DETECTION TESTS:                                                            │
│   ─────────────────────                                                             │
│   03_profanity.txt              🚨 Detect profanity (low-medium severity)           │
│   04_threats.txt                🚨 Detect threats (medium-high severity)            │
│   05_harassment.txt             🚨 Detect harassment (medium severity)              │
│   06_hate_speech.txt            🚨 Detect hate speech (high severity)               │
│   07_mixed_abuse.txt            🚨 Detect multiple: profanity + threat + harassment │
│                                                                                     │
│   EDGE CASES:                                                                       │
│   ───────────                                                                       │
│   09_frustrated_but_polite.txt  ✅ Pass - Strong frustration WITHOUT abuse          │
│   11_professional_complaint.txt ✅ Pass - Professional tone complaint               │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Response Actions by Severity

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                      SEVERITY-BASED RESPONSE ACTIONS                                │
│                                                                                     │
│   SEVERITY       SPEAKER       ACTION                                               │
│   ────────       ───────       ──────                                               │
│                                                                                     │
│   🟡 LOW         Customer      • Flag in report                                     │
│                                • Include in summary                                 │
│                                • Continue processing                                │
│                                                                                     │
│   🟡 LOW         Agent         • Flag for coaching                                  │
│                                • Add to QA feedback                                 │
│                                                                                     │
│   🟠 MEDIUM      Customer      • Flag prominently in report                         │
│                                • Supervisor notification recommended                │
│                                                                                     │
│   🟠 MEDIUM      Agent         • Flag for coaching (priority)                       │
│                                • Manager review recommended                         │
│                                                                                     │
│   🔴 HIGH        Customer      • Major flag in report                               │
│                                • Account review recommended                         │
│                                • Potential escalation trigger                       │
│                                                                                     │
│   🔴 HIGH        Agent         • Mandatory HR review                                │
│                                • Immediate escalation required                      │
│                                                                                     │
│   🔴 CRITICAL    Any           • Immediate escalation                               │
│                                • Human review required                              │
│                                • Legal team notification (if threats)               │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Technology Stack

### Complete Technology Stack Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            TECHNOLOGY STACK                                         │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │  LAYER              TECHNOLOGY           PURPOSE                             │  │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                              │  │
│   │  ORCHESTRATION      ┌───────────────┐   Multi-agent workflow                 │  │
│   │                     │   LangGraph   │   State management                     │  │
│   │                     └───────────────┘   Conditional routing                  │  │
│   │                                                                              │  │
│   │  LLM FRAMEWORK      ┌───────────────┐   LLM interactions                     │  │
│   │                     │  LangChain    │   Prompts & chains                     │  │
│   │                     └───────────────┘   Tool integration                     │  │
│   │                                                                              │  │
│   │  OBSERVABILITY      ┌───────────────┐   Tracing & debugging                  │  │
│   │                     │  LangSmith    │   Evaluation framework                 │  │
│   │                     └───────────────┘   Performance monitoring               │  │
│   │                                                                              │  │
│   │  MODEL CONTROL      ┌───────────────┐   Model routing                        │  │
│   │                     │   LiteLLM     │   Cost management                      │  │
│   │                     └───────────────┘   Fallback chains                      │  │
│   │                                                                              │  │
│   │  STRUCTURED DATA    ┌───────────────┐   Schema validation                    │  │
│   │                     │   Pydantic    │   Type safety                          │  │
│   │                     └───────────────┘   LLM output parsing                   │  │
│   │                                                                              │  │
│   │  TRANSCRIPTION      ┌───────────────┐   Audio to text                        │  │
│   │                     │ Whisper API   │   Speech recognition                   │  │
│   │                     └───────────────┘   (Future Phase)                       │  │
│   │                                                                              │  │
│   │  UI FRAMEWORK       ┌───────────────┐   Web interface                        │  │
│   │                     │  Streamlit    │   Interactive dashboard                │  │
│   │                     └───────────────┘   File upload                          │  │
│   │                                                                              │  │
│   │  CONTAINERIZATION   ┌───────────────┐   Development & deployment             │  │
│   │                     │   Docker      │   Environment consistency              │  │
│   │                     └───────────────┘   HF Spaces deployment                 │  │
│   │                                                                              │  │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### LLM Model Configuration

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         MODEL CONFIGURATION                                         │
│                                                                                     │
│   AGENT               MODEL              RATIONALE                                  │
│   ─────               ─────              ─────────                                  │
│                                                                                     │
│   Input Validation    Rule-based         No LLM needed - deterministic rules        │
│                                                                                     │
│   Intake              Rule-based         Metadata extraction is deterministic       │
│                                                                                     │
│   Transcription       pass-through       Text input doesn't need processing         │
│                       whisper-1          For audio (future)                         │
│                                                                                     │
│   Abuse Detection     GPT-4o-mini        Context-aware content moderation           │
│                       temp=0             Consistent detection                       │
│                                                                                     │
│   Summarization       GPT-4o-mini        Structured output generation               │
│                                          Cost-effective for summaries               │
│                                                                                     │
│   Critic              GPT-4o-mini        Quality evaluation                         │
│                                          Structured critique output                 │
│                                                                                     │
│   QA Scoring          GPT-4o-mini        Performance evaluation                     │
│                                          Consistent rubric application              │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### The Critic Independence Principle

For optimal quality control, the system is designed to support using different model families for generation vs. critique:

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    CRITIC INDEPENDENCE PRINCIPLE                                    │
│                                                                                     │
│   PROBLEM:                                                                          │
│   If Model A generates content, Model A critiquing its own output may               │
│   have blind spots - it might miss the same errors consistently.                    │
│                                                                                     │
│   SOLUTION (Recommended for production):                                            │
│   Use a different model family for critique than for generation.                    │
│                                                                                     │
│                                                                                     │
│   ┌─────────────────┐         ┌─────────────────┐                                   │
│   │    GPT-4        │         │    Claude       │                                   │
│   │  (OpenAI)       │         │  (Anthropic)    │                                   │
│   │                 │         │                 │                                   │
│   │  Generates      │ ───────▶│  Critiques      │                                   │
│   │  Summary        │         │  Summary        │                                   │
│   │                 │         │                 │                                   │
│   └─────────────────┘         └─────────────────┘                                   │
│                                      │                                              │
│                                      ▼                                              │
│                        Catches errors GPT-4 might                                   │
│                        be blind to                                                  │
│                                                                                     │
│   CURRENT IMPLEMENTATION:                                                           │
│   Both use GPT-4o-mini for cost efficiency (development phase)                      │
│                                                                                     │
│   PRODUCTION RECOMMENDATION:                                                        │
│   Summarization: GPT-4 (OpenAI)                                                     │
│   Critic: Claude Sonnet (Anthropic)                                                 │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Evaluation Framework

### LangSmith Integration

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         LANGSMITH OBSERVABILITY                                     │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                              │  │
│   │   CAPABILITY           USE CASE                                              │  │
│   │   ──────────           ────────                                              │  │
│   │                                                                              │  │
│   │   Tracing              Track every agent call, LLM invocation                │  │
│   │                        See complete execution flow                           │  │
│   │                                                                              │  │
│   │   Debugging            Visual debugging of agent handoffs                    │  │
│   │                        Inspect supervisor decisions                          │  │
│   │                        View intermediate states                              │  │
│   │                                                                              │  │
│   │   Monitoring           Latency tracking per agent                            │  │
│   │                        Token usage and costs                                 │  │
│   │                        Error rates                                           │  │
│   │                                                                              │  │
│   │   Replay               Re-run failed executions                              │  │
│   │                        Debug with exact inputs                               │  │
│   │                                                                              │  │
│   │   Datasets             Store test cases                                      │  │
│   │                        Version control for evaluations                       │  │
│   │                                                                              │  │
│   │   Evaluation           Automated quality assessment                          │  │
│   │                        LLM-as-judge evaluators                               │  │
│   │                                                                              │  │
│   │   Feedback             Collect human ratings                                 │  │
│   │                        Track improvements over time                          │  │
│   │                                                                              │  │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│   TRACE METADATA CAPTURED:                                                          │
│   ─────────────────────────                                                         │
│   • Call ID / Session ID                                                            │
│   • Input file type (audio/transcript)                                              │
│   • Agent execution path (actual route taken)                                       │
│   • Revision counts                                                                 │
│   • Model used (including fallbacks)                                                │
│   • Token counts and costs                                                          │
│   • Validation/guardrail results                                                    │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Evaluation Metrics

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         EVALUATION METRICS                                          │
│                                                                                     │
│   EVALUATOR               TYPE            TARGET AGENT      METRIC                  │
│   ─────────               ────            ────────────      ──────                  │
│                                                                                     │
│   Faithfulness            LLM-as-Judge    Summarization     Summary matches         │
│                                                             transcript (0-10)       │
│                                                                                     │
│   Completeness            LLM-as-Judge    Summarization     All key points          │
│                                                             captured (0-10)         │
│                                                                                     │
│   Conciseness             LLM-as-Judge    Summarization     Appropriately           │
│                                                             brief (0-10)            │
│                                                                                     │
│   QA Score Validity       Heuristic       QA Scoring        Scores in 0-10          │
│                                                             range, fields present   │
│                                                                                     │
│   Rubric Consistency      LLM-as-Judge    QA Scoring        Scores align with       │
│                                                             rubric definitions      │
│                                                                                     │
│   Schema Validation       Heuristic       Intake            Pydantic validation     │
│                                                             pass rate               │
│                                                                                     │
│   Latency                 Heuristic       All               Per-agent and total     │
│                                                             pipeline latency        │
│                                                                                     │
│   Routing Efficiency      Custom          Supervisor        Optimal path taken,     │
│                                                             unnecessary loops       │
│                                                             avoided                 │
│                                                                                     │
│   Revision Effectiveness  Custom          Critic Loop       Did revisions           │
│                                                             improve quality?        │
│                                                                                     │
│   Abuse Detection         Custom          Abuse Guardrail   Flagged correctly       │
│   Precision                                                 vs false positives      │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Deployment Architecture

### Hugging Face Spaces Deployment

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                       DEPLOYMENT ARCHITECTURE                                       │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                         HUGGING FACE SPACES                                  │  │
│   │                                                                              │  │
│   │   ┌─────────────────────────────────────────────────────────────────────┐   │   │
│   │   │                     DOCKER CONTAINER                                 │   │  │
│   │   │                                                                      │   │  │
│   │   │   ┌─────────────────────────────────────────────────────────────┐   │   │   │
│   │   │   │  Python 3.11 Runtime                                         │   │   │  │
│   │   │   │                                                              │   │   │  │
│   │   │   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │   │   │   │
│   │   │   │  │  Streamlit   │  │  LangGraph   │  │  Agent Module    │   │   │   │   │
│   │   │   │  │  (Port 7860) │  │  Workflow    │  │  (7 Agents)      │   │   │   │   │
│   │   │   │  └──────────────┘  └──────────────┘  └──────────────────┘   │   │   │   │
│   │   │   │                                                              │   │   │  │
│   │   │   └─────────────────────────────────────────────────────────────┘   │   │   │
│   │   │                                                                      │   │  │
│   │   │   ENVIRONMENT VARIABLES (HF Secrets):                                │   │  │
│   │   │   • OPENAI_API_KEY                                                   │   │  │
│   │   │   • LANGCHAIN_API_KEY                                                │   │  │
│   │   │   • LANGCHAIN_TRACING_V2=true                                        │   │  │
│   │   │   • LANGCHAIN_PROJECT=call-center-assistant                          │   │  │
│   │   │                                                                      │   │  │
│   │   └─────────────────────────────────────────────────────────────────────┘   │   │
│   │                                                                              │  │
│   │   PUBLIC URL: https://huggingface.co/spaces/[username]/call-center-assistant │  │
│   │                                                                              │  │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│   EXTERNAL SERVICES:                                                                │
│   ──────────────────                                                                │
│                                                                                     │
│   ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐              │
│   │    OpenAI API    │    │   LangSmith      │    │  Anthropic API   │              │
│   │                  │    │                  │    │   (optional)     │              │
│   │  • GPT-4o-mini   │    │  • Tracing       │    │  • Claude        │              │
│   │  • Whisper       │    │  • Evaluation    │    │                  │              │
│   └──────────────────┘    └──────────────────┘    └──────────────────┘              │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Dockerfile Configuration

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

# Copy application
COPY . .

# HF Spaces expects port 7860
EXPOSE 7860

# Health check
HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
```

### Development Workflow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         DEVELOPMENT WORKFLOW                                        │
│                                                                                     │
│   ┌─────────────────┐                                                               │
│   │ Local Dev       │                                                               │
│   │ (venv)          │  ← Daily development                                          │
│   │ Fast iteration  │    source venv/bin/activate                                   │
│   │                 │    streamlit run app.py                                       │
│   └────────┬────────┘                                                               │
│            │                                                                        │
│            ▼                                                                        │
│   ┌─────────────────┐                                                               │
│   │ Docker Test     │  ← Before committing                                          │
│   │ (local)         │    docker build -t call-center-assistant .                    │
│   │ Verify build    │    docker run -p 7860:7860 call-center-assistant              │
│   └────────┬────────┘                                                               │
│            │                                                                        │
│            ▼                                                                        │
│   ┌─────────────────┐                                                               │
│   │ Git Push        │  ← Commit & push                                              │
│   │ GitHub/HF       │    git push origin main                                       │
│   └────────┬────────┘                                                               │
│            │                                                                        │
│            ▼                                                                        │
│   ┌─────────────────┐                                                               │
│   │ HF Spaces       │  ← Auto-deploy                                                │
│   │ Production      │    Automatic build on push                                    │
│   └─────────────────┘                                                               │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Future Roadmap

### Phase 6: Workflow Visualization

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    PLANNED: n8n-STYLE WORKFLOW ANIMATION                            │
│                                                                                     │
│   FEATURES:                                                                         │
│   • Real-time node highlighting as agents execute                                   │
│   • Color-coded states: Pending (gray) → Running (amber) → Complete (green)         │
│   • Animated edges showing data flow direction                                      │
│   • Loop visualization for revision cycles                                          │
│   • Interactive: zoom, pan, drag nodes                                              │
│   • Execution history display                                                       │
│                                                                                     │
│   IMPLEMENTATION:                                                                   │
│   • streamlit-flow-component for graph rendering                                    │
│   • LangGraph callbacks for animation updates                                       │
│   • Real-time state synchronization                                                 │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Phase 7: Audio Transcription

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    PLANNED: WHISPER API INTEGRATION                                 │
│                                                                                     │
│   FEATURES:                                                                         │
│   • Audio file upload (.wav, .mp3, .m4a)                                            │
│   • Whisper API transcription                                                       │
│   • Speaker diarization (who said what)                                             │
│   • Timestamp extraction                                                            │
│   • Language detection                                                              │
│                                                                                     │
│   AUDIO VALIDATION:                                                                 │
│   • Duration: 10s - 3600s (1 hour max)                                              │
│   • File integrity checks                                                           │
│   • Speech vs music/silence classification                                          │
│   • Speaker count detection                                                         │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Extended Capabilities

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         FUTURE ENHANCEMENTS                                         │
│                                                                                     │
│   SUPERVISOR AGENT (Full Implementation)                                            │
│   • Dynamic routing based on state analysis                                         │
│   • Multi-model reasoning for routing decisions                                     │
│   • Autonomous escalation decisions                                                 │
│                                                                                     │
│   HUMAN ESCALATION                                                                  │
│   • Terminal node for critical issues                                               │
│   • Integration with ticketing systems                                              │
│   • Real-time alerts for high-severity abuse                                        │
│                                                                                     │
│   MULTI-MODEL STRATEGY                                                              │
│   • Claude for critic (different perspective)                                       │
│   • GPT-4 for summarization (best quality)                                          │
│   • Cost-optimized model routing                                                    │
│   • Automatic fallback chains                                                       │
│                                                                                     │
│   BATCH PROCESSING                                                                  │
│   • Process multiple calls in parallel                                              │
│   • CSV/Excel export of results                                                     │
│   • Aggregate analytics dashboard                                                   │
│                                                                                     │
│   REAL-TIME PROCESSING                                                              │
│   • Live call analysis                                                              │
│   • Streaming transcription                                                         │
│   • Real-time abuse alerts                                                          │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Appendix A: Project File Structure

```
ai_call_center_assistant/
├── app.py                          # Main Streamlit application
├── Dockerfile                      # Docker configuration
├── requirements.txt                # Python dependencies
├── README.md                       # HF Spaces documentation
├── REQUIREMENTS.md                 # Detailed requirements spec
├── DEVELOPMENT.md                  # Developer guide
├── EXECUTION_PLAN.md               # Phase-by-phase plan
├── PHASE3_COMPLETE.md              # Phase 3 summary
├── project_report.md               # This document
│
├── agents/                         # Agent implementations
│   ├── __init__.py
│   ├── abuse_detection_agent.py    # Content moderation
│   ├── critic_agent.py             # Summary quality review
│   ├── input_validation_agent.py   # Input guardrails
│   ├── intake_agent.py             # Metadata extraction
│   ├── qa_scoring_agent.py         # Performance evaluation
│   ├── summarization_agent.py      # Call summary generation
│   ├── supervisor_agent.py         # Workflow routing
│   └── transcription_agent.py      # Text/audio handling
│
├── config/                         # Configuration
│   ├── __init__.py
│   └── settings.py                 # Environment settings
│
├── graph/                          # LangGraph workflows
│   ├── __init__.py
│   ├── workflow.py                 # Phase 3 linear workflow
│   ├── workflow_phase4.py          # Phase 4 with critic loop
│   └── workflow_phase5.py          # Phase 5 with guardrails
│
├── models/                         # Pydantic schemas
│   ├── __init__.py
│   └── schemas.py                  # All data models
│
├── guardrails/                     # Guardrail implementations
│   └── __init__.py
│
├── ui/                             # UI components
│   ├── __init__.py
│   ├── agent_interactions.py       # Agent interaction display
│   ├── progress_tracker.py         # Execution progress
│   └── workflow_visualizer.py      # (Future) Graph animation
│
├── evaluation/                     # Evaluation framework
│   ├── __init__.py
│   ├── langsmith_eval.py           # LangSmith integration
│   ├── run_eval.py                 # Evaluation runner
│   ├── datasets/
│   │   └── test_cases.json         # Test dataset
│   └── evaluators/
│       ├── __init__.py
│       ├── completeness.py
│       ├── faithfulness.py
│       └── qa_validator.py
│
├── data/                           # Sample data
│   └── sample_transcripts/
│       ├── billing_inquiry.txt
│       ├── complaint_with_frustration.txt
│       └── tech_support_unresolved.txt
│
├── test_data/                      # Test data
│   ├── guardrail_tests/            # Guardrail test cases
│   │   ├── README.md
│   │   ├── 01_valid_normal.txt
│   │   ├── 02_too_short.txt
│   │   ├── 03_profanity.txt
│   │   └── ...
│   └── audio/                      # Audio test files
│
├── scripts/                        # Utility scripts
│   ├── setup_local.sh
│   ├── test_docker.sh
│   └── cleanup_docker.sh
│
└── tests/                          # Unit tests
    └── __init__.py
```

---

## Appendix B: API Reference

### Running the Analysis Pipeline

```python
from graph.workflow_phase5 import run_phase5_analysis

# Execute the complete pipeline
result = run_phase5_analysis(
    raw_input="Agent: Hello, thank you for calling...",
    input_type="transcript",
    input_file_path="call.txt"
)

# Access results
print(result["summary"].brief_summary)
print(result["qa_scores"].overall)
print(result["execution_path"])
```

### State Access Patterns

```python
# Validation result
if result["validation_result"].is_valid:
    # Process succeeded
    pass

# Check for abuse
for flag in result["abuse_flags"]:
    print(f"Abuse detected: {flag.abuse_type}, Severity: {flag.severity}")

# Summary details
summary = result["summary"]
print(f"Sentiment: {summary.sentiment.value}")
print(f"Resolution: {summary.resolution_status.value}")

# QA Scores
qa = result["qa_scores"]
print(f"Overall Score: {qa.overall}/10")

# Critique info
if result["summary_critique"]:
    critique = result["summary_critique"]
    print(f"Revisions made: {result['revision_count']}")
```

---

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| **Agent** | An autonomous component that performs a specific task in the pipeline |
| **Guardrail** | A protective mechanism that validates input or flags content issues |
| **LangGraph** | Framework for building stateful multi-agent applications |
| **StateGraph** | LangGraph construct for defining agent workflow as a directed graph |
| **AgentState** | Pydantic model containing all shared data between agents |
| **Conditional Edge** | Graph edge that routes based on runtime state evaluation |
| **Revision Loop** | Pattern where Critic sends Summarization back for improvement |
| **Structured Output** | LLM response parsed into Pydantic model (type-safe) |
| **LangSmith** | Observability platform for LLM applications |
| **Pydantic** | Python library for data validation using type hints |

---

*Document generated: January 25, 2026*  
*Project: AI Call Center Assistant*  
*Phase: 5 (Guardrails Complete)*
