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
- ⏳ **Audio Transcription**: Whisper API integration (planned)
- ⏳ **Workflow Visualization**: n8n-style animation (planned)

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

## Quick Start - Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/pushkarbh/ai_call_center_assistant.git
cd ai_call_center_assistant

# 2. Set up environment
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh

# 3. Add your API keys to .env file
cp .env.example .env
# Edit .env with your actual API keys:
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY
# - LANGCHAIN_API_KEY (optional, for observability)

# 4. Run the app
source venv/bin/activate
streamlit run app.py --server.port=7860

# 5. Open in browser
# Navigate to http://localhost:7860
```

## Repository
GitHub: https://github.com/pushkarbh/ai_call_center_assistant
