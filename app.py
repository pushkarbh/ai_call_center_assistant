import streamlit as st

st.set_page_config(
    page_title="Call Center Assistant",
    page_icon="📞",
    layout="wide"
)

st.title("📞 AI Call Center Assistant")
st.markdown("**Phase 1**: Dependency Verification + UI Skeleton")

# ===================
# Dependency Check
# ===================
st.header("1. Dependency Verification")

with st.status("Checking dependencies...", expanded=True) as status:
    all_ok = True

    # Test core imports
    try:
        st.write("Checking Streamlit...")
        import streamlit
        st.write(f"  ✅ streamlit {streamlit.__version__}")
    except Exception as e:
        st.write(f"  ❌ streamlit: {e}")
        all_ok = False

    try:
        st.write("Checking Pydantic...")
        import pydantic
        st.write(f"  ✅ pydantic {pydantic.__version__}")
    except Exception as e:
        st.write(f"  ❌ pydantic: {e}")
        all_ok = False

    try:
        st.write("Checking LangChain...")
        import langchain
        st.write(f"  ✅ langchain {langchain.__version__}")
    except Exception as e:
        st.write(f"  ❌ langchain: {e}")
        all_ok = False

    try:
        st.write("Checking LangChain-OpenAI...")
        from langchain_openai import ChatOpenAI
        st.write("  ✅ langchain-openai")
    except Exception as e:
        st.write(f"  ❌ langchain-openai: {e}")
        all_ok = False

    try:
        st.write("Checking LangChain-Anthropic...")
        from langchain_anthropic import ChatAnthropic
        st.write("  ✅ langchain-anthropic")
    except Exception as e:
        st.write(f"  ❌ langchain-anthropic: {e}")
        all_ok = False

    try:
        st.write("Checking LangGraph...")
        from langgraph.graph import StateGraph
        st.write("  ✅ langgraph")
    except Exception as e:
        st.write(f"  ❌ langgraph: {e}")
        all_ok = False

    try:
        st.write("Checking LiteLLM...")
        import litellm
        try:
            version = litellm.__version__
        except AttributeError:
            version = "(version info not available)"
        st.write(f"  ✅ litellm {version}")
    except Exception as e:
        st.write(f"  ❌ litellm: {e}")
        all_ok = False

    try:
        st.write("Checking OpenAI...")
        import openai
        st.write(f"  ✅ openai {openai.__version__}")
    except Exception as e:
        st.write(f"  ❌ openai: {e}")
        all_ok = False

    try:
        st.write("Checking streamlit-flow...")
        from streamlit_flow import streamlit_flow
        st.write("  ✅ streamlit-flow")
    except Exception as e:
        st.write(f"  ❌ streamlit-flow: {e}")
        all_ok = False

    try:
        st.write("Checking project modules...")
        from config.settings import settings
        from models.schemas import CallSummary, QAScores, AgentState
        st.write("  ✅ project modules")
    except Exception as e:
        st.write(f"  ❌ project modules: {e}")
        all_ok = False

    if all_ok:
        status.update(label="All dependencies verified!", state="complete")
    else:
        status.update(label="Some dependencies failed!", state="error")

# ===================
# Configuration Check
# ===================
st.header("2. Configuration Status")

try:
    from config.settings import settings
    config_status = settings.validate()

    col1, col2, col3 = st.columns(3)
    with col1:
        if config_status["openai"]:
            st.success("✅ OpenAI API Key")
        else:
            st.warning("⚠️ OpenAI API Key not set")

    with col2:
        if config_status["anthropic"]:
            st.success("✅ Anthropic API Key")
        else:
            st.warning("⚠️ Anthropic API Key not set")

    with col3:
        if config_status["langsmith"]:
            st.success("✅ LangSmith API Key")
        else:
            st.warning("⚠️ LangSmith API Key not set")
except Exception as e:
    st.error(f"Configuration error: {e}")

# ===================
# UI Skeleton
# ===================
st.header("3. UI Skeleton")

st.divider()

# Two-column layout
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("📤 Upload")
    uploaded_file = st.file_uploader(
        "Upload audio or transcript",
        type=["wav", "mp3", "m4a", "txt", "json"],
        help="Supported formats: WAV, MP3, M4A (audio) or TXT, JSON (transcript)"
    )

    if uploaded_file:
        st.info(f"File: {uploaded_file.name} ({uploaded_file.size} bytes)")

    process_btn = st.button("🚀 Process Call", type="primary", disabled=not uploaded_file)

    if process_btn:
        st.info("Processing will be implemented in Phase 2")

with col_right:
    st.subheader("🔄 Workflow")
    st.info("Workflow animation will be implemented in Phase 6")

    # Placeholder for workflow visualization
    st.markdown("""
    ```
    ┌────────────┐     ┌──────────────┐     ┌─────────────┐
    │  Intake    │────▶│ Transcribe   │────▶│  Summarize  │
    │  Agent     │     │    Agent     │     │    Agent    │
    └────────────┘     └──────────────┘     └─────────────┘
                                                   │
                                                   ▼
                                           ┌─────────────┐
                                           │  QA Score   │
                                           │    Agent    │
                                           └─────────────┘
    ```
    """)

st.divider()

# Results tabs
st.subheader("📊 Results")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Transcript",
    "Summary",
    "QA Scores",
    "Abuse Flags",
    "Debug"
])

with tab1:
    st.markdown("*Transcript will appear here after processing...*")

with tab2:
    st.markdown("*Summary will appear here after processing...*")

    # Preview of what summary will look like
    with st.expander("Preview: Summary Format"):
        st.markdown("""
        **Brief Summary**
        > Customer called about billing issue. Agent resolved by applying credit.

        **Key Points**
        - Customer charged $150 instead of $99
        - Setup fee was not communicated
        - Agent credited $50 back

        **Action Items**
        - None

        **Sentiment**: Positive | **Resolution**: Resolved
        """)

with tab3:
    st.markdown("*QA Scores will appear here after processing...*")

    # Preview of what scores will look like
    with st.expander("Preview: QA Scores Format"):
        cols = st.columns(4)
        cols[0].metric("Empathy", "8.5", delta="Good")
        cols[1].metric("Professionalism", "9.0", delta="Excellent")
        cols[2].metric("Resolution", "8.0", delta="Good")
        cols[3].metric("Tone", "8.5", delta="Good")

with tab4:
    st.markdown("*Abuse flags will appear here if detected...*")

with tab5:
    st.markdown("*Debug info will appear here after processing...*")

    with st.expander("Preview: Debug Info"):
        st.json({
            "execution_path": ["supervisor", "intake", "transcription", "summarization", "qa_scoring"],
            "models_used": ["gpt-4o-mini", "whisper-1", "gpt-4", "gpt-4"],
            "revision_count": 0,
            "total_time_ms": 3500,
            "langsmith_trace_url": "https://smith.langchain.com/..."
        })

# ===================
# Footer
# ===================
st.divider()
st.caption("AI Call Center Assistant | Capstone Project | Phase 1")
