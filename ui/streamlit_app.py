"""
Enhanced Streamlit UI for the Insurance AI System.
Provides a web interface for interacting with the AI-enhanced insurance platform.
"""

import os
import json
import time
import uuid
import requests
import asyncio
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add project root to path for AI integration
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import AI components
try:
    from main import InsuranceAIApplication
    from config.settings import get_settings
    AI_AVAILABLE = True
except ImportError as e:
    st.warning(f"AI components not available: {e}")
    AI_AVAILABLE = False

# API configuration
API_URL = os.environ.get("API_URL", "http://localhost:8080")

# Set page configuration
st.set_page_config(
    page_title="Insurance AI System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #1E3A8A;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .status-pending {
        color: #FFA500;
        font-weight: bold;
    }
    .status-success {
        color: #008000;
        font-weight: bold;
    }
    .status-failure {
        color: #FF0000;
        font-weight: bold;
    }
    .info-box {
        background-color: #F0F2F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 0.3rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2E4A9A;
    }
</style>
""", unsafe_allow_html=True)


# Session state initialization
if "institution_id" not in st.session_state:
    st.session_state.institution_id = ""
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "selected_task" not in st.session_state:
    st.session_state.selected_task = None
if "report_content" not in st.session_state:
    st.session_state.report_content = None


def get_institutions() -> List[str]:
    """
    Get list of available institutions.
    
    Returns:
        List of institution IDs
    """
    # In a real implementation, this would call the API
    # For now, return a static list
    return ["institution_a", "institution_b", "institution_c"]


def api_request(endpoint: str, method: str = "GET", data: Dict = None, 
                headers: Dict = None) -> Dict:
    """
    Make a request to the API.
    
    Args:
        endpoint: API endpoint
        method: HTTP method
        data: Request data
        headers: Request headers
        
    Returns:
        API response
    """
    if headers is None:
        headers = {}
    
    if st.session_state.institution_id:
        headers["X-Institution-ID"] = st.session_state.institution_id
    
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                st.error(f"Error details: {error_data.get('detail', 'Unknown error')}")
            except:
                st.error(f"Status code: {e.response.status_code}")
        return {"status": "error", "message": str(e)}


def get_task_status(task_id: str) -> Dict:
    """
    Get the status of a task.
    
    Args:
        task_id: Task ID
        
    Returns:
        Task status
    """
    return api_request(f"/status/{task_id}")


def get_report(report_id: str) -> Dict:
    """
    Get a report.
    
    Args:
        report_id: Report ID
        
    Returns:
        Report data
    """
    return api_request(f"/report/{report_id}")


def run_underwriting(data: Dict) -> Dict:
    """
    Run underwriting analysis.
    
    Args:
        data: Underwriting data
        
    Returns:
        API response
    """
    return api_request("/run/underwriting", method="POST", data=data)


def run_claims(data: Dict) -> Dict:
    """
    Run claims processing.
    
    Args:
        data: Claims data
        
    Returns:
        API response
    """
    return api_request("/run/claims", method="POST", data=data)


def run_actuarial(data: Dict) -> Dict:
    """
    Run actuarial analysis.
    
    Args:
        data: Actuarial data
        
    Returns:
        API response
    """
    return api_request("/run/actuarial", method="POST", data=data)


# AI Integration Functions
@st.cache_resource
def initialize_ai_system():
    """Initialize the AI system (cached for performance)."""
    if not AI_AVAILABLE:
        return None
    
    try:
        app = InsuranceAIApplication()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(app.initialize())
        return app
    except Exception as e:
        st.error(f"Failed to initialize AI system: {e}")
        return None


def run_ai_analysis(analysis_type: str, data: Dict) -> Dict:
    """
    Run AI analysis using the integrated AI system.
    
    Args:
        analysis_type: Type of analysis (underwriting, claims, actuarial)
        data: Input data for analysis
        
    Returns:
        Analysis results
    """
    if not AI_AVAILABLE:
        return {"status": "error", "message": "AI system not available"}
    
    app = initialize_ai_system()
    if not app:
        return {"status": "error", "message": "Failed to initialize AI system"}
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if analysis_type == "underwriting":
            result = loop.run_until_complete(app.run_underwriting_analysis(data))
        elif analysis_type == "claims":
            result = loop.run_until_complete(app.run_claims_analysis(data))
        elif analysis_type == "actuarial":
            result = loop.run_until_complete(app.run_actuarial_analysis(data))
        else:
            return {"status": "error", "message": f"Unknown analysis type: {analysis_type}"}
        
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_ai_system_status() -> Dict:
    """Get AI system status and configuration."""
    if not AI_AVAILABLE:
        return {"available": False, "message": "AI components not loaded"}
    
    try:
        settings = get_settings()
        app = initialize_ai_system()
        
        return {
            "available": True,
            "provider": settings.ai.provider,
            "model": settings.ai.model,
            "initialized": app is not None,
            "health": "healthy" if app else "unhealthy"
        }
    except Exception as e:
        return {"available": False, "message": str(e)}


def update_task_list():
    """Update the task list in the session state."""
    # In a real implementation, this would call the API to get all tasks
    # For now, just refresh the status of existing tasks
    updated_tasks = []
    for task in st.session_state.tasks:
        task_id = task.get("task_id")
        if task_id:
            status_response = get_task_status(task_id)
            if status_response.get("status") == "success":
                updated_tasks.append(status_response)
            else:
                updated_tasks.append(task)
    
    st.session_state.tasks = updated_tasks


def render_sidebar():
    """Render the sidebar."""
    with st.sidebar:
        st.markdown('<div class="main-header">Insurance AI System</div>', unsafe_allow_html=True)
        
        # AI System Status
        st.markdown('<div class="section-header">🤖 AI System Status</div>', unsafe_allow_html=True)
        ai_status = get_ai_system_status()
        
        if ai_status["available"]:
            st.success("✅ AI System Online")
            st.info(f"Provider: {ai_status.get('provider', 'Unknown').upper()}")
            st.info(f"Model: {ai_status.get('model', 'Unknown')}")
            st.info(f"Health: {ai_status.get('health', 'Unknown').title()}")
        else:
            st.warning("⚠️ AI System Offline")
            st.error(ai_status.get("message", "Unknown error"))
        
        # Institution selector
        st.markdown('<div class="section-header">Institution</div>', unsafe_allow_html=True)
        institutions = get_institutions()
        selected_institution = st.selectbox(
            "Select Institution",
            institutions,
            index=0 if not st.session_state.institution_id else institutions.index(st.session_state.institution_id)
        )
        
        if st.button("Set Institution"):
            st.session_state.institution_id = selected_institution
            st.success(f"Institution set to: {selected_institution}")
        
        # Task list
        st.markdown('<div class="section-header">Recent Tasks</div>', unsafe_allow_html=True)
        
        if st.button("Refresh Tasks"):
            update_task_list()
        
        if not st.session_state.tasks:
            st.info("No tasks yet. Submit a request to create a task.")
        else:
            for i, task in enumerate(st.session_state.tasks):
                task_id = task.get("task_id", "Unknown")
                task_type = task.get("task_type", "Unknown")
                status = task.get("status", "PENDING")
                
                # Determine status class
                if status == "SUCCESS":
                    status_class = "status-success"
                elif status in ["FAILURE", "REVOKED"]:
                    status_class = "status-failure"
                else:
                    status_class = "status-pending"
                
                # Create a clickable task item
                if st.button(
                    f"{task_type.capitalize()}: {task_id[:8]}... - "
                    f"<span class='{status_class}'>{status}</span>",
                    key=f"task_{i}",
                    help=f"View details for task {task_id}",
                    use_container_width=True
                ):
                    st.session_state.selected_task = task
                    st.session_state.report_content = None
                    
                    # If task has a report, fetch it
                    if status == "SUCCESS" and task.get("report_id"):
                        report_response = get_report(task.get("report_id"))
                        if report_response.get("status") == "success":
                            st.session_state.report_content = report_response


def render_underwriting_form():
    """Render the underwriting form."""
    st.markdown('<div class="section-header">Underwriting Application</div>', unsafe_allow_html=True)
    
    with st.form("underwriting_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            applicant_id = st.text_input("Applicant ID", value=f"UW-{uuid.uuid4().hex[:8].upper()}")
            full_name = st.text_input("Full Name", value="Alice Example")
            address = st.text_input("Address", value="123 Main St")
            date_of_birth = st.date_input("Date of Birth")
        
        with col2:
            income = st.number_input("Annual Income", value=80000)
            credit_score = st.number_input("Credit Score", value=720)
            debt_to_income_ratio = st.number_input("Debt to Income Ratio", value=0.3, format="%.2f")
            address_location_tag = st.selectbox(
                "Address Location Tag",
                ["SafeZoneA", "SafeZoneB", "SafeZoneC", "RiskZoneA", "RiskZoneB"]
            )
        
        document_text = st.text_area(
            "Document Text (OCR)",
            value="Name: Alice Example\nDOB: 01/01/1990\nOther info..."
        )
        
        # Analysis options
        st.markdown("### Analysis Options")
        col1, col2 = st.columns(2)
        
        with col1:
            use_ai_analysis = st.checkbox("🤖 Use AI Analysis", value=True, help="Enable AI-powered risk assessment")
        
        with col2:
            analysis_mode = st.selectbox(
                "Analysis Mode",
                ["Standard API", "Direct AI", "Both"],
                help="Choose how to process the application"
            )
        
        submitted = st.form_submit_button("Submit Underwriting Application")
        
        if submitted:
            if not st.session_state.institution_id:
                st.error("Please select an institution first.")
                return
            
            # Prepare data
            data = {
                "institution_id": st.session_state.institution_id,
                "applicant_id": applicant_id,
                "full_name": full_name,
                "address": address,
                "date_of_birth": date_of_birth.strftime("%m/%d/%Y"),
                "income": income,
                "credit_score": int(credit_score),
                "debt_to_income_ratio": debt_to_income_ratio,
                "address_location_tag": address_location_tag,
                "document_text": document_text
            }
            
            # Process based on analysis mode
            if analysis_mode in ["Direct AI", "Both"] and use_ai_analysis:
                st.info("🤖 Running AI analysis...")
                ai_result = run_ai_analysis("underwriting", data)
                
                if ai_result["status"] == "success":
                    st.success("✅ AI Analysis Complete!")
                    
                    # Display AI results
                    with st.expander("🤖 AI Analysis Results"):
                        result = ai_result["result"]
                        st.json(result)
                        
                        if hasattr(result, 'content'):
                            st.markdown("**AI Assessment:**")
                            st.write(result.content)
                else:
                    st.error(f"AI Analysis failed: {ai_result['message']}")
            
            if analysis_mode in ["Standard API", "Both"]:
                # Submit to standard API
                response = run_underwriting(data)
                
                if response.get("status") == "success":
                    st.success(f"Underwriting task created: {response.get('task_id')}")
                    
                    # Add task to list
                    task = {
                        "task_id": response.get("task_id"),
                        "task_type": "underwriting",
                        "status": "PENDING",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    st.session_state.tasks.insert(0, task)
                else:
                    st.error(f"Failed to create underwriting task: {response.get('message')}")


def render_claims_form():
    """Render the claims form."""
    st.markdown('<div class="section-header">Claims Processing</div>', unsafe_allow_html=True)
    
    with st.form("claims_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            claim_id = st.text_input("Claim ID", value=f"CL-{uuid.uuid4().hex[:8].upper()}")
            policy_id = st.text_input("Policy ID", value=f"POL-{uuid.uuid4().hex[:6].upper()}")
            claimant_name = st.text_input("Claimant Name", value="Bob Example")
        
        with col2:
            incident_date = st.date_input("Incident Date")
            claim_amount = st.number_input("Claim Amount", value=5000)
        
        incident_description = st.text_area(
            "Incident Description",
            value="Water damage from burst pipe in kitchen."
        )
        
        submitted = st.form_submit_button("Submit Claim")
        
        if submitted:
            if not st.session_state.institution_id:
                st.error("Please select an institution first.")
                return
            
            # Prepare data
            data = {
                "institution_id": st.session_state.institution_id,
                "claim_id": claim_id,
                "policy_id": policy_id,
                "claimant_name": claimant_name,
                "incident_date": incident_date.strftime("%Y-%m-%d"),
                "claim_amount": claim_amount,
                "incident_description": incident_description
            }
            
            # Submit request
            response = run_claims(data)
            
            if response.get("status") == "success":
                st.success(f"Claims task created: {response.get('task_id')}")
                
                # Add task to list
                task = {
                    "task_id": response.get("task_id"),
                    "task_type": "claims",
                    "status": "PENDING",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                st.session_state.tasks.insert(0, task)
            else:
                st.error(f"Failed to create claims task: {response.get('message')}")


def render_actuarial_form():
    """Render the actuarial form."""
    st.markdown('<div class="section-header">Actuarial Analysis</div>', unsafe_allow_html=True)
    
    with st.form("actuarial_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_id = st.text_input("Analysis ID", value=f"ACT-{uuid.uuid4().hex[:8].upper()}")
            data_type = st.selectbox(
                "Data Type",
                ["demographic", "claims_history", "risk_factors", "market_trends"]
            )
        
        with col2:
            age_group = st.selectbox(
                "Age Group",
                ["18-25", "26-35", "36-45", "46-55", "56-65", "66+"]
            )
            region = st.selectbox(
                "Region",
                ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
            )
            coverage_type = st.selectbox(
                "Coverage Type",
                ["basic", "standard", "premium", "comprehensive"]
            )
        
        # Parameters
        st.markdown("### Analysis Parameters")
        confidence_level = st.slider("Confidence Level", 0.8, 0.99, 0.95, 0.01, format="%.2f")
        time_horizon = st.selectbox("Time Horizon", ["3m", "6m", "1y", "2y", "5y"])
        
        submitted = st.form_submit_button("Run Actuarial Analysis")
        
        if submitted:
            if not st.session_state.institution_id:
                st.error("Please select an institution first.")
                return
            
            # Prepare data
            data = {
                "institution_id": st.session_state.institution_id,
                "analysis_id": analysis_id,
                "data_source": {
                    "type": data_type,
                    "age_group": age_group,
                    "region": region,
                    "coverage_type": coverage_type
                },
                "parameters": {
                    "confidence_level": confidence_level,
                    "time_horizon": time_horizon
                }
            }
            
            # Submit request
            response = run_actuarial(data)
            
            if response.get("status") == "success":
                st.success(f"Actuarial task created: {response.get('task_id')}")
                
                # Add task to list
                task = {
                    "task_id": response.get("task_id"),
                    "task_type": "actuarial",
                    "status": "PENDING",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                st.session_state.tasks.insert(0, task)
            else:
                st.error(f"Failed to create actuarial task: {response.get('message')}")


def render_task_details():
    """Render task details."""
    task = st.session_state.selected_task
    
    if not task:
        return
    
    st.markdown('<div class="section-header">Task Details</div>', unsafe_allow_html=True)
    
    # Create columns for task details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Task ID:** {task.get('task_id')}")
        st.markdown(f"**Type:** {task.get('task_type', 'Unknown').capitalize()}")
        st.markdown(f"**Status:** {task.get('status', 'Unknown')}")
    
    with col2:
        st.markdown(f"**Created:** {task.get('created_at', 'Unknown')}")
        st.markdown(f"**Updated:** {task.get('updated_at', 'Unknown')}")
        if task.get("report_id"):
            st.markdown(f"**Report ID:** {task.get('report_id')}")
    
    # Show result or error
    if task.get("status") == "SUCCESS" and task.get("result"):
        st.markdown("### Result")
        st.json(task.get("result"))
    elif task.get("status") == "FAILURE" and task.get("error"):
        st.error(f"Task failed: {task.get('error')}")
    
    # Show report content if available
    if st.session_state.report_content:
        st.markdown("### Report")
        report = st.session_state.report_content
        
        # Display report content
        st.markdown(f"**Report ID:** {report.get('report_id')}")
        st.markdown(f"**Type:** {report.get('report_type', 'Unknown').capitalize()}")
        st.markdown(f"**Created:** {report.get('created_at', 'Unknown')}")
        
        # Display report content
        content = report.get("content", {})
        
        if content:
            # Check if there's a title
            if "title" in content:
                st.markdown(f"## {content['title']}")
            
            # Display content as JSON
            st.json(content)
            
            # If there are visualizable elements, create charts
            if report.get("report_type") == "actuarial" and "data_points" in content:
                try:
                    data_points = content["data_points"]
                    df = pd.DataFrame(data_points)
                    
                    st.markdown("### Visualization")
                    
                    # Create a chart based on the data
                    if "value" in df.columns and "category" in df.columns:
                        fig = px.bar(df, x="category", y="value", title="Analysis Results")
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not create visualization: {str(e)}")


def render_status_panel():
    """Render the status panel."""
    st.markdown('<div class="section-header">Status Panel</div>', unsafe_allow_html=True)
    
    # Create a placeholder for the status
    status_placeholder = st.empty()
    
    # Check if there are any tasks
    if not st.session_state.tasks:
        with status_placeholder.container():
            st.info("No tasks have been submitted yet.")
        return
    
    # Get the most recent task
    latest_task = st.session_state.tasks[0]
    
    # Update the status
    with status_placeholder.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Active Tasks",
                len([t for t in st.session_state.tasks if t.get("status") in ["PENDING", "STARTED"]])
            )
        
        with col2:
            st.metric(
                "Completed Tasks",
                len([t for t in st.session_state.tasks if t.get("status") == "SUCCESS"])
            )
        
        with col3:
            st.metric(
                "Failed Tasks",
                len([t for t in st.session_state.tasks if t.get("status") in ["FAILURE", "REVOKED"]])
            )
        
        # Show latest task status
        st.markdown(f"**Latest Task:** {latest_task.get('task_type', 'Unknown').capitalize()} - "
                   f"{latest_task.get('task_id')}")
        
        # Create a progress bar for pending tasks
        if latest_task.get("status") in ["PENDING", "STARTED"]:
            st.progress(50, text="Processing...")
        elif latest_task.get("status") == "SUCCESS":
            st.success("Task completed successfully")
        else:
            st.error(f"Task failed: {latest_task.get('error', 'Unknown error')}")


def main():
    """Main function."""
    # Render sidebar
    render_sidebar()

    st.markdown(
        '<div class="main-header">Welcome to the Insurance AI Platform</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "Use the tabs below to submit underwriting applications, manage claims, "
        "and run actuarial analyses. Start by selecting your institution in the sidebar."
    )

    # Main content
    if not st.session_state.institution_id:
        st.warning("Please select an institution from the sidebar to continue.")
        return
    
    # Create tabs for different functions
    tab1, tab2, tab3, tab4 = st.tabs([
        "Status Dashboard", "Underwriting", "Claims", "Actuarial"
    ])
    
    with tab1:
        # Status dashboard
        render_status_panel()
        
        # Task details if a task is selected
        if st.session_state.selected_task:
            render_task_details()
    
    with tab2:
        # Underwriting form
        render_underwriting_form()
    
    with tab3:
        # Claims form
        render_claims_form()
    
    with tab4:
        # Actuarial form
        render_actuarial_form()


if __name__ == "__main__":
    main()
