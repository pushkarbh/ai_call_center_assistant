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

## Current Phase: 3 - Multi-Agent Pipeline ✅

**Pipeline**: Intake → Transcription → Summarization → QA Scoring

### Features
- ✅ **Intake Agent**: Metadata extraction and input validation
- ✅ **Transcription Agent**: Text pass-through (Whisper API integration coming soon)
- ✅ **Summarization Agent**: Call analysis with GPT-4o-mini
- ✅ **QA Scoring Agent**: Empathy, professionalism, resolution, tone evaluation (0-10 scale)
- ✅ **LangGraph Workflow**: Linear multi-agent orchestration
- ✅ **File Upload**: Support for .txt, .wav, .mp3, .m4a files
- ⏳ **Audio Transcription**: Whisper API integration (Phase 3+)
- ⏳ **Abuse Detection**: Coming in Phase 5
- ⏳ **Workflow Visualization**: n8n-style animation (Phase 6)

## How It Works

1. Upload a call transcript (.txt) or audio file (.wav, .mp3, .m4a)
2. The multi-agent pipeline processes your input:
   - **Intake**: Validates input and extracts metadata
   - **Transcription**: Prepares text for analysis
   - **Summarization**: Analyzes call content, sentiment, resolution
   - **QA Scoring**: Evaluates agent performance on 4 dimensions
3. View comprehensive results: summary, scores, metadata, execution path

## Tech Stack
- **Orchestration**: LangGraph
- **LLM Framework**: LangChain
- **Observability**: LangSmith
- **Model Control**: LiteLLM
- **UI**: Streamlit
- **Deployment**: Docker

## Repository
GitHub: https://github.com/pushkarbh/ai_call_center_assistant
