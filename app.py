import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

st.set_page_config(
    page_title="Call Center Assistant",
    page_icon="📞",
    layout="wide"
)

# ===================
# Initialize
# ===================
st.title("📞 AI Call Center Assistant")
st.markdown("**Phase 2**: Single Agent (Summarization)")

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ OPENAI_API_KEY not set. Please add it to your environment or HF Spaces secrets.")
    st.stop()

# Import after env check
from agents.summarization_agent import SummarizationAgent
from models.schemas import CallSummary

# Initialize agent (cached)
@st.cache_resource
def get_summarization_agent():
    return SummarizationAgent(model="gpt-4o-mini")

agent = get_summarization_agent()

# ===================
# Sidebar - Sample Data
# ===================
with st.sidebar:
    st.header("📁 Sample Transcripts")

    sample_dir = Path("data/sample_transcripts")
    if sample_dir.exists():
        sample_files = list(sample_dir.glob("*.txt"))
        if sample_files:
            selected_sample = st.selectbox(
                "Load a sample transcript:",
                options=["None"] + [f.name for f in sample_files]
            )
        else:
            selected_sample = "None"
            st.info("No sample files found")
    else:
        selected_sample = "None"
        st.info("Sample directory not found")

    st.divider()
    st.markdown("**Agent Info**")
    st.caption(f"Model: {agent.model_name}")

# ===================
# Main Content
# ===================
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📤 Input")

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload transcript (.txt)",
        type=["txt"],
        help="Upload a text file containing a call transcript"
    )

    # Text area for transcript
    if uploaded_file:
        transcript_text = uploaded_file.read().decode("utf-8")
    elif selected_sample != "None":
        sample_path = Path("data/sample_transcripts") / selected_sample
        transcript_text = sample_path.read_text()
    else:
        transcript_text = ""

    transcript_input = st.text_area(
        "Transcript",
        value=transcript_text,
        height=400,
        placeholder="Paste or upload a call transcript..."
    )

    # Process button
    process_btn = st.button(
        "🚀 Generate Summary",
        type="primary",
        disabled=not transcript_input.strip()
    )

with col_right:
    st.subheader("📊 Results")

    if process_btn and transcript_input.strip():
        with st.spinner("Analyzing transcript with GPT-4..."):
            try:
                summary = agent.run(transcript_input)
                st.session_state["last_summary"] = summary
                st.session_state["last_transcript"] = transcript_input
            except Exception as e:
                st.error(f"Error generating summary: {e}")
                st.stop()

    # Display results if available
    if "last_summary" in st.session_state:
        summary: CallSummary = st.session_state["last_summary"]

        # Brief Summary
        st.markdown("**Brief Summary**")
        st.info(summary.brief_summary)

        # Key Points
        st.markdown("**Key Points**")
        for point in summary.key_points:
            st.markdown(f"• {point}")

        # Action Items
        if summary.action_items:
            st.markdown("**Action Items**")
            for item in summary.action_items:
                st.markdown(f"☐ {item}")
        else:
            st.markdown("**Action Items**")
            st.markdown("_No action items_")

        # Customer Intent
        st.markdown("**Customer Intent**")
        st.write(summary.customer_intent)

        # Metadata
        st.divider()
        cols = st.columns(3)

        with cols[0]:
            sentiment_colors = {
                "positive": "🟢",
                "neutral": "🟡",
                "negative": "🔴"
            }
            st.metric(
                "Sentiment",
                f"{sentiment_colors.get(summary.sentiment.value, '⚪')} {summary.sentiment.value.title()}"
            )

        with cols[1]:
            resolution_colors = {
                "resolved": "✅",
                "unresolved": "⏳",
                "escalated": "⬆️"
            }
            st.metric(
                "Resolution",
                f"{resolution_colors.get(summary.resolution_status.value, '❓')} {summary.resolution_status.value.title()}"
            )

        with cols[2]:
            st.metric("Topics", len(summary.topics))

        # Topics
        with st.expander("Topics Discussed"):
            for topic in summary.topics:
                st.markdown(f"• {topic}")

        # Raw JSON
        with st.expander("Raw JSON Output"):
            st.json(summary.model_dump())

    else:
        st.info("Upload or select a transcript, then click 'Generate Summary' to see results.")

# ===================
# Footer
# ===================
st.divider()
st.caption("AI Call Center Assistant | Capstone Project | Phase 2 - Single Agent")
