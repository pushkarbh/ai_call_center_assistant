# AI Call Center Assistant - Requirements Document

> **Capstone Project**: Applied Agentic AI for SWEs
> **Version**: 1.1 (True Multi-Agent Architecture)
> **Last Updated**: 2026-01-22

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Agent Architecture](#3-agent-architecture)
4. [Workflow Visualization](#4-workflow-visualization)
5. [Guardrails & Validation](#5-guardrails--validation)
6. [Abuse Detection](#6-abuse-detection)
7. [Model Control Plane](#7-model-control-plane)
8. [LangSmith Integration](#8-langsmith-integration)
9. [Evaluation Framework](#9-evaluation-framework)
10. [Pydantic Structured Outputs](#10-pydantic-structured-outputs)
11. [UI Requirements](#11-ui-requirements)
12. [Docker Architecture](#12-docker-architecture)
13. [Project Structure](#13-project-structure)
14. [Evaluation Criteria](#14-evaluation-criteria)

---

## 1. Project Overview

### Problem Statement

In modern call centers, crucial insights from conversations are often trapped in long transcripts or voice recordings. Manual summaries and quality checks are time-consuming and inconsistent.

### Solution

Build a **true multi-agent system** that converts call recordings/transcripts into structured summaries and QA insights, with:

- **Autonomous agent orchestration** - Agents decide what happens next
- **Self-correction loops** - Agents critique and improve each other's work
- **Dynamic routing** - Supervisor agent routes based on state and reasoning
- **Real-time workflow visualization** - n8n-style animation showing execution path
- **Abuse detection and flagging**
- **Input validation guardrails**
- **Production-grade observability**

### Business Value

| Capability | Benefit |
|------------|---------|
| Automated Insight Extraction | Rapidly summarize calls without manual effort |
| QA Monitoring at Scale | Score service quality using LLM agents |
| Consistency & Compliance | Standardize evaluations across interactions |
| Voice-to-Insights Pipeline | Convert audio into structured data for decision-making |
| Abuse Detection | Protect staff and flag problematic interactions |
| Self-Correction | Higher quality outputs through agent collaboration |

---

## 2. Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Orchestration** | LangGraph | Multi-agent workflow, state management, conditional routing |
| **LLM Framework** | LangChain | LLM interactions, prompts, chains |
| **Observability** | LangSmith | Tracing, debugging, monitoring, evaluation (Day 1) |
| **Model Control Plane** | LiteLLM | Model fallback, cost management, routing |
| **Transcription** | Whisper API | Audio to text conversion |
| **Structured Output** | Pydantic | Schema validation, typed LLM responses |
| **UI Framework** | Streamlit | Web interface |
| **Workflow Animation** | streamlit-flow-component | n8n-style agent visualization |
| **Containerization** | Docker + docker-compose | Development & deployment (Day 1) |
| **Memory/Cache** | Redis | Call context, session state |
| **Guardrails** | Guardrails AI + OpenAI Moderation | Input validation, abuse detection |

### Why These Choices

- **LangGraph over CrewAI**: Better state management, native LangChain integration, superior conditional routing for true multi-agent behavior
- **Streamlit over Gradio**: Better layout flexibility for multi-section dashboard, easier agent status visualization
- **LiteLLM**: Unified API for multiple LLM providers with automatic fallback
- **Pydantic**: Forces structured output from LLMs, validates data, enables type-safe state management
- **Docker from Day 1**: Consistent environments, easy deployment, production-ready
- **LangSmith from Day 1**: Full observability, evaluation framework, debugging

---

## 3. Agent Architecture

### What Makes This a True Multi-Agent System

| Characteristic | Our Implementation |
|----------------|-------------------|
| **Dynamic Routing** | Supervisor Agent decides which agent to invoke based on current state |
| **Agent Autonomy** | Agents reason about their outputs and can request re-processing |
| **Inter-Agent Communication** | Critic Agent reviews Summarization Agent's work |
| **Self-Correction Loops** | Summary can be revised multiple times based on critique |
| **Conditional Branching** | Different paths based on abuse detection, quality scores |
| **Escalation Decisions** | Agents can autonomously decide to escalate to humans |

### Agent Flow Diagram (True Multi-Agent)

```
                              ┌─────────────────┐
                              │   Supervisor    │◀─────────────────────────────┐
                              │     Agent       │                              │
                              └────────┬────────┘                              │
                                       │                                       │
                                       │ (decides next agent)                  │
                                       │                                       │
         ┌───────────┬─────────────────┼─────────────────┬───────────┐         │
         ▼           ▼                 ▼                 ▼           ▼         │
┌─────────────┐ ┌──────────┐   ┌─────────────┐   ┌──────────┐ ┌───────────┐    │
│   Intake    │ │Transcribe│   │ Summarize   │   │ QA Score │ │  Abuse    │    │
│   Agent     │ │  Agent   │   │   Agent     │   │  Agent   │ │  Review   │    │
└──────┬──────┘ └────┬─────┘   └──────┬──────┘   └────┬─────┘ └─────┬─────┘    │
       │             │                │               │             │          │
       │             │                ▼               │             │          │
       │             │         ┌─────────────┐        │             │          │
       │             │         │   Summary   │        │             │          │
       │             │         │   Critic    │        │             │          │
       │             │         └──────┬──────┘        │             │          │
       │             │                │               │             │          │
       │             │                │ (needs revision?)           │          │
       │             │                │               │             │          │
       │             │         ┌──────┴──────┐        │             │          │
       │             │         │             │        │             │          │
       │             │    [YES: loop back]   │        │             │          │
       │             │         │        [NO: continue]│             │          │
       │             │         ▼             │        │             │          │
       │             │   ┌──────────┐        │        │             │          │
       │             │   │Summarize │        │        │             │          │
       │             │   │(retry)   │        │        │             │          │
       │             │   └──────────┘        │        │             │          │
       │             │                       │        │             │          │
       └─────────────┴───────────────────────┴────────┴─────────────┘          │
                                       │                                       │
                                       │ (all return to supervisor)            │
                                       └───────────────────────────────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │     Human       │
                              │   Escalation    │ (when critical issues detected)
                              └─────────────────┘
```

### Agent Responsibilities

| Agent | Type | Responsibility | Autonomy |
|-------|------|----------------|----------|
| **Input Validation Guardrail** | Guardrail | Validate file format, detect content type, check duration | Reject/confirm decisions |
| **Supervisor Agent** | Orchestrator | Analyze state, decide which agent to invoke next, handle completion | Full routing autonomy |
| **Intake Agent** | Worker | Extract metadata, validate schema, prepare for processing | Reports to Supervisor |
| **Transcription Agent** | Worker | Convert audio to text via Whisper; pass-through if transcript provided | Reports to Supervisor |
| **Summarization Agent** | Worker | Generate structured summary, key points, action items | Can be asked to retry |
| **Summary Critic Agent** | Reviewer | Review summary for faithfulness, completeness; request revisions | Decides if revision needed |
| **QA Scoring Agent** | Worker | Evaluate tone, empathy, professionalism, resolution using rubric | Reports to Supervisor |
| **Abuse Review Agent** | Specialist | Deep analysis of flagged content, severity assessment | Can trigger escalation |
| **Human Escalation** | Terminal | Handle critical cases requiring human intervention | Terminal node |

### Supervisor Agent Logic

```python
SUPERVISOR_PROMPT = """
You are orchestrating a call center analysis pipeline.

Current State:
- Has transcript: {has_transcript}
- Has summary: {has_summary}
- Summary quality: {summary_quality}
- Summary revision count: {revision_count}
- Has QA scores: {has_qa_scores}
- Abuse detected: {abuse_detected}
- Abuse severity: {abuse_severity}

Available agents:
1. intake_agent - Extract metadata (if not done)
2. transcription_agent - Convert audio to text (if needed)
3. summarization_agent - Generate call summary
4. summary_critic_agent - Review summary quality
5. qa_scoring_agent - Score call quality
6. abuse_review_agent - Deep analysis of flagged content
7. human_escalation - Escalate to human reviewer
8. COMPLETE - Finish processing

Rules:
- Always run intake first
- Transcription only needed for audio input
- After summarization, always run critic
- If critic says revision needed AND revision_count < 3, run summarization again
- If abuse_severity is HIGH or CRITICAL, run abuse_review
- If abuse_review recommends escalation, go to human_escalation
- When all required outputs exist and quality is acceptable, return COMPLETE

Based on the current state, which agent should run next?
Reason step by step, then output your decision.
"""
```

### LangGraph Implementation

```python
from langgraph.graph import StateGraph, END
from typing import Literal

def build_workflow():
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("supervisor", supervisor_agent)
    graph.add_node("intake", intake_agent)
    graph.add_node("transcription", transcription_agent)
    graph.add_node("summarization", summarization_agent)
    graph.add_node("summary_critic", summary_critic_agent)
    graph.add_node("qa_scoring", qa_scoring_agent)
    graph.add_node("abuse_review", abuse_review_agent)
    graph.add_node("human_escalation", human_escalation_node)

    # Entry point
    graph.set_entry_point("supervisor")

    # Supervisor routes to appropriate agent
    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "intake": "intake",
            "transcription": "transcription",
            "summarization": "summarization",
            "summary_critic": "summary_critic",
            "qa_scoring": "qa_scoring",
            "abuse_review": "abuse_review",
            "human_escalation": "human_escalation",
            "COMPLETE": END
        }
    )

    # All worker agents return to supervisor
    for agent in ["intake", "transcription", "summarization", "qa_scoring", "abuse_review"]:
        graph.add_edge(agent, "supervisor")

    # Critic has conditional routing (revision loop)
    graph.add_conditional_edges(
        "summary_critic",
        lambda state: "summarization" if state.needs_revision and state.revision_count < 3 else "supervisor",
        {
            "summarization": "summarization",
            "supervisor": "supervisor"
        }
    )

    # Human escalation is terminal
    graph.add_edge("human_escalation", END)

    return graph.compile()
```

### Self-Correction: Summary Critique Loop

```python
class SummaryCriticAgent:
    """Reviews summaries and requests revisions if needed"""

    async def run(self, state: AgentState) -> AgentState:
        critique_prompt = """
        Review this call summary for quality:

        TRANSCRIPT:
        {transcript}

        SUMMARY:
        {summary}

        Evaluate:
        1. Faithfulness: Does the summary accurately reflect the transcript? (no hallucinations)
        2. Completeness: Are all key points, action items, and customer concerns captured?
        3. Conciseness: Is it appropriately brief without losing important details?

        Score each 1-10 and provide specific feedback.
        If any score is below 7, request a revision with specific instructions.

        Output JSON:
        {{
            "faithfulness_score": int,
            "completeness_score": int,
            "conciseness_score": int,
            "needs_revision": bool,
            "revision_instructions": str or null,
            "feedback": str
        }}
        """

        result = await self.llm.invoke(critique_prompt.format(
            transcript=state.transcript.full_text,
            summary=state.summary.model_dump_json()
        ))

        return state.copy(update={
            "summary_critique": result,
            "needs_revision": result.needs_revision,
            "revision_count": state.revision_count + (1 if result.needs_revision else 0)
        })
```

---

## 4. Workflow Visualization

### Requirements

- **n8n-style animated graph** showing agent workflow
- **Real-time node highlighting** as agents execute
- **Dynamic path visualization** - shows actual execution path, not just static graph
- **Loop visualization** - clearly shows when agents retry/loop
- **Color-coded states**:
  - Gray: Pending (not yet visited)
  - Amber/Yellow: Running (currently executing)
  - Green: Complete (successfully finished)
  - Red: Error (failed)
  - Blue: Revisiting (running again after loop)
- **Animated edges** showing data flow direction (pulsing dots)
- **Interactive**: Zoom, pan, drag nodes
- **Execution history**: Shows the path taken through the graph

### Animation for Multi-Agent Dynamic Routing

Unlike a linear pipeline, our multi-agent system has:
- Conditional paths (Supervisor decides routing)
- Loops (Critic → Summarization → Critic)
- Parallel possibilities (though executed sequentially)

The animation captures this by:

```python
class AnimationState:
    """Tracks animation state for workflow visualization"""
    agent_states: dict[str, str]      # node_id -> "pending"|"running"|"complete"|"error"
    active_edges: set[tuple[str,str]] # Currently animated edges
    execution_path: list[str]         # Ordered list of visited nodes
    edge_history: list[tuple[str,str]] # All edges traversed
    retry_counts: dict[str, int]      # How many times each node ran
    current_decision: str | None      # Supervisor's current reasoning
```

### Animation Events

| Event | Visual Effect |
|-------|---------------|
| Supervisor analyzing | Supervisor node pulses, shows "Deciding..." |
| Supervisor decides | Edge to chosen agent animates, decision shown in tooltip |
| Agent starts | Node turns amber, label shows "Running..." |
| Agent completes | Node turns green |
| Agent errors | Node turns red, error icon |
| Critic requests revision | Edge back to Summarization animates (different color) |
| Same node runs again | Node shows retry count badge, turns blue then amber |
| Return to Supervisor | Edge animates back to Supervisor |
| Processing complete | All visited nodes stay green, path highlighted |

### Implementation

```python
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge

class WorkflowVisualizer:
    def __init__(self):
        self.node_positions = {
            "supervisor": (300, 0),
            "intake": (100, 150),
            "transcription": (200, 150),
            "summarization": (300, 150),
            "summary_critic": (300, 300),
            "qa_scoring": (400, 150),
            "abuse_review": (500, 150),
            "human_escalation": (500, 300),
        }

    def get_node_style(self, state: str, retry_count: int = 0) -> dict:
        base_styles = {
            "pending": {"background": "#6b7280", "color": "white"},
            "running": {"background": "#f59e0b", "color": "white"},
            "complete": {"background": "#22c55e", "color": "white"},
            "error": {"background": "#ef4444", "color": "white"},
            "revisiting": {"background": "#3b82f6", "color": "white"},
        }
        style = base_styles.get(state, base_styles["pending"])
        if retry_count > 1:
            style["border"] = "3px solid #8b5cf6"  # Purple border for retries
        return style

    def render(self, animation_state: AnimationState):
        nodes = []
        for node_id, pos in self.node_positions.items():
            state = animation_state.agent_states.get(node_id, "pending")
            retry_count = animation_state.retry_counts.get(node_id, 0)

            label = self.get_node_label(node_id)
            if retry_count > 1:
                label += f" (x{retry_count})"
            if state == "running":
                label += " ⏳"

            nodes.append(StreamlitFlowNode(
                id=node_id,
                pos=pos,
                data={"label": label},
                style=self.get_node_style(state, retry_count)
            ))

        edges = []
        # Define all possible edges
        edge_definitions = [
            ("supervisor", "intake"),
            ("supervisor", "transcription"),
            ("supervisor", "summarization"),
            ("supervisor", "summary_critic"),
            ("supervisor", "qa_scoring"),
            ("supervisor", "abuse_review"),
            ("supervisor", "human_escalation"),
            ("intake", "supervisor"),
            ("transcription", "supervisor"),
            ("summarization", "supervisor"),
            ("summarization", "summary_critic"),
            ("summary_critic", "supervisor"),
            ("summary_critic", "summarization"),  # Revision loop
            ("qa_scoring", "supervisor"),
            ("abuse_review", "supervisor"),
            ("abuse_review", "human_escalation"),
        ]

        for source, target in edge_definitions:
            is_active = (source, target) in animation_state.active_edges
            was_traversed = (source, target) in animation_state.edge_history
            is_revision_loop = source == "summary_critic" and target == "summarization"

            edges.append(StreamlitFlowEdge(
                id=f"{source}-{target}",
                source=source,
                target=target,
                animated=is_active,
                style={
                    "stroke": "#8b5cf6" if is_revision_loop else ("#22c55e" if was_traversed else "#6b7280"),
                    "strokeWidth": 3 if is_active else (2 if was_traversed else 1),
                }
            ))

        streamlit_flow(
            "workflow",
            nodes,
            edges,
            height=500,
            fit_view=True,
            show_minimap=True
        )
```

### LangGraph Callbacks for Animation

```python
from langchain_core.callbacks import BaseCallbackHandler

class AnimationCallback(BaseCallbackHandler):
    """Callback handler that updates UI animation state"""

    def __init__(self, animation_state: AnimationState):
        self.animation_state = animation_state

    def on_chain_start(self, serialized, inputs, **kwargs):
        node_name = serialized.get("name", "unknown")

        # Update state
        self.animation_state.agent_states[node_name] = "running"
        self.animation_state.execution_path.append(node_name)
        self.animation_state.retry_counts[node_name] = \
            self.animation_state.retry_counts.get(node_name, 0) + 1

        # Update active edge (from previous node)
        if len(self.animation_state.execution_path) > 1:
            prev_node = self.animation_state.execution_path[-2]
            edge = (prev_node, node_name)
            self.animation_state.active_edges = {edge}
            self.animation_state.edge_history.append(edge)

        # Trigger UI refresh
        st.session_state.animation_state = self.animation_state
        st.rerun()

    def on_chain_end(self, outputs, **kwargs):
        node_name = self.animation_state.execution_path[-1]
        self.animation_state.agent_states[node_name] = "complete"
        self.animation_state.active_edges = set()

        st.session_state.animation_state = self.animation_state
        st.rerun()

    def on_chain_error(self, error, **kwargs):
        node_name = self.animation_state.execution_path[-1]
        self.animation_state.agent_states[node_name] = "error"
        self.animation_state.active_edges = set()

        st.session_state.animation_state = self.animation_state
        st.rerun()
```

### Example Animation Sequence

User uploads a call recording. The animation shows:

```
1. [Supervisor] lights up amber → "Deciding: need to process new input"

2. Edge Supervisor→Intake animates
   [Intake] turns amber → extracts metadata → turns green

3. Edge Intake→Supervisor animates
   [Supervisor] lights up → "Deciding: have audio, need transcription"

4. Edge Supervisor→Transcription animates
   [Transcription] turns amber → transcribes → turns green

5. Edge Transcription→Supervisor animates
   [Supervisor] → "Deciding: have transcript, need summary"

6. Edge Supervisor→Summarization animates
   [Summarization] turns amber → generates summary → turns green

7. Edge Summarization→Supervisor animates
   [Supervisor] → "Deciding: have summary, need critique"

8. Edge Supervisor→SummaryCritic animates
   [SummaryCritic] turns amber → reviews → "needs revision" → turns green

9. Edge SummaryCritic→Summarization animates (PURPLE - revision loop!)
   [Summarization] shows "(x2)", turns blue then amber → revises → turns green

10. Edge Summarization→Supervisor animates
    [Supervisor] → "Deciding: revised summary, need critique again"

11. Edge Supervisor→SummaryCritic animates
    [SummaryCritic] → reviews → "looks good now" → turns green

12. Edge SummaryCritic→Supervisor animates
    [Supervisor] → "Deciding: summary approved, need QA scores"

13. Edge Supervisor→QAScoring animates
    [QAScoring] turns amber → scores → turns green

14. Edge QAScoring→Supervisor animates
    [Supervisor] → "Deciding: all complete, finishing"

15. [Supervisor] turns green
    Graph shows: Supervisor, Intake, Transcription, Summarization(x2), SummaryCritic(x2), QAScoring all green
    Traversed edges highlighted
```

---

## 5. Guardrails & Validation

### Input Validation Layers

| Layer | Check | Action |
|-------|-------|--------|
| **1. File Format** | Allowed extensions (.wav, .mp3, .m4a, .txt, .json) | Hard reject |
| **2. File Integrity** | Not corrupted, not empty | Hard reject |
| **3. Duration** | 10s - 3600s (1 hour) | Warn if outside range |
| **4. Audio Classification** | Speech vs Music vs Silence | Reject music |
| **5. Speaker Count** | Detect number of speakers | Warn if single speaker |
| **6. Language Detection** | Identify spoken language | Warn if non-English |
| **7. Content Classification** | Call vs Podcast vs Audiobook vs Other | User confirmation if uncertain |

### Validation Result Schema

```python
from pydantic import BaseModel

class InputValidationResult(BaseModel):
    is_valid: bool
    confidence: float              # 0.0 - 1.0
    input_type_detected: str       # "call_recording", "music", "podcast", etc.
    issues: list[str]
    requires_user_confirmation: bool
    rejection_reason: str | None
```

### User Confirmation Flow

1. **Hard Reject** (confidence < 0.5): Show error, block processing
2. **User Confirmation** (0.5 < confidence < 0.8): Show warning with details, let user decide
3. **Auto-Accept** (confidence > 0.8): Proceed with processing

### Audio Classification

Options:
- Whisper's built-in speech detection (low confidence = likely not speech)
- Hugging Face `MIT/ast-finetuned-audioset` model for audio classification
- Custom speech/music classifier

---

## 6. Abuse Detection

### Abuse Types

| Type | Description | Examples |
|------|-------------|----------|
| **Profanity** | Offensive language, swearing | Explicit words, slurs |
| **Threat** | Explicit or implied threats | "I'll sue you", "I'll come to your office" |
| **Harassment** | Bullying, intimidation | Repeated insults, personal attacks |
| **Discrimination** | Race, gender, age-based | Slurs, stereotyping |

### Severity Levels

| Severity | Description | Action |
|----------|-------------|--------|
| **Low** | Mild frustration, minor profanity | Flag in report |
| **Medium** | Repeated profanity, raised aggression | Flag prominently |
| **High** | Threats, discrimination, severe harassment | Trigger Abuse Review Agent |
| **Critical** | Violence threats, legal threats | Abuse Review → Human Escalation |

### Abuse Flag Schema

```python
from pydantic import BaseModel
from enum import Enum

class AbuseType(str, Enum):
    PROFANITY = "profanity"
    THREAT = "threat"
    HARASSMENT = "harassment"
    DISCRIMINATION = "discrimination"

class AbuseSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AbuseFlag(BaseModel):
    detected: bool
    speaker: str                    # "customer" | "agent" | "both"
    abuse_type: list[AbuseType]
    severity: AbuseSeverity
    evidence: list[str]             # Quoted excerpts
    recommended_action: str
    requires_escalation: bool
```

### Detection Implementation

**Hybrid Approach**:

1. **Fast First-Pass**: OpenAI Moderation API (free, fast)
2. **Detailed Analysis**: Custom LLM prompt for context-aware detection

```python
class AbuseDetectionGuard:
    async def check(self, transcript: str) -> AbuseFlag:
        # Step 1: Fast moderation check
        moderation = openai.moderations.create(input=transcript)

        if moderation.results[0].flagged:
            # Step 2: Detailed LLM analysis for context
            return await self.analyze_with_llm(transcript)

        return AbuseFlag(detected=False, ...)
```

### Multi-Agent Integration

When abuse is detected:
1. **Low/Medium**: Flagged in output, processing continues normally
2. **High**: Supervisor routes to Abuse Review Agent for deeper analysis
3. **Critical**: Abuse Review Agent triggers Human Escalation node

```python
# In Supervisor logic
if state.abuse_flag and state.abuse_flag.severity in ["high", "critical"]:
    if not state.abuse_review_complete:
        return "abuse_review"  # Route to specialist agent
```

### Handling by Speaker

| Speaker | Low/Medium Severity | High/Critical Severity |
|---------|---------------------|------------------------|
| **Customer** | Flag in report, note in CRM | Supervisor notification, potential account flag |
| **Agent** | Flag for coaching | Mandatory HR review, immediate escalation |

---

## 7. Model Control Plane & Multi-LLM Strategy

### Why Multiple LLMs

Using different LLMs for different tasks provides:

| Benefit | Description |
|---------|-------------|
| **Bias Reduction** | Critic uses different model than generator for independent judgment |
| **Cost Optimization** | Cheaper models for simple tasks |
| **Redundancy** | Fallback chains across providers |
| **Best-Fit Selection** | Each model's strengths matched to tasks |

### The Critic Independence Principle

> If Model A generates content, Model A critiquing its own output may have blind spots.

**Solution**: Use a different model family for critique than for generation.

```
GPT-4 generates summary ───▶ Claude critiques it
                                    │
                                    ▼
                            Catches errors GPT-4
                            might be blind to
```

### Task-to-Model Mapping

| Agent | Primary Model | Fallback | Rationale |
|-------|---------------|----------|-----------|
| **Supervisor** | GPT-4 | Claude Sonnet | Strong reasoning for routing |
| **Intake** | GPT-4o-mini | Claude Haiku | Simple extraction, cost-sensitive |
| **Transcription** | Whisper API | Deepgram | Dedicated ASR |
| **Summarization** | GPT-4 | Claude Sonnet | Core task, needs quality |
| **Summary Critic** | **Claude Sonnet** | GPT-4 | **Different family for independence** |
| **QA Scoring** | GPT-4 | Claude Sonnet | Structured evaluation |
| **Abuse Detection** | Claude Sonnet | GPT-4 | Claude has strong safety training |
| **Abuse Review** | **GPT-4** | Claude Opus | **Different from initial detection** |

### Configuration

```yaml
# config/litellm_config.yaml
model_list:
  # Supervisor - strong reasoning
  - model_name: "supervisor"
    litellm_params:
      model: "gpt-4"
      api_key: "${OPENAI_API_KEY}"

  # Summarization - core generation (OpenAI family)
  - model_name: "summarization"
    litellm_params:
      model: "gpt-4"
      api_key: "${OPENAI_API_KEY}"

  # Summary Critic - DIFFERENT family (Anthropic) for independence
  - model_name: "summary_critic"
    litellm_params:
      model: "claude-3-sonnet-20240229"
      api_key: "${ANTHROPIC_API_KEY}"

  # Simple tasks - cheaper model
  - model_name: "intake"
    litellm_params:
      model: "gpt-4o-mini"
      api_key: "${OPENAI_API_KEY}"

  # QA Scoring
  - model_name: "qa_scoring"
    litellm_params:
      model: "gpt-4"
      api_key: "${OPENAI_API_KEY}"

  # Abuse Detection - Claude (safety-focused)
  - model_name: "abuse_detection"
    litellm_params:
      model: "claude-3-sonnet-20240229"
      api_key: "${ANTHROPIC_API_KEY}"

# Fallback chains (cross-family for redundancy)
fallbacks:
  supervisor: ["claude-3-sonnet-20240229"]
  summarization: ["claude-3-sonnet-20240229"]
  summary_critic: ["gpt-4"]
  intake: ["claude-3-haiku-20240307"]
  qa_scoring: ["claude-3-sonnet-20240229"]
  abuse_detection: ["gpt-4"]

router_settings:
  num_retries: 2
  timeout: 30
  allowed_fails: 1
```

### Implementation

```python
# config/models.py
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

class ModelRegistry:
    """Centralized model management with task-based routing"""

    def __init__(self):
        self.models = {
            "supervisor": ChatOpenAI(model="gpt-4"),
            "summarization": ChatOpenAI(model="gpt-4"),
            "summary_critic": ChatAnthropic(model="claude-3-sonnet-20240229"),  # Different!
            "intake": ChatOpenAI(model="gpt-4o-mini"),
            "qa_scoring": ChatOpenAI(model="gpt-4"),
            "abuse_detection": ChatAnthropic(model="claude-3-sonnet-20240229"),
        }

    def get_model(self, task: str):
        return self.models.get(task)

# Usage in agents
registry = ModelRegistry()

class SummarizationAgent:
    def __init__(self):
        self.llm = registry.get_model("summarization")  # GPT-4

class SummaryCriticAgent:
    def __init__(self):
        self.llm = registry.get_model("summary_critic")  # Claude - different!
```

### Cost Optimization

| Task | Model | Approx Cost | Justification |
|------|-------|-------------|---------------|
| Intake | GPT-4o-mini | ~$0.15/1M tokens | Simple extraction |
| Summarization | GPT-4 | ~$30/1M tokens | Quality critical |
| Critic | Claude Sonnet | ~$15/1M tokens | Independent review |
| QA Scoring | GPT-4 | ~$30/1M tokens | Nuanced evaluation |

### Observability

LangSmith tracks which model was used for each step:

```python
# Each agent logs model usage
return state.update(
    summary=result,
    models_used=state.models_used + [self.llm.model_name]
)
```

---

## 8. LangSmith Integration

### Setup (Day 1 Requirement)

```python
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "call-center-assistant"
os.environ["LANGCHAIN_API_KEY"] = "..."
```

### Capabilities Used

| Feature | Use Case |
|---------|----------|
| **Tracing** | Track every agent call, LLM invocation, chain execution |
| **Debugging** | Visual debugging of agent handoffs, see Supervisor decisions |
| **Monitoring** | Latency, token usage, costs |
| **Replay** | Replay failed runs for debugging |
| **Datasets** | Store test cases for evaluation |
| **Evaluation** | Automated quality assessment |
| **Feedback** | Collect human ratings on outputs |

### Multi-Agent Tracing

LangSmith captures:
- Supervisor decision reasoning
- Which agents were called and in what order
- Loop iterations (revision cycles)
- Time spent in each agent
- Token usage per agent

### Trace Metadata

Each run includes:
- Call ID / Session ID
- Input file type (audio/transcript)
- Agent execution path (actual route taken)
- Revision counts
- Model used (including fallbacks)
- Token counts and costs
- Validation/guardrail results

---

## 9. Evaluation Framework

### Test Dataset

Create a dataset of 10-15 annotated examples with:
- Input transcripts
- Expected summaries
- Expected QA scores
- Expected abuse flags

### Evaluators

| Evaluator | Type | Target Agent | Metric |
|-----------|------|--------------|--------|
| **Faithfulness** | LLM-as-Judge | Summarization | Does summary match transcript? (0-10) |
| **Completeness** | LLM-as-Judge | Summarization | Are all key points captured? (0-10) |
| **Conciseness** | LLM-as-Judge | Summarization | Is summary appropriately brief? (0-10) |
| **QA Score Validity** | Heuristic | QA Scoring | All scores in 0-10 range, required fields present |
| **Rubric Consistency** | LLM-as-Judge | QA Scoring | Do scores align with rubric definitions? |
| **Schema Validation** | Heuristic | Intake | Pydantic model validation pass rate |
| **Latency** | Heuristic | All | Per-agent and total pipeline latency |
| **Routing Efficiency** | Custom | Supervisor | Optimal path taken, unnecessary loops avoided |
| **Revision Effectiveness** | Custom | Critic Loop | Did revisions improve quality scores? |
| **Abuse Detection Precision** | Custom | Abuse Guardrail | Flagged correctly vs false positives |

### Running Evaluations

```python
from langsmith.evaluation import evaluate

results = evaluate(
    lambda inputs: graph.invoke(inputs),
    data="call-center-eval",
    evaluators=[
        faithfulness_evaluator,
        completeness_evaluator,
        qa_score_evaluator,
        latency_evaluator,
        routing_efficiency_evaluator
    ],
    experiment_prefix="v1.0"
)
```

### Evaluation Dashboard

LangSmith provides:
- Experiment comparison (v1 vs v2)
- Score distributions
- Failure analysis
- Regression detection
- Agent-level metrics

---

## 10. Pydantic Structured Outputs

### Why Pydantic

Pydantic solves the critical problem: **LLMs return unstructured text, but your application needs structured, validated data.**

| Without Pydantic | With Pydantic |
|------------------|---------------|
| LLM returns "The call went well" | LLM returns `{"sentiment": "positive", "resolution_status": "resolved", ...}` |
| QA score might be "8/10" or "eight" | Always `float` between 0-10 |
| Missing fields crash your app | Validation error before processing |
| Manual JSON parsing everywhere | Automatic serialization |
| No IDE autocomplete | Full type hints and autocomplete |
| Hope LLM follows format | Enforce LLM follows format |

### Core Schemas

```python
# models/schemas.py

from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime
from typing import Optional

# --- Enums ---

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class ResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    ESCALATED = "escalated"

# --- Input/Output Schemas ---

class CallMetadata(BaseModel):
    call_id: str
    timestamp: datetime
    duration_seconds: float
    caller_id: Optional[str] = None
    agent_id: Optional[str] = None
    input_type: str  # "audio" | "transcript"

class TranscriptSegment(BaseModel):
    speaker: str
    text: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class TranscriptData(BaseModel):
    segments: list[TranscriptSegment]
    full_text: str
    language: str = "en"
    confidence: float = Field(ge=0.0, le=1.0)

class CallSummary(BaseModel):
    """Structured summary generated by Summarization Agent"""
    brief_summary: str = Field(description="2-3 sentence overview")
    key_points: list[str] = Field(description="3-5 bullet points")
    action_items: list[str] = Field(description="Follow-up tasks, can be empty")
    customer_intent: str = Field(description="What the customer wanted")
    resolution_status: ResolutionStatus
    topics: list[str] = Field(description="Main topics discussed")
    sentiment: Sentiment

class QAScores(BaseModel):
    """Quality scores generated by QA Scoring Agent"""
    empathy: float = Field(ge=0, le=10)
    professionalism: float = Field(ge=0, le=10)
    resolution: float = Field(ge=0, le=10)
    tone: float = Field(ge=0, le=10)
    comments: str = Field(description="Evaluator notes")

    @validator('empathy', 'professionalism', 'resolution', 'tone', pre=True)
    def round_scores(cls, v):
        if isinstance(v, (int, float)):
            return round(float(v), 1)
        return v

    @property
    def overall(self) -> float:
        """Weighted average of all scores"""
        return round((self.empathy + self.professionalism +
                     self.resolution + self.tone) / 4, 1)

class SummaryCritique(BaseModel):
    """Output from Summary Critic Agent"""
    faithfulness_score: int = Field(ge=1, le=10)
    completeness_score: int = Field(ge=1, le=10)
    conciseness_score: int = Field(ge=1, le=10)
    needs_revision: bool
    revision_instructions: Optional[str] = None
    feedback: str

class FinalReport(BaseModel):
    """Complete output of the pipeline"""
    metadata: CallMetadata
    transcript: TranscriptData
    summary: CallSummary
    qa_scores: QAScores
    abuse_flags: list[AbuseFlag] = []
    processing_time_ms: float
    models_used: list[str]
    revision_count: int = 0
    execution_path: list[str] = []  # Agents that ran
```

### LangGraph State Schema

```python
from pydantic import BaseModel
from typing import Optional

class AgentState(BaseModel):
    """State passed between agents in LangGraph"""

    # Input
    input_file_path: str
    input_type: str  # "audio" | "transcript"

    # Validation
    validation_result: Optional[InputValidationResult] = None
    user_confirmed: bool = False

    # Processing outputs
    metadata: Optional[CallMetadata] = None
    transcript: Optional[TranscriptData] = None
    summary: Optional[CallSummary] = None
    summary_critique: Optional[SummaryCritique] = None
    qa_scores: Optional[QAScores] = None
    abuse_flags: list[AbuseFlag] = []
    abuse_review_complete: bool = False

    # Control flow
    current_agent: str = "supervisor"
    needs_revision: bool = False
    revision_count: int = 0
    execution_path: list[str] = []
    errors: list[str] = []

    # Final output
    final_report: Optional[FinalReport] = None

    class Config:
        # Allow arbitrary types for flexibility
        arbitrary_types_allowed = True
```

### Using with LangChain

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# LangChain's with_structured_output handles Pydantic automatically
llm = ChatOpenAI(model="gpt-4").with_structured_output(CallSummary)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a call center analyst. Summarize the following transcript."),
    ("human", "{transcript}")
])

chain = prompt | llm

# Returns a validated CallSummary object
summary: CallSummary = chain.invoke({"transcript": transcript})

# Guaranteed structure - IDE autocomplete works
print(summary.brief_summary)      # str
print(summary.key_points)         # list[str]
print(summary.resolution_status)  # ResolutionStatus enum
print(summary.sentiment.value)    # "positive" | "neutral" | "negative"
```

---

## 11. UI Requirements

### Main Sections

#### 1. File Upload Section
- Accept audio files: `.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`
- Accept transcript files: `.txt`, `.json`
- Drag-and-drop interface
- File validation feedback

#### 2. Workflow Visualization Section
- **n8n-style animated graph** (see Section 4)
- Real-time agent status updates
- Dynamic path visualization
- Loop/retry indicators
- Color-coded nodes (pending/running/complete/error)
- Animated edges showing data flow
- Supervisor decision display

#### 3. Results Dashboard

| Panel | Content |
|-------|---------|
| **Transcript** | Full text with speaker labels (if diarized) |
| **Summary** | Structured summary with key points, action items |
| **QA Scores** | Rubric breakdown (empathy, professionalism, resolution, tone) |
| **Tags/Highlights** | Entities, topics, sentiment indicators |
| **Abuse Flags** | Any detected issues with evidence and recommended actions |

#### 4. Debug/Trace View (Collapsible)
- Link to LangSmith trace
- Token usage per agent
- Latency breakdown
- Execution path (agents visited in order)
- Revision count
- Model used (including fallbacks)

### Validation UI Flows

#### Hard Reject
```
❌ File rejected: [reason]

   [Try Another File]
```

#### User Confirmation Required
```
⚠️ We detected some potential issues with this file:
   • Only one speaker detected - may not be a conversation
   • Content appears to be: podcast

   Confidence: 65%

   [✓ Proceed Anyway]  [✗ Cancel]
```

#### Abuse Escalation Alert
```
⚠️ ESCALATION REQUIRED

Speaker: Agent
Severity: HIGH
Type: Harassment

Evidence:
> "If you can't understand simple instructions..."
> "This is the third time I'm explaining this to you."

[Escalate to Supervisor]  [View Full Context]
```

---

## 12. Docker Architecture & Deployment

### Deployment Target: Hugging Face Spaces

We deploy to **Hugging Face Spaces with Docker** from day one, building incrementally.

**Why HF Spaces?**
- Full Docker support (unlike Streamlit Cloud)
- Free tier sufficient for capstone
- Built-in secrets management
- Easy sharing and demo

### Dockerfile (HF Spaces)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# HF Spaces uses port 7860
EXPOSE 7860

# Health check for HF Spaces
HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
```

### Local Development (docker-compose)

```yaml
# docker-compose.yml (for local development)
version: '3.8'

services:
  app:
    build: .
    ports:
      - "7860:7860"
    environment:
      - LANGCHAIN_TRACING_V2=true
      - LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY}
      - LANGCHAIN_PROJECT=call-center-assistant
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/app/data
```

### HF Spaces Secrets Configuration

In your HF Space settings (Settings → Repository secrets):

| Secret Name | Description |
|-------------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4, Whisper |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude |
| `LANGCHAIN_API_KEY` | LangSmith API key for tracing |
| `LANGCHAIN_TRACING_V2` | Set to `true` |
| `LANGCHAIN_PROJECT` | Set to `call-center-assistant` |

### Environment Variables

```bash
# .env.example (for local development)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=call-center-assistant

OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Deployment Strategy

```
Step 1: Minimal app ────────▶ Deploy to HF Spaces ────▶ Verify working
    │
    ▼
Step 2: All dependencies ───▶ Deploy to HF Spaces ────▶ Verify imports
    │
    ▼
Step 3+: Add features ──────▶ Deploy incrementally ────▶ Verify each step
```

**Key Principle**: The project was built iteratively with continuous deployment verification.

---

## 13. Project Structure

```
call_center_assistant/
├── agents/
│   ├── __init__.py
│   ├── supervisor_agent.py       # Orchestration & routing decisions
│   ├── intake_agent.py
│   ├── transcription_agent.py
│   ├── summarization_agent.py
│   ├── summary_critic_agent.py   # Reviews & requests revisions
│   ├── qa_scoring_agent.py
│   ├── abuse_review_agent.py     # Deep abuse analysis
│   └── human_escalation.py       # Terminal escalation node
├── graph/
│   ├── __init__.py
│   ├── workflow.py               # LangGraph definition with conditional routing
│   ├── state.py                  # AgentState schema
│   └── callbacks.py              # Animation & LangSmith callbacks
├── guardrails/
│   ├── __init__.py
│   ├── input_validator.py        # File & content validation
│   ├── audio_classifier.py       # Music vs speech detection
│   ├── conversation_detector.py  # Call vs podcast vs other
│   ├── abuse_detector.py         # Toxicity & abuse flagging
│   └── schemas.py                # Pydantic models for guardrails
├── ui/
│   ├── __init__.py
│   ├── app.py                    # Streamlit main entry
│   └── components/
│       ├── __init__.py
│       ├── flow_visualizer.py    # n8n-style animation with dynamic routing
│       ├── upload.py             # File upload component
│       ├── results.py            # Results dashboard
│       └── validation_modal.py   # User confirmation dialogs
├── models/
│   ├── __init__.py
│   └── schemas.py                # Pydantic models (CallSummary, QAScores, etc.)
├── evaluation/
│   ├── __init__.py
│   ├── datasets/
│   │   └── test_cases.json       # Ground truth examples
│   ├── evaluators/
│   │   ├── __init__.py
│   │   ├── faithfulness.py
│   │   ├── completeness.py
│   │   ├── qa_score_validator.py
│   │   ├── routing_efficiency.py # Evaluates Supervisor decisions
│   │   └── latency.py
│   └── run_eval.py               # Evaluation runner script
├── config/
│   ├── __init__.py
│   ├── settings.py               # App configuration
│   └── litellm_config.yaml       # Model routing config
├── data/
│   └── sample_calls/             # Test audio/transcripts
├── tests/
│   ├── __init__.py
│   ├── test_agents/
│   ├── test_guardrails/
│   └── test_integration/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── REQUIREMENTS.md               # This document
└── README.md
```

---

## 14. Evaluation Criteria

Based on bootcamp rubric:

| Category | Weight | How We Address It |
|----------|--------|-------------------|
| **Functionality** | 35% | Full pipeline: audio → summary + QA, with guardrails and self-correction |
| **Agent Design** | 25% | True multi-agent with Supervisor routing, Critic loops, autonomous decisions |
| **User Experience** | 15% | Animated workflow showing dynamic routing, clean dashboard, validation flows |
| **Routing & Fallback** | 15% | LiteLLM MCP, Supervisor-based routing, graceful degradation, revision loops |
| **Documentation** | 10% | README, inline docs, LangSmith traces, this requirements doc |

---

## Appendix A: Sample Evaluation Rubric for QA Scoring

### Empathy (0-10)

| Score | Criteria |
|-------|----------|
| 9-10 | Actively acknowledges feelings, uses empathetic language, shows genuine concern |
| 7-8 | Shows understanding, uses appropriate tone |
| 5-6 | Neutral, task-focused but not cold |
| 3-4 | Dismissive or rushed |
| 0-2 | Cold, robotic, or antagonistic |

### Professionalism (0-10)

| Score | Criteria |
|-------|----------|
| 9-10 | Polite, clear communication, proper greeting/closing |
| 7-8 | Professional throughout, minor lapses |
| 5-6 | Adequate but room for improvement |
| 3-4 | Unprofessional language or behavior |
| 0-2 | Rude, inappropriate, or offensive |

### Resolution (0-10)

| Score | Criteria |
|-------|----------|
| 9-10 | Issue fully resolved, customer satisfied |
| 7-8 | Issue mostly resolved, clear next steps |
| 5-6 | Partial resolution, some ambiguity |
| 3-4 | Issue unresolved, poor guidance |
| 0-2 | Made situation worse or no attempt to help |

### Tone (0-10)

| Score | Criteria |
|-------|----------|
| 9-10 | Warm, engaging, builds rapport |
| 7-8 | Pleasant and appropriate |
| 5-6 | Neutral, neither positive nor negative |
| 3-4 | Terse, impatient, or condescending |
| 0-2 | Hostile or aggressive |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-22 | Initial requirements capture |
| 1.1 | 2026-01-22 | Added true multi-agent architecture with Supervisor, Critic loops, dynamic routing; Enhanced animation requirements for multi-agent visualization; Added Pydantic section; Updated project structure |
| 1.2 | 2026-01-22 | Added Multi-LLM strategy (Critic Independence Principle); Updated deployment target to Hugging Face Spaces with Docker; Created separate EXECUTION_PLAN.md with phased approach |

---

## Next Steps

1. Review and approve this requirements document
2. Set up project scaffold with Docker
3. Implement LangGraph workflow with Supervisor Agent
4. Implement worker agents (Intake, Transcription, Summarization)
5. Add Summary Critic Agent with revision loop
6. Add QA Scoring and Abuse Review agents
7. Implement guardrails (input validation, abuse detection)
8. Build Streamlit UI with dynamic workflow visualization
9. Set up LangSmith evaluation pipeline
10. Test with sample data
11. Documentation and demo video
