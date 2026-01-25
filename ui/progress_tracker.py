"""
Real-time workflow progress tracker
Shows live execution status as agents run
"""

import streamlit as st
from typing import List, Optional

def create_progress_tracker(container, total_steps: int = 7):
    """Create a progress tracker that can be updated in real-time
    
    Args:
        container: Streamlit container to render into
        total_steps: Total number of steps in the workflow
        
    Returns:
        Dictionary of placeholder elements for each step
    """
    
    steps = [
        {"id": "validation", "name": "🛡️ Validation", "color": "#2196f3"},
        {"id": "intake", "name": "📥 Intake", "color": "#9c27b0"},
        {"id": "transcription", "name": "📝 Transcription", "color": "#ff9800"},
        {"id": "abuse_detection", "name": "🚨 Abuse Detection", "color": "#f44336"},
        {"id": "summarization", "name": "📋 Summarization", "color": "#4caf50"},
        {"id": "critic", "name": "🔍 Critic", "color": "#e91e63"},
        {"id": "qa_scoring", "name": "📊 QA Scoring", "color": "#8bc34a"},
    ]
    
    with container:
        st.markdown("### 🔄 Workflow Progress")
        
        # Create status placeholders for each step
        placeholders = {}
        for step in steps:
            col1, col2 = st.columns([3, 1])
            with col1:
                placeholders[f"{step['id']}_name"] = st.empty()
            with col2:
                placeholders[f"{step['id']}_status"] = st.empty()
            
            # Initial state
            placeholders[f"{step['id']}_name"].markdown(
                f"<span style='color: #999'>{step['name']}</span>",
                unsafe_allow_html=True
            )
            placeholders[f"{step['id']}_status"].markdown("⏸️ Pending")
        
        placeholders["progress_bar"] = st.empty()
        placeholders["progress_text"] = st.empty()
        
    return placeholders, steps

def update_step_status(placeholders, steps, step_id: str, status: str = "running"):
    """Update the status of a specific step
    
    Args:
        placeholders: Dictionary of placeholder elements
        steps: List of step configurations
        step_id: ID of the step to update
        status: 'running', 'completed', 'error'
    """
    
    step = next((s for s in steps if s['id'] == step_id), None)
    if not step:
        return
    
    status_icons = {
        "running": "⚙️",
        "completed": "✅",
        "error": "❌",
        "pending": "⏸️"
    }
    
    status_colors = {
        "running": "#ffd700",
        "completed": step['color'],
        "error": "#f44336",
        "pending": "#999"
    }
    
    icon = status_icons.get(status, "⏸️")
    color = status_colors.get(status, "#999")
    
    # Update step name with color
    placeholders[f"{step_id}_name"].markdown(
        f"<span style='color: {color}; font-weight: bold'>{step['name']}</span>",
        unsafe_allow_html=True
    )
    
    # Update status
    if status == "running":
        placeholders[f"{step_id}_status"].markdown(f"{icon} Running...")
    elif status == "completed":
        placeholders[f"{step_id}_status"].markdown(f"{icon} Done")
    elif status == "error":
        placeholders[f"{step_id}_status"].markdown(f"{icon} Error")

def update_progress(placeholders, completed_steps: int, total_steps: int, current_step: str = ""):
    """Update the overall progress bar
    
    Args:
        placeholders: Dictionary of placeholder elements
        completed_steps: Number of completed steps
        total_steps: Total number of steps
        current_step: Name of current step
    """
    
    progress = completed_steps / total_steps
    placeholders["progress_bar"].progress(progress)
    
    if current_step:
        placeholders["progress_text"].caption(f"Processing: {current_step} ({completed_steps}/{total_steps})")
    else:
        placeholders["progress_text"].caption(f"Completed: {completed_steps}/{total_steps}")
