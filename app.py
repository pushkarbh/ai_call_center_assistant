import streamlit as st

st.set_page_config(
    page_title="Call Center Assistant",
    page_icon="📞",
    layout="wide"
)

st.title("📞 AI Call Center Assistant")
st.markdown("**Phase 0**: Deployment Verification")

st.divider()

# Simple health check display
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Status", "Online", delta="Healthy")

with col2:
    st.metric("Phase", "0", delta="Initial")

with col3:
    st.metric("Platform", "HF Spaces")

st.divider()

st.success("✅ App successfully deployed to Hugging Face Spaces!")

st.info("""
**Next Steps (Phase 1):**
- Install all dependencies
- Verify LangChain, LangGraph, Whisper imports
- Create UI skeleton
""")

# Footer
st.divider()
st.caption("AI Call Center Assistant | Capstone Project | Phase 0")
