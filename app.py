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
st.markdown("**Phase 5**: Guardrails (Input Validation + Abuse Detection)")

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ OPENAI_API_KEY not set. Please add it to your environment or HF Spaces secrets.")
    st.stop()

# Import after env check
from graph.workflow_phase5 import run_phase5_analysis
from models.schemas import AgentState

# ===================
# Sidebar - Sample Data
# ===================
with st.sidebar:
    st.header("📁 Sample Transcripts")

    # Collect samples from both directories
    all_samples = []
    
    sample_dir = Path("data/sample_transcripts")
    if sample_dir.exists():
        all_samples.extend([f.name for f in sample_dir.glob("*.txt")])
    
    test_dir = Path("test_data")
    if test_dir.exists():
        all_samples.extend([f.name for f in test_dir.glob("*.txt")])
    
    if all_samples:
        selected_sample = st.selectbox(
            "Load a sample transcript:",
            options=["None"] + sorted(all_samples)
        )
    else:
        selected_sample = "None"
        st.info("No sample files found")

    st.divider()
    st.markdown("**Pipeline**")
    st.caption("Validation → Intake → Transcription → Abuse Detection")
    st.caption("→ Summarization → Critic (loop) → QA Scoring")

# ===================
# Main Content
# ===================
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📤 Input")

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload transcript or audio",
        type=["txt", "wav", "mp3", "m4a"],
        help="Upload a text transcript or audio file"
    )

    # Text area for transcript
    transcript_text = ""
    file_name = None
    input_type = "transcript"
    
    if uploaded_file:
        file_name = uploaded_file.name
        # Check if audio file
        if file_name.endswith(('.wav', '.mp3', '.m4a')):
            input_type = "audio"
            st.info(f"🎵 Audio file detected: {file_name}")
            st.warning("⚠️ Audio transcription with Whisper API not yet implemented. Coming soon!")
            # For now, just show the file name
            transcript_text = ""
        else:
            # Text file
            try:
                transcript_text = uploaded_file.read().decode("utf-8")
            except Exception as e:
                st.error(f"Error reading file: {e}")
                transcript_text = ""
    elif selected_sample != "None":
        try:
            # Load from test_data first, then sample_transcripts
            test_path = Path("test_data") / selected_sample
            sample_path = Path("data/sample_transcripts") / selected_sample
            
            if test_path.exists():
                transcript_text = test_path.read_text()
                file_name = selected_sample
            elif sample_path.exists():
                transcript_text = sample_path.read_text()
                file_name = selected_sample
            else:
                st.error(f"Sample file not found: {selected_sample}")
                transcript_text = ""
        except Exception as e:
            st.error(f"Error loading sample: {e}")
            transcript_text = ""

    transcript_input = st.text_area(
        "Transcript",
        value=transcript_text,
        height=400,
        placeholder="Paste or upload a call transcript..."
    )

    # Process button
    process_btn = st.button(
        "🚀 Analyze Call",
        type="primary",
        disabled=not transcript_input.strip()
    )

with col_right:
    st.subheader("📊 Results")

    if process_btn and transcript_input.strip():
        with st.spinner("Running analysis with guardrails..."):
            try:
                # Run the Phase 5 workflow
                final_state = run_phase5_analysis(
                    raw_input=transcript_input,
                    input_type=input_type,
                    input_file_path=file_name
                )
                st.session_state["last_state"] = final_state
            except Exception as e:
                st.error(f"Error running analysis: {e}")
                import traceback
                st.code(traceback.format_exc())
                st.stop()

    # Display results if available
    if "last_state" in st.session_state:
        state = st.session_state["last_state"]  # LangGraph returns a dict
        
        # Validation Results
        if state.get("validation_result"):
            validation = state["validation_result"]
            
            if validation.is_valid:
                st.success("✅ Input validation passed")
            else:
                st.error("❌ Input validation failed")
                for issue in validation.issues:
                    st.error(f"• {issue}")
            
            if validation.warnings:
                with st.expander("⚠️ Validation Warnings"):
                    for warning in validation.warnings:
                        st.warning(warning)
        
        # Abuse Detection Results
        if state.get("abuse_flags"):
            abuse_flags = state["abuse_flags"]
            
            if abuse_flags:
                st.divider()
                st.markdown("### 🚨 Abuse Detection Alerts")
                
                for flag in abuse_flags:
                    severity_colors = {
                        "low": "🟡",
                        "medium": "🟠",
                        "high": "🔴",
                        "critical": "🔴",
                        "none": "⚪"
                    }
                    
                    severity_icon = severity_colors.get(flag.severity.value, "⚪")
                    
                    # Display abuse types (it's a list)
                    abuse_types_str = ", ".join([t.value.upper() for t in flag.abuse_type])
                    
                    with st.expander(f"{severity_icon} {abuse_types_str} - {flag.severity.value.upper()} severity"):
                        if flag.speaker:
                            st.markdown(f"**Speaker**: {flag.speaker}")
                        if flag.evidence:
                            st.markdown(f"**Evidence**: {', '.join([f'\"{e}\"' for e in flag.evidence])}")
                        if flag.recommended_action:
                            st.markdown(f"**Recommended Action**: {flag.recommended_action}")
            else:
                st.success("✅ No abusive content detected")
        
        # Only show summary if validation passed
        if not state.get("validation_result") or state.get("validation_result").is_valid:
            summary = state["summary"]
            
            st.divider()
            st.markdown("### 📋 Call Summary")

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

        # QA Scores
        if state.get("qa_scores"):
            st.divider()
            st.markdown("### 📋 Quality Evaluation")
            
            qa = state["qa_scores"]
            qa_cols = st.columns(4)
            
            with qa_cols[0]:
                st.metric("Empathy", f"{qa.empathy}/10")
            with qa_cols[1]:
                st.metric("Professionalism", f"{qa.professionalism}/10")
            with qa_cols[2]:
                st.metric("Resolution", f"{qa.resolution}/10")
            with qa_cols[3]:
                st.metric("Tone", f"{qa.tone}/10")
            
            # Overall score
            st.metric("Overall Score", f"{qa.overall}/10")
            
            # Comments
            with st.expander("Detailed QA Comments"):
                st.markdown(qa.comments)

        # Critique Results
        if state.get("summary_critique"):
            st.divider()
            st.markdown("### 🔍 Summary Critique")
            
            critique = state["summary_critique"]
            
            # Critique scores
            crit_cols = st.columns(3)
            with crit_cols[0]:
                st.metric("Faithfulness", f"{critique.faithfulness_score}/10")
            with crit_cols[1]:
                st.metric("Completeness", f"{critique.completeness_score}/10")
            with crit_cols[2]:
                st.metric("Conciseness", f"{critique.conciseness_score}/10")
            
            # Revision status
            if state["revision_count"] > 0:
                if critique.needs_revision:
                    st.warning(f"⚠️ Revision {state['revision_count']}/3: Summary needs improvement")
                else:
                    st.success(f"✅ Summary approved after {state['revision_count']} revision(s)")
            else:
                if critique.needs_revision:
                    st.info("ℹ️ Summary could be improved (but no revisions were made)")
                else:
                    st.success("✅ Summary approved on first attempt")
            
            # Feedback
            with st.expander("Detailed Critique Feedback"):
                st.markdown(critique.feedback)
                if critique.revision_instructions:
                    st.markdown("**Revision Instructions:**")
                    st.markdown(critique.revision_instructions)

        # Metadata
        if state.get("metadata"):
            with st.expander("Call Metadata"):
                meta = state["metadata"]
                st.write(f"**Call ID**: {meta.call_id}")
                st.write(f"**Timestamp**: {meta.timestamp}")
                if meta.duration_seconds:
                    minutes = int(meta.duration_seconds // 60)
                    seconds = int(meta.duration_seconds % 60)
                    st.write(f"**Estimated Duration**: {minutes}m {seconds}s")
                st.write(f"**Input Type**: {meta.input_type}")
                if meta.file_name:
                    st.write(f"**File**: {meta.file_name}")

        # Execution info
        with st.expander("Pipeline Execution"):
            st.write(f"**Execution Path**: {' → '.join(state['execution_path'])}")
            st.write(f"**Models Used**: {', '.join(state['models_used'])}")

        # Raw state JSON
        with st.expander("Raw State JSON"):
            st.json(state)

    else:
        st.info("Upload or select a transcript, then click 'Analyze Call' to see results.")

# ===================
# Footer
# ===================
st.divider()
st.caption("AI Call Center Assistant | Capstone Project | Phase 5 - Guardrails")
