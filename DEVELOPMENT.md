# Development Guide

## Two Development Approaches

### 1. Local Development (venv) - Recommended for daily work

Fast iteration, full IDE support, easy debugging.

```bash
# One-time setup
chmod +x setup_local.sh
./setup_local.sh

# Daily workflow
source venv/bin/activate
streamlit run app.py --server.port=7860
# Open http://localhost:7860

# When done
deactivate
```

### 2. Docker Testing - Before deploying to HF Spaces

Test exact production environment locally.

```bash
# One-time setup
chmod +x test_docker.sh

# Test before deploying
./test_docker.sh
# Open http://localhost:7860

# View logs
docker logs -f call-center-test

# Stop and cleanup
docker stop call-center-test
docker rm call-center-test
```

## Recommended Workflow

```
┌─────────────────┐
│ Local Dev       │
│ (venv)          │  ← Daily development
│ Fast iteration  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Docker Test     │  ← Before committing
│ (local)         │
│ Verify build    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Git Push        │  ← Commit & push
│ GitHub/HF       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ HF Spaces       │  ← Auto-deploy
│ Production      │
└─────────────────┘
```

## File Structure

```
ai_call_center_assistant/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
├── Dockerfile             # HF Spaces deployment config
├── setup_local.sh         # Local venv setup script
├── test_docker.sh         # Docker testing script
├── .gitignore            # Git ignore rules
├── README.md             # HF Spaces documentation
├── DEVELOPMENT.md        # This file
├── REQUIREMENTS.md       # Project requirements
├── EXECUTION_PLAN.md     # Phase-by-phase plan
└── data/
    └── sample_transcripts/

# Ignored (not in Git)
venv/                     # Virtual environment
__pycache__/             # Python cache
.env                     # Environment variables
```

## Adding New Dependencies

```bash
# Activate venv
source venv/bin/activate

# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Test with Docker
./test_docker.sh

# Commit and push
git add requirements.txt
git commit -m "deps: Add package-name"
git push origin main
```

## Environment Variables

For local development with API keys:

```bash
# Create .env file (already in .gitignore)
cat > .env << EOF
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
LANGCHAIN_API_KEY=your-key-here
EOF

# Load in app.py
from dotenv import load_dotenv
load_dotenv()
```

For HF Spaces, add secrets in the Space settings UI.

## Troubleshooting

### venv issues
```bash
# Remove and recreate
rm -rf venv
./setup_local.sh
```

### Docker issues
```bash
# Clean everything
docker stop call-center-test
docker rm call-center-test
docker rmi call-center-assistant:test

# Rebuild
./test_docker.sh
```

### Port 7860 already in use
```bash
# Find and kill process
lsof -ti:7860 | xargs kill -9

# Or use different port
streamlit run app.py --server.port=8501
```

## Phase 3 - Multi-Agent Pipeline

### What's New in Phase 3

Phase 3 introduces a **linear multi-agent workflow** using LangGraph:

**Pipeline**: Intake → Transcription → Summarization → QA Scoring

**Agents**:
1. **Intake Agent**: Validates input, extracts metadata, generates call ID
2. **Transcription Agent**: Pass-through for text, Whisper API for audio (future)
3. **Summarization Agent**: Analyzes call with GPT-4o-mini (from Phase 2)
4. **QA Scoring Agent**: Evaluates empathy, professionalism, resolution, tone (0-10 scale)

**State Management**: Uses `AgentState` Pydantic model to pass data between agents

### Testing Phase 3

```bash
# Activate venv
source venv/bin/activate

# Run locally
streamlit run app.py --server.port=7860

# Test with sample transcripts
# - Select from dropdown: billing_inquiry.txt, tech_support_unresolved.txt, etc.
# - Click "Analyze Call" button
# - View all agent outputs: Summary, QA Scores, Metadata, Execution Path

# Test with uploaded file
# - Upload a .txt file with transcript
# - See complete pipeline results
```

### Architecture

```
Input (text/audio)
    ↓
[Intake Agent]
    ↓ (metadata extracted)
[Transcription Agent]
    ↓ (transcript ready)
[Summarization Agent]
    ↓ (summary generated)
[QA Scoring Agent]
    ↓ (quality scores)
Final State → UI Display
```

### Files Created in Phase 3

- `agents/intake_agent.py` - Input validation and metadata extraction
- `agents/transcription_agent.py` - Text pass-through and Whisper integration
- `agents/qa_scoring_agent.py` - Quality evaluation with GPT-4o-mini
- `graph/workflow.py` - LangGraph workflow definition
- Updated `app.py` - Multi-agent UI with tabs for all outputs

