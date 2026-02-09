# Development Guide

## Local Build & Development Workflow

### Step 1: Initial Setup (One-time)

```bash
# Clone the repository (if not already done)
git clone https://github.com/pushkarbh/ai_call_center_assistant.git
cd ai_call_center_assistant

# Run setup script
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh

# This script will:
# - Create a Python virtual environment (venv/)
# - Install all dependencies from requirements.txt
# - Install test dependencies (pytest, pytest-cov, etc.)
# - Set up your .env file template
```

**Required Environment Variables:**

Edit the `.env` file in the project root with your API keys:

```bash
OPENAI_API_KEY=sk-...                    # Required for GPT-4o-mini agents
ANTHROPIC_API_KEY=sk-ant-...            # Required for Claude Sonnet critic
LANGCHAIN_TRACING_V2=true               # Optional: Enable LangSmith tracing
LANGCHAIN_API_KEY=ls__...               # Optional: LangSmith API key
LANGCHAIN_PROJECT=call-center-assistant # Optional: LangSmith project name
```

### Step 2: Activate Environment (Every Session)

```bash
# Activate virtual environment
source venv/bin/activate

# Verify installation
python --version  # Should show Python 3.12.x
pip list | grep pytest  # Should show pytest packages
```

### Step 3: Run Tests

#### Unit Tests (Fast, No API Calls)

```bash
# Run only unit tests (uses mocks, no external API calls)
pytest tests/ -v -m "not integration"

# Expected: ~40 tests pass in <5 seconds
```

#### Integration Tests (Requires API Keys)

```bash
# Run only integration tests (makes real API calls)
pytest tests/ -v -m integration

# Expected: ~2 tests pass in ~30 seconds
# Note: These tests will consume API credits
```

#### All Tests

```bash
# Run complete test suite
pytest tests/ -v

# Expected: All 42 tests pass
```

#### Test Coverage Report

```bash
# Generate coverage report
pytest tests/ --cov=agents --cov=graph --cov=models --cov=evaluation/evaluators --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=agents --cov=graph --cov=models --cov-report=html
# Open htmlcov/index.html in browser
```

### Step 4: Run Application Locally

```bash
# Start Streamlit app (ensure venv is activated)
streamlit run app.py --server.port=7860

# Open http://localhost:7860 in your browser
```

### Step 5: Test with Sample Data

```bash
# Use provided test transcripts
data/sample_transcripts/billing_inquiry.txt
data/sample_transcripts/complaint_with_frustration.txt
data/sample_transcripts/tech_support_unresolved.txt

# Or use guardrail test cases
test_data/guardrail_tests/01_valid_normal.txt
test_data/guardrail_tests/03_profanity.txt
test_data/guardrail_tests/07_mixed_abuse.txt
```

### Step 6: Deactivate Environment

```bash
# When done developing
deactivate
```

## Docker Build & Testing (Pre-deployment)

### Test Production Environment Locally

```bash
# Build and run in Docker (matches HF Spaces environment)
chmod +x scripts/test_docker.sh
./scripts/test_docker.sh

# Open http://localhost:7860
# Test the same way end-users will experience it

# View container logs
docker logs -f call-center-test

# Stop and cleanup
docker stop call-center-test
docker rm call-center-test

# Remove old images (optional)
chmod +x scripts/cleanup_docker.sh
./scripts/cleanup_docker.sh
```

## Recommended Development Workflow

```
┌─────────────────────────────────────┐
│ 1. Local Development (venv)         │
│    - source venv/bin/activate       │
│    - Make code changes              │
│    - Test manually with app         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. Run Unit Tests                   │
│    pytest tests/ -m "not integration" │
│    - Fast feedback (~5 sec)         │
│    - No API calls                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. Run Integration Tests            │
│    pytest tests/ -v                 │
│    - Complete validation (~30 sec)  │
│    - Tests real API integration     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Docker Build Test (optional)     │
│    ./scripts/test_docker.sh         │
│    - Matches production environment │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 5. Git Commit & Push                │
│    git add . && git commit          │
│    git push origin main             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 6. Auto-Deploy to HF Spaces         │
│    - Automatic on push to main      │
│    - Monitor build logs on HF       │
└─────────────────────────────────────┘
```

---

## Running Tests

### Unit Tests (Fast)

Run unit tests without API calls:

```bash
source venv/bin/activate
pytest tests/ -m "not integration"
```

### Integration Tests (Require API Keys)

Run full integration tests (requires API keys in `.env`):

```bash
source venv/bin/activate
pytest tests/ -m integration
```

### All Tests

Run all tests:

```bash
source venv/bin/activate
pytest tests/
```

### Test Coverage

Generate coverage report:

```bash
source venv/bin/activate
pytest tests/ --cov=agents --cov=graph --cov=models --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Organization

- `test_models.py` - Pydantic model validation tests
- `test_agents.py` - Individual agent unit tests
- `test_workflow.py` - Workflow and integration tests
- `test_evaluators.py` - Evaluator tests
- `conftest.py` - Shared fixtures and configuration

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

## Deploying to Hugging Face Spaces

### Prerequisites

Your repository should have the HF Spaces remote configured:

```bash
# Check configured remotes
git remote -v

# Should show:
# hf      https://huggingface.co/spaces/USERNAME/SPACE_NAME (fetch)
# hf      https://huggingface.co/spaces/USERNAME/SPACE_NAME (push)
# origin  https://github.com/USERNAME/REPO_NAME.git (fetch)
# origin  https://github.com/USERNAME/REPO_NAME.git (push)
```

### Deployment Steps

```bash
# 1. Ensure all changes are committed
git add .
git commit -m "Your commit message"

# 2. Push to GitHub first (recommended)
git push origin main

# 3. Push to Hugging Face Spaces
git push hf main
```

### Troubleshooting Large Files

HF Spaces rejects files larger than 10MB. If you encounter this error:

```bash
# 1. Remove large files from current commit
git rm --cached "Large File.pdf"
echo "*.pdf" >> .gitignore  # Add to gitignore
git add .gitignore
git commit -m "Remove large files for HF compatibility"

# 2. If the file is in git history, remove it from ALL commits
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch '*.pdf'" \
  --prune-empty --tag-name-filter cat -- --all

# 3. Force push to clean history
git push --force origin main
git push --force hf main
```

### Common File Types to Exclude

Add these to `.gitignore` before committing:

```
# Large binary files
*.pdf
*.zip
*.tar.gz

# Development files
venv/
__pycache__/
.pytest_cache/
htmlcov/
.coverage
.env

# IDE files
.vscode/
.idea/
.DS_Store
```

### Monitoring Deployment

After pushing to HF Spaces:

1. Visit your space: `https://huggingface.co/spaces/USERNAME/SPACE_NAME`
2. Check the **Logs** tab for build status
3. Build typically takes 2-5 minutes
4. App auto-restarts once build completes

### Force Rebuild

If changes don't appear after push:

```bash
# 1. Make a trivial change and commit
echo "" >> README.md
git add README.md
git commit -m "Trigger rebuild"

# 2. Push to HF
git push hf main
```

---

## Adding New Dependencies

```bash
# Activate venv
source venv/bin/activate

# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Test with Docker (matches HF environment)
./scripts/test_docker.sh

# Commit and push to both remotes
git add requirements.txt
git commit -m "deps: Add package-name"
git push origin main
git push hf main  # Deploy to HF Spaces
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

## Multi-Agent Pipeline

### Multi-Agent Workflow

The system implements a **linear multi-agent workflow** using LangGraph:

**Pipeline**: Intake → Transcription → Summarization → QA Scoring

**Agents**:
1. **Intake Agent**: Validates input, extracts metadata, generates call ID
2. **Transcription Agent**: Pass-through for text, Whisper API for audio (future)
3. **Summarization Agent**: Analyzes call with GPT-4o-mini
4. **QA Scoring Agent**: Evaluates empathy, professionalism, resolution, tone (0-10 scale)

**State Management**: Uses `AgentState` Pydantic model to pass data between agents

### Testing the Pipeline

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

### Pipeline Files

- `agents/intake_agent.py` - Input validation and metadata extraction
- `agents/transcription_agent.py` - Text pass-through and Whisper integration
- `agents/qa_scoring_agent.py` - Quality evaluation with GPT-4o-mini
- `graph/workflow.py` - LangGraph workflow definition
- Updated `app.py` - Multi-agent UI with tabs for all outputs

