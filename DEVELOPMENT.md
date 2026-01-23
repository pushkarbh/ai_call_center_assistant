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
