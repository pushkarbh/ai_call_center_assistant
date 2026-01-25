"""
Agent interaction visualizer - shows what data each agent contributed
"""

import streamlit as st
from typing import Dict, Any

def render_agent_interactions(state: Dict[str, Any]):
    """Render a detailed view of agent interactions and state contributions
    
    Args:
        state: Final workflow state with all agent contributions
    """
    
    st.markdown("### 🔗 Agent Interactions & State Flow")
    st.caption("Shows all agents and their execution status")
    
    execution_path = state.get("execution_path", [])
    errors = state.get("errors", [])
    
    # Define ALL possible agents in the workflow
    all_agents = [
        "validation",
        "intake", 
        "transcription",
        "abuse_detection",
        "summarization",
        "critic",
        "qa_scoring"
    ]
    
    # Define what each agent contributes to state
    agent_contributions = {
        "validation": {
            "icon": "🛡️",
            "name": "Input Validation",
            "reads": ["raw_input"],
            "writes": ["validation_result"],
            "decision": "Continue or Stop workflow"
        },
        "intake": {
            "icon": "📥",
            "name": "Intake Agent",
            "reads": ["raw_input", "validation_result"],
            "writes": ["intake_metadata"],
            "decision": None
        },
        "transcription": {
            "icon": "📝",
            "name": "Transcription Agent",
            "reads": ["raw_input", "input_type"],
            "writes": ["transcript"],
            "decision": None
        },
        "abuse_detection": {
            "icon": "🚨",
            "name": "Abuse Detection",
            "reads": ["transcript"],
            "writes": ["abuse_flags"],
            "decision": None
        },
        "summarization": {
            "icon": "📋",
            "name": "Summarization Agent",
            "reads": ["transcript", "critic_feedback (if revision)"],
            "writes": ["summary"],
            "decision": None
        },
        "critic": {
            "icon": "🔍",
            "name": "Critic Agent",
            "reads": ["summary", "transcript"],
            "writes": ["critique", "needs_revision", "revision_count"],
            "decision": "Revise or Continue to QA"
        },
        "qa_scoring": {
            "icon": "📊",
            "name": "QA Scoring",
            "reads": ["summary", "transcript"],
            "writes": ["qa_scores"],
            "decision": None
        }
    }
    
    # Create visual flow for ALL agents
    for i, agent_id in enumerate(all_agents):
        agent_info = agent_contributions.get(agent_id, {
            "icon": "❓",
            "name": agent_id,
            "reads": [],
            "writes": [],
            "decision": None
        })
        
        # Determine execution status
        was_executed = agent_id in execution_path
        execution_count = execution_path.count(agent_id) if was_executed else 0
        has_error = any(agent_id in str(err) for err in errors)
        
        # Color coding based on status
        if not was_executed:
            # Not executed - gray/disabled
            status_emoji = "⚪"
            status_text = "Not Executed"
            bg_color = "#f5f5f5"
            border_color = "#cccccc"
            text_color = "#999999"
        elif has_error:
            # Error - red
            status_emoji = "❌"
            status_text = "Error"
            bg_color = "#ffebee"
            border_color = "#f44336"
            text_color = "#c62828"
        else:
            # Success - green
            status_emoji = "✅"
            status_text = "Success"
            if execution_count > 1:
                status_text += f" (x{execution_count})"
            bg_color = "#e8f5e9"
            border_color = "#4caf50"
            text_color = "#2e7d32"
        
        # Create styled card
        with st.container():
            st.markdown(
                f"""
                <div style="
                    background-color: {bg_color};
                    border-left: 5px solid {border_color};
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                ">
                    <h4 style="color: {text_color}; margin: 0;">
                        {status_emoji} {agent_info['icon']} {agent_info['name']}
                    </h4>
                    <p style="color: {text_color}; margin: 5px 0; font-size: 0.9em;">
                        <strong>Status:</strong> {status_text}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Show details only for executed agents
            if was_executed:
                with st.expander("📋 View Details", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📖 Reads:**")
                        for item in agent_info['reads']:
                            st.caption(f"• {item}")
                    
                    with col2:
                        st.markdown("**✍️ Writes:**")
                        for item in agent_info['writes']:
                            st.caption(f"• {item}")
                    
                    if agent_info['decision']:
                        st.markdown(f"**🎯 Decision:** {agent_info['decision']}")
                    
                    # Show actual data if available
                    if agent_id == "validation" and state.get("validation_result"):
                        validation = state["validation_result"]
                        st.json({
                            "is_valid": validation.is_valid,
                            "confidence": validation.confidence,
                            "issues": validation.issues
                        })
                    
                    elif agent_id == "abuse_detection" and state.get("abuse_flags"):
                        st.caption(f"Detected {len(state['abuse_flags'])} abuse flag(s)")
                    
                    elif agent_id == "critic" and state.get("critique"):
                        critique = state["critique"]
                        st.caption(f"Scores: Faithfulness={critique.faithfulness_score}, "
                                  f"Completeness={critique.completeness_score}, "
                                  f"Conciseness={critique.conciseness_score}")
                        if state.get("needs_revision"):
                            st.warning("🔄 Needs Revision")
        
        # Show arrow between agents (only between executed ones or showing skip)
        if i < len(all_agents) - 1:
            next_agent_id = all_agents[i + 1]
            
            if was_executed and next_agent_id in execution_path:
                # Check for revision loop
                if agent_id == "critic" and execution_path.count("summarization") > 1:
                    st.markdown("**↩️ Revision Loop ↩️**")
                else:
                    st.markdown("**⬇️**")
            elif was_executed and next_agent_id not in execution_path:
                st.markdown("**⏸️ Workflow stopped**")
            elif not was_executed:
                st.markdown("**· · ·** _(skipped)_")
    
    # Summary statistics
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Agents", len(all_agents))
    
    with col2:
        executed = len(set(execution_path))
        st.metric("Executed", executed, delta=None)
    
    with col3:
        skipped = len(all_agents) - len(set(execution_path))
        st.metric("Skipped", skipped, delta=None)
    
    with col4:
        revision_count = execution_path.count("summarization") - 1 if execution_path.count("summarization") > 0 else 0
        st.metric("Revisions", revision_count)
