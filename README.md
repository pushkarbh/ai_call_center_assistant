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

## Multi-Agent Pipeline

**Workflow**: Validation → Intake → Transcription → Abuse Detection → Summarization → Critic → (Revision Loop) → QA Scoring

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

## Quick Start - Local Build & Run

```bash
# 1. Clone the repository
git clone https://github.com/pushkarbh/ai_call_center_assistant.git
cd ai_call_center_assistant

# 2. Set up environment (one-time)
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh

# 3. Configure API keys
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY=sk-...       (required)
# - ANTHROPIC_API_KEY=sk-ant-... (required)
# - LANGCHAIN_API_KEY=ls__...   (optional)

# 4. Activate environment
source venv/bin/activate

# 5. Run tests (recommended)
pytest tests/ -v -m "not integration"  # Unit tests (fast)
pytest tests/ -v                        # All tests (requires API keys)

# 6. Run the application
streamlit run app.py --server.port=7860

# 7. Open in browser
# Navigate to http://localhost:7860
```

## Repository
GitHub: https://github.com/pushkarbh/ai_call_center_assistant

---

## Testing

### Test Suite

The project includes 42 comprehensive tests covering all components.

```bash
# Activate environment first
source venv/bin/activate

# Unit tests only (fast, ~5 seconds, no API calls)
pytest tests/ -v -m "not integration"
# ✅ 40 tests: Models, agents, evaluators, workflow structure

# Integration tests only (requires API keys, ~30 seconds)
pytest tests/ -v -m integration
# ✅ 2 tests: Full pipeline with real API calls

# All tests (complete suite)
pytest tests/ -v
# ✅ 42 tests total

# With coverage report
pytest tests/ --cov=agents --cov=graph --cov=models --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=agents --cov=graph --cov=models --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Coverage

| Component | Tests | Coverage |
|-----------|-------|----------|
| **Pydantic Models** | 18 tests | Model validation, defaults, constraints |
| **Agents** | 9 tests | Intake, Transcription, Validation, Mocked LLM agents |
| **Workflow** | 5 tests | Graph creation, routing, validation, integration |
| **Evaluators** | 6 tests | Faithfulness, Completeness, QA validation |
| **Integration** | 2 tests | Full pipeline end-to-end with real APIs |

**Test Files:**
- `tests/test_models.py` - Pydantic schema validation
- `tests/test_agents.py` - Individual agent unit tests
- `tests/test_workflow.py` - Workflow and integration tests
- `tests/test_evaluators.py` - Evaluator tests
- `tests/conftest.py` - Shared fixtures and configuration
- `pytest.ini` - Test configuration
