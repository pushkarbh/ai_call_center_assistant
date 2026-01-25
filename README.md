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

A multi-agent system for analyzing call center recordings and transcripts using LangGraph.

## Current Phase: 5 - Guardrails ✅

**Pipeline**: Validation → Intake → Transcription → Abuse Detection → Summarization → Critic → (Revision Loop) → QA Scoring

### Features
- ✅ **Input Validation Agent**: Checks transcript quality (word count, structure, spam detection)
- ✅ **Intake Agent**: Metadata extraction and input validation
- ✅ **Transcription Agent**: Text pass-through (Whisper API integration coming soon)
- ✅ **Abuse Detection Agent**: Detects profanity, threats, harassment, hate speech (GPT-4o-mini)
- ✅ **Summarization Agent**: Call analysis with GPT-4o-mini (supports revisions)
- ✅ **Critic Agent**: Evaluates summary quality (faithfulness, completeness, conciseness)
- ✅ **Revision Loop**: Automatically improves summaries (up to 3 attempts)
- ✅ **QA Scoring Agent**: Empathy, professionalism, resolution, tone evaluation (0-10 scale)
- ✅ **Supervisor Agent**: Dynamic routing and workflow control
- ✅ **LangGraph Conditional Routing**: Stops on validation failure, loops for revisions
- ✅ **File Upload**: Support for .txt, .wav, .mp3, .m4a files
- ⏳ **Audio Transcription**: Whisper API integration (Phase 7)
- ⏳ **Workflow Visualization**: n8n-style animation (Phase 6)

## How It Works

1. Upload a call transcript (.txt) or audio file (.wav, .mp3, .m4a)
2. The multi-agent pipeline processes your input:
   - **Validation**: Checks input quality (length, structure, spam detection)
   - **Intake**: Validates input and extracts metadata
   - **Transcription**: Prepares text for analysis
   - **Abuse Detection**: Scans for profanity, threats, harassment, hate speech
   - **Summarization**: Analyzes call content, sentiment, resolution
   - **Critic**: Evaluates summary quality (faithfulness, completeness, conciseness)
   - **Revision Loop**: If needed, sends summary back for improvement (up to 3 times)
   - **QA Scoring**: Evaluates agent performance on 4 dimensions
3. View comprehensive results: validation status, abuse alerts, summary, critique scores, QA metrics

## Tech Stack
- **Orchestration**: LangGraph
- **LLM Framework**: LangChain
- **Observability**: LangSmith
- **Model Control**: LiteLLM
- **UI**: Streamlit
- **Deployment**: Docker

## Repository
GitHub: https://github.com/pushkarbh/ai_call_center_assistant
