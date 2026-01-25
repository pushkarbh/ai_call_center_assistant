"""
Workflow visualization component using streamlit-flow-component
Shows the agent execution flow in an n8n-style diagram
"""

import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout

def create_workflow_nodes(execution_path=None, current_step=None):
    """Create nodes for the workflow visualization
    
    Args:
        execution_path: List of agent names that have been executed
        current_step: Current agent being executed
    """
    
    # Define all possible nodes in the workflow
    nodes = [
        StreamlitFlowNode(
            id="validation",
            pos=(100, 50),
            data={"label": "🛡️ Validation"},
            node_type="input",
            source_position="right",
            target_position="left",
            style={"background": "#e3f2fd", "border": "2px solid #2196f3"}
        ),
        StreamlitFlowNode(
            id="intake",
            pos=(300, 50),
            data={"label": "📥 Intake"},
            node_type="default",
            source_position="right",
            target_position="left",
            style={"background": "#f3e5f5", "border": "2px solid #9c27b0"}
        ),
        StreamlitFlowNode(
            id="transcription",
            pos=(500, 50),
            data={"label": "📝 Transcription"},
            node_type="default",
            source_position="right",
            target_position="left",
            style={"background": "#fff3e0", "border": "2px solid #ff9800"}
        ),
        StreamlitFlowNode(
            id="abuse_detection",
            pos=(700, 50),
            data={"label": "🚨 Abuse Detection"},
            node_type="default",
            source_position="right",
            target_position="left",
            style={"background": "#ffebee", "border": "2px solid #f44336"}
        ),
        StreamlitFlowNode(
            id="summarization",
            pos=(900, 50),
            data={"label": "📋 Summarization"},
            node_type="default",
            source_position="right",
            target_position="left",
            style={"background": "#e8f5e9", "border": "2px solid #4caf50"}
        ),
        StreamlitFlowNode(
            id="critic",
            pos=(1100, 50),
            data={"label": "🔍 Critic"},
            node_type="default",
            source_position="bottom",
            target_position="left",
            style={"background": "#fce4ec", "border": "2px solid #e91e63"}
        ),
        StreamlitFlowNode(
            id="qa_scoring",
            pos=(1300, 50),
            data={"label": "📊 QA Scoring"},
            node_type="output",
            source_position="right",
            target_position="left",
            style={"background": "#f1f8e9", "border": "2px solid #8bc34a"}
        ),
    ]
    
    # Update node styles based on execution status
    if execution_path:
        for node in nodes:
            if node.id in execution_path:
                if current_step and node.id == current_step:
                    # Currently executing
                    node.style["border"] = "3px solid #ffd700"
                    node.style["boxShadow"] = "0 0 10px #ffd700"
                else:
                    # Completed
                    node.style["opacity"] = "1"
                    node.style["border"] = "2px solid #4caf50"
            else:
                # Not yet executed
                node.style["opacity"] = "0.4"
    
    return nodes

def create_workflow_edges(execution_path=None):
    """Create edges connecting the workflow nodes
    
    Args:
        execution_path: List of agent names that have been executed
    """
    
    edges = [
        StreamlitFlowEdge(
            id="validation-intake",
            source="validation",
            target="intake",
            animated=False,
            style={"stroke": "#2196f3"}
        ),
        StreamlitFlowEdge(
            id="intake-transcription",
            source="intake",
            target="transcription",
            animated=False,
            style={"stroke": "#9c27b0"}
        ),
        StreamlitFlowEdge(
            id="transcription-abuse",
            source="transcription",
            target="abuse_detection",
            animated=False,
            style={"stroke": "#ff9800"}
        ),
        StreamlitFlowEdge(
            id="abuse-summarization",
            source="abuse_detection",
            target="summarization",
            animated=False,
            style={"stroke": "#f44336"}
        ),
        StreamlitFlowEdge(
            id="summarization-critic",
            source="summarization",
            target="critic",
            animated=False,
            style={"stroke": "#4caf50"}
        ),
        StreamlitFlowEdge(
            id="critic-qa",
            source="critic",
            target="qa_scoring",
            animated=False,
            style={"stroke": "#e91e63"}
        ),
        # Revision loop edge (from critic back to summarization)
        StreamlitFlowEdge(
            id="critic-summarization-loop",
            source="critic",
            target="summarization",
            animated=True,
            label="Needs Revision",
            style={"stroke": "#ff5722", "strokeDasharray": "5,5"},
            edge_type="smoothstep"
        ),
    ]
    
    # Animate edges for executed path
    if execution_path:
        for i in range(len(execution_path) - 1):
            source = execution_path[i]
            target = execution_path[i + 1]
            
            # Find and animate the edge
            for edge in edges:
                if edge.source == source and edge.target == target:
                    edge.animated = True
                    edge.style["stroke"] = "#4caf50"
                    edge.style["strokeWidth"] = "3"
    
    return edges

def render_workflow_visualization(execution_path=None, current_step=None):
    """Render the workflow visualization
    
    Args:
        execution_path: List of agent names executed so far
        current_step: Current agent being executed
    """
    
    st.markdown("### 🔄 Workflow Execution")
    
    nodes = create_workflow_nodes(execution_path, current_step)
    edges = create_workflow_edges(execution_path)
    
    # Create the flow state
    flow_state = StreamlitFlowState(nodes=nodes, edges=edges)
    
    # Render the flow
    streamlit_flow(
        key="workflow_flow",
        state=flow_state,
        fit_view=True,
        height=250,
        enable_node_menu=False,
        enable_edge_menu=False,
        enable_pane_menu=False,
        get_node_on_click=False,
        get_edge_on_click=False,
        allow_new_edges=False,
        animate_new_edges=True,
        hide_watermark=True,
    )
    
    # Show execution status
    if execution_path:
        st.caption(f"**Execution Path**: {' → '.join(execution_path)}")
        
        # Check for revision loops
        revision_count = execution_path.count("summarization") - 1
        if revision_count > 0:
            st.caption(f"🔄 **Revisions**: {revision_count} iteration(s)")
