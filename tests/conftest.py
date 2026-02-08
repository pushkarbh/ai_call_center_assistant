"""Pytest configuration and fixtures"""
import pytest
import os
from dotenv import load_dotenv

# Load environment variables for tests
load_dotenv()


@pytest.fixture(scope="session")
def sample_transcript():
    """Sample transcript for testing"""
    return """Customer: Hi, I have a question about my bill. I was charged $150 but my plan is $99.
Agent: I understand your concern. Let me check your account. Can I have your account number?
Customer: Sure, it's 12345678.
Agent: Thank you. I see a one-time setup fee of $50 plus your $99 plan charge.
Customer: I wasn't told about a setup fee.
Agent: I apologize for the confusion. I'll credit the $50 back to your account.
Customer: That's great, thank you!
Agent: You're welcome. Is there anything else I can help with?
Customer: No, that's all. Thanks again!
Agent: Have a wonderful day!"""


@pytest.fixture(scope="session")
def sample_short_transcript():
    """Short transcript that should fail validation"""
    return "Hello. Bye."


@pytest.fixture(scope="session")
def sample_abusive_transcript():
    """Transcript with abusive language"""
    return """Customer: This is bullshit! You people are idiots!
Agent: I understand you're frustrated. Let me help you.
Customer: You're damn right I'm frustrated!
Agent: I apologize for the experience. What can I do to help?"""


@pytest.fixture(scope="session")
def api_keys_available():
    """Check if API keys are available"""
    return {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "langsmith": bool(os.getenv("LANGCHAIN_API_KEY"))
    }


@pytest.fixture
def disable_langsmith():
    """Temporarily disable LangSmith tracing for tests"""
    original = os.environ.get("LANGCHAIN_TRACING_V2")
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    yield
    if original:
        os.environ["LANGCHAIN_TRACING_V2"] = original
    else:
        os.environ.pop("LANGCHAIN_TRACING_V2", None)


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require API keys)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (may take longer to run)"
    )
