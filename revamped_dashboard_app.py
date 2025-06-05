"""
Insurance AI System - Comprehensive Dashboard UI (Revamped & Enhanced)

A complete control tower interface for insurance operations with AI integration.
Features: Dashboard, Policy Management, Claims Processing, Analytics, Fraud Detection,
Knowledge Base, System Configuration, Notifications, User Management, and Human Escalation.

This version includes a dramatically enhanced UI with dark/light mode toggle,
advanced data visualizations, animations, and modern design patterns for a "WOW" effect.
"""

import streamlit as st
import asyncio
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import base64
from typing import Dict, Any, List, Optional
import sys
import os
import time
import random
from dataclasses import dataclass
import uuid

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import theme configuration and UI components
from theme_config import (
    initialize_theme_config, apply_theme_css, toggle_theme, 
    get_current_theme, get_theme_config, get_color_palette
)
from ui_components import (
    render_header, render_metric_card, render_alert, create_modern_chart,
    render_data_table, render_sidebar_navigation, render_progress_bar,
    render_card, render_tabs, render_status_badge, render_notification_toast,
    render_ai_confidence_indicator, render_floating_action_button,
    render_animated_counter, render_feature_card, render_gradient_card,
    render_3d_card, render_glass_card
)

# Import with error handling
try:
    from main import InsuranceAIApplication
    from config.settings import get_settings
    BACKEND_AVAILABLE = True
except ImportError as e:
    st.warning(f"Backend not fully available: {e}")
    BACKEND_AVAILABLE = False
    
    # Mock settings for standalone operation
    class MockSettings:
        def __init__(self):
            self.ai_provider = "openai"
            self.openai_api_key = None
    
    def get_settings():
        return MockSettings()

# Import AI-enhanced dashboard components
try:
    from ui.ai_enhanced_dashboard import ai_dashboard
    AI_ENHANCED_AVAILABLE = True
except ImportError as e:
    st.warning(f"AI-enhanced features not available: {e}")
    AI_ENHANCED_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Insurance AI Control Tower",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme configuration
initialize_theme_config()
apply_theme_css()

# Data Models (same as before)
@dataclass
class PolicyData:
    id: str
    customer_name: str
    policy_type: str
    status: str
    premium: float
    risk_score: float
    created_date: datetime
    ai_decision: str
    confidence: float

@dataclass
class ClaimData:
    id: str
    policy_id: str
    customer_name: str
    claim_type: str
    amount: float
    status: str
    created_date: datetime
    ai_decision: str
    fraud_score: float
    confidence: float

@dataclass
class AgentActivity:
    agent_name: str
    status: str
    current_task: str
    last_activity: datetime
    tasks_completed: int
    success_rate: float

@dataclass
class Alert:
    id: str
    type: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

if 'user_role' not in st.session_state:
    st.session_state.user_role = 'Admin'

if 'notifications' not in st.session_state:
    st.session_state.notifications = []

# Mock data generators (same as before)
def generate_mock_policies(count=50):
    policies = []
    policy_types = ['Auto', 'Home', 'Life', 'Health', 'Commercial']
    statuses = ['Active', 'Pending', 'Expired', 'Cancelled']
    for i in range(count):
        policy = PolicyData(
            id=f"POL-{1000+i}", customer_name=f"Customer {i+1}",
            policy_type=random.choice(policy_types), status=random.choice(statuses),
            premium=random.uniform(500, 5000), risk_score=random.uniform(0.1, 0.9),
            created_date=datetime.now() - timedelta(days=random.randint(1, 365)),
            ai_decision=random.choice(['Approved', 'Rejected', 'Review Required']),
            confidence=random.uniform(0.7, 0.99)
        )
        policies.append(policy)
    return policies

def generate_mock_claims(count=30):
    claims = []
    claim_types = ['Auto Accident', 'Property Damage', 'Medical', 'Theft', 'Fire']
    statuses = ['Open', 'Under Review', 'Approved', 'Denied', 'Closed']
    for i in range(count):
        claim = ClaimData(
            id=f"CLM-{2000+i}", policy_id=f"POL-{1000+random.randint(0, 49)}",
            customer_name=f"Customer {i+1}", claim_type=random.choice(claim_types),
            amount=random.uniform(1000, 50000), status=random.choice(statuses),
            created_date=datetime.now() - timedelta(days=random.randint(1, 90)),
            ai_decision=random.choice(['Approve', 'Deny', 'Investigate', 'Escalate']),
            fraud_score=random.uniform(0.0, 1.0), confidence=random.uniform(0.6, 0.95)
        )
        claims.append(claim)
    return claims

def generate_mock_agents():
    agents = [
        AgentActivity("Underwriting Agent", "Active", "Analyzing Policy POL-1023", datetime.now(), 45, 0.92),
        AgentActivity("Claims Agent", "Active", "Processing Claim CLM-2015", datetime.now(), 32, 0.88),
        AgentActivity("Fraud Detection Agent", "Idle", "Monitoring for anomalies", datetime.now() - timedelta(minutes=5), 18, 0.95),
        AgentActivity("Actuarial Agent", "Active", "Risk modeling analysis", datetime.now(), 12, 0.91),
        AgentActivity("Compliance Agent", "Error", "Connection timeout", datetime.now() - timedelta(minutes=2), 8, 0.89),
        AgentActivity("Customer Service Agent", "Active", "Handling inquiry INQ-3001", datetime.now(), 67, 0.94)
    ]
    return agents

def generate_mock_alerts():
    alerts = [
        Alert("ALT-001", "SLA Violation", "High", "Claim CLM-2008 exceeds 48-hour SLA", datetime.now() - timedelta(hours=2), False),
        Alert("ALT-002", "Fraud Detection", "Critical", "Suspicious pattern detected in claims cluster", datetime.now() - timedelta(minutes=30), False),
        Alert("ALT-003", "System", "Medium", "AI model confidence below threshold", datetime.now() - timedelta(hours=1), True),
        Alert("ALT-004", "Compliance", "High", "Regulatory filing deadline approaching", datetime.now() - timedelta(hours=4), False),
        Alert("ALT-005", "Performance", "Low", "Response time degradation detected", datetime.now() - timedelta(minutes=15), False)
    ]
    return alerts

# Navigation
def render_navigation():
    """Render the enhanced navigation sidebar"""
    theme = get_current_theme()
    palette = get_color_palette()
    
    st.sidebar.markdown("### 🏢 Insurance AI Control Tower")
    
    # Theme toggle button
    if st.sidebar.button("🌓" if theme == "light" else "☀️", key="theme_toggle_sidebar", help="Toggle dark/light mode"):
        toggle_theme()
        st.experimental_rerun() # Use experimental_rerun
    
    st.sidebar.markdown("---")
    
    # User info card
    render_glass_card(
        title=f"👤 {st.session_state.user_role}",
        content=f"Session Start: {datetime.now().strftime('%H:%M:%S')}",
        blur=5
    )
    
    st.sidebar.markdown("---")
    
    # Navigation items
    nav_items = [
        {"id": "Dashboard", "label": "Dashboard", "icon": "🏠"},
        {"id": "AI_Services", "label": "AI Services", "icon": "🤖"},
        {"id": "Policy_Management", "label": "Policy Management", "icon": "📋"},
        {"id": "Claims_Processing", "label": "Claims Processing", "icon": "⚖️"},
        {"id": "Analytics", "label": "Analytics & Risk", "icon": "📊"},
        {"id": "Fraud_Detection", "label": "Fraud Detection", "icon": "🕵️"},
        {"id": "Knowledge_Base", "label": "Knowledge Base", "icon": "📚"},
        {"id": "System_Config", "label": "System Config", "icon": "⚙️"},
        {"id": "Notifications", "label": "Notifications", "icon": "📩"},
        {"id": "User_Management", "label": "User Management", "icon": "👤"},
        {"id": "Human_Escalation", "label": "Human Escalation", "icon": "📞"}
    ]
    
    render_sidebar_navigation(nav_items, "Navigation")
    
    # Quick stats in sidebar using animated counters
    st.sidebar.markdown("### 📈 Quick Stats")
    render_animated_counter(1247, label="Active Policies", duration=1500)
    render_animated_counter(89, label="Open Claims", duration=1500)
    render_animated_counter(94.2, suffix="%", label="AI Accuracy", duration=1500)
    render_animated_counter(32.5, label="Avg Risk Score", duration=1500)

# Page Components
def render_dashboard():
    """Render the enhanced main dashboard"""
    render_header("Insurance AI Control Tower", "Real-time overview of all insurance operations")
    
    # Overview metrics using enhanced metric cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        render_metric_card("Total Policies", "1,247", "↑ 23 today", "📋")
    with col2:
        render_metric_card("Claims Processed", "89", "↑ 12 today", "⚖️")
    with col3:
        render_metric_card("Flagged Risks", "15", "↓ 3 today", "🚨")
    with col4:
        render_metric_card("Pending Reviews", "7", "→ 0 change", "⏳")
    with col5:
        render_metric_card("AI Accuracy", "94.2%", "↑ 1.2%", "🤖")
    
    # Main dashboard content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # AI Agent Activity Heatmap (using modern chart)
        st.subheader("🤖 AI Agent Activity Heatmap")
        agents = ['Underwriting', 'Claims', 'Fraud Detection', 'Actuarial', 'Compliance', 'Customer Service']
        hours = [f"{i:02d}:00" for i in range(24)]
        activity_data = [{'Agent': agent, 'Hour': hour, 'Activity': random.randint(0, 100)} for agent in agents for hour in hours]
        df_activity = pd.DataFrame(activity_data)
        pivot_data = df_activity.pivot(index='Agent', columns='Hour', values='Activity')
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=pivot_data.values, x=pivot_data.columns, y=pivot_data.index,
            colorscale='Blues', hovertemplate='Agent: %{y}<br>Hour: %{x}<br>Activity: %{z}<extra></extra>'
        ))
        theme_config = get_theme_config()
        fig_heatmap.update_layout(
            title="Agent Activity by Hour (Last 24h)", height=400,
            plot_bgcolor=theme_config["backgroundColor"], paper_bgcolor=theme_config["backgroundColor"],
            font_color=theme_config["textColor"], margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Live Agent Feed using enhanced cards
        st.subheader("📡 Live Agent Feed")
        agents = generate_mock_agents()
        for agent in agents:
            status_color = "success" if agent.status == "Active" else "warning" if agent.status == "Idle" else "danger"
            content = f"""
            <strong>Status:</strong> {agent.status}<br>
            <strong>Task:</strong> {agent.current_task}<br>
            <strong>Success Rate:</strong> {agent.success_rate:.1%}
            """
            render_3d_card(
                title=agent.agent_name,
                content=content,
                icon="👤",
                color=f"var(--{status_color}-color)"
            )
    
    with col2:
        # Alert Stream using enhanced alerts
        st.subheader("🚨 Alert Stream")
        alerts = generate_mock_alerts()
        for alert in alerts:
            alert_type = "danger" if alert.severity == "Critical" else "warning" if alert.severity == "High" else "info"
            status_icon = "✅" if alert.resolved else "🔴"
            render_alert(
                f"{status_icon} <strong>{alert.type}:</strong> {alert.message}<br><small>{alert.timestamp.strftime('%H:%M:%S')}</small>",
                alert_type, dismissible=True
            )
        
        # System Health using gradient card
        health_content = """
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <div>🟢 API Response Time: <strong>245ms</strong></div>
            <div>🟢 Database Connections: <strong>12/50</strong></div>
            <div>🟡 AI Model Latency: <strong>1.2s</strong></div>
            <div>🟢 Error Rate: <strong>0.3%</strong></div>
            <div>🟡 Memory Usage: <strong>68%</strong></div>
        </div>
        """
        render_gradient_card(
            title="💚 System Health",
            content=health_content,
            gradient_start="var(--success-color)",
            gradient_end="var(--info-color)"
        )

def render_policy_management():
    """Render enhanced policy management interface"""
    render_header("Policy & Underwriting Management", "Manage insurance policies and underwriting decisions")
    
    # Policy filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        policy_type_filter = st.selectbox("Policy Type", ["All", "Auto", "Home", "Life", "Health", "Commercial"])
    with col2:
        status_filter = st.selectbox("Status", ["All", "Active", "Pending", "Expired", "Cancelled"])
    with col3:
        risk_filter = st.selectbox("Risk Level", ["All", "Low (0-0.3)", "Medium (0.3-0.7)", "High (0.7-1.0)"])
    with col4:
        ai_decision_filter = st.selectbox("AI Decision", ["All", "Approved", "Rejected", "Review Required"])
    
    # Generate and filter policy data
    policies = generate_mock_policies()
    policy_data = [{
        'Policy ID': p.id, 'Customer': p.customer_name, 'Type': p.policy_type,
        'Status': p.status, 'Premium': f"${p.premium:,.2f}", 'Risk Score': f"{p.risk_score:.2f}",
        'AI Decision': p.ai_decision, 'Confidence': f"{p.confidence:.1%}",
        'Created Date': p.created_date.strftime("%Y-%m-%d")
    } for p in policies]
    
    df_policies = pd.DataFrame(policy_data)
    
    # Apply filters (example for status)
    if status_filter != "All":
        df_policies = df_policies[df_policies['Status'] == status_filter]
    
    # Render data table with enhanced features
    render_data_table(df_policies.to_dict('records'), 
                      columns=['Policy ID', 'Customer', 'Type', 'Status', 'Premium', 'Risk Score', 'AI Decision', 'Confidence', 'Created Date'],
                      height=500, interactive=True)
    
    # Action buttons
    st.markdown("### Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ New Policy Application"):
            render_notification_toast("Opening new policy form...", "info")
    with col2:
        if st.button("🔄 Bulk Update Status"):
            render_notification_toast("Bulk update initiated...", "info")
    with col3:
        if st.button("📄 Generate Report"):
            render_notification_toast("Generating policy report...", "info")

def render_claims_processing():
    """Render enhanced claims processing interface"""
    render_header("Claims Processing & Management", "Handle insurance claims efficiently")
    
    # Claims filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        claim_type_filter = st.selectbox("Claim Type", ["All", "Auto Accident", "Property Damage", "Medical", "Theft", "Fire"])
    with col2:
        status_filter = st.selectbox("Status", ["All", "Open", "Under Review", "Approved", "Denied", "Closed"])
    with col3:
        fraud_filter = st.selectbox("Fraud Score", ["All", "Low (0-0.3)", "Medium (0.3-0.7)", "High (0.7-1.0)"])
    with col4:
        ai_decision_filter = st.selectbox("AI Decision", ["All", "Approve", "Deny", "Investigate", "Escalate"])
    
    # Generate and filter claims data
    claims = generate_mock_claims()
    claims_data = [{
        'Claim ID': c.id, 'Policy ID': c.policy_id, 'Customer': c.customer_name,
        'Type': c.claim_type, 'Amount': f"${c.amount:,.2f}", 'Status': c.status,
        'Fraud Score': f"{c.fraud_score:.2f}", 'AI Decision': c.ai_decision,
        'Confidence': f"{c.confidence:.1%}", 'Created Date': c.created_date.strftime("%Y-%m-%d")
    } for c in claims]
    
    df_claims = pd.DataFrame(claims_data)
    
    # Apply filters (example for status)
    if status_filter != "All":
        df_claims = df_claims[df_claims['Status'] == status_filter]
    
    # Render data table
    render_data_table(df_claims.to_dict('records'), 
                      columns=['Claim ID', 'Policy ID', 'Customer', 'Type', 'Amount', 'Status', 'Fraud Score', 'AI Decision', 'Confidence', 'Created Date'],
                      height=500, interactive=True)
    
    # Action buttons
    st.markdown("### Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ New Claim Submission"):
            render_notification_toast("Opening new claim form...", "info")
    with col2:
        if st.button("🔍 Initiate Investigation"):
            render_notification_toast("Investigation process started...", "warning")
    with col3:
        if st.button("✅ Approve Selected"):
            render_notification_toast("Selected claims approved.", "success")

def render_analytics():
    """Render enhanced analytics and risk dashboard"""
    render_header("Analytics & Risk Insights", "Visualize trends and assess risks")
    
    # Tabs for different analytics views
    tabs_data = [
        {"label": "📈 Performance Metrics", "content": render_performance_analytics},
        {"label": "📉 Risk Analysis", "content": render_risk_analytics},
        {"label": "🗺️ Geographic Insights", "content": render_geo_analytics}
    ]
    render_tabs(tabs_data)

def render_performance_analytics():
    """Render performance metrics section"""
    st.subheader("Key Performance Indicators")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # Example Line Chart
        df_perf = pd.DataFrame({
            'Month': pd.to_datetime(['2024-01', '2024-02', '2024-03', '2024-04', '2024-05']),
            'Policies Issued': [180, 210, 195, 230, 250],
            'Claims Processed': [60, 75, 70, 85, 90]
        })
        fig_perf = create_modern_chart(df_perf, 'line', x='Month', y=['Policies Issued', 'Claims Processed'], 
                                     title="Monthly Performance Trends")
        st.plotly_chart(fig_perf, use_container_width=True)
    
    with col2:
        # Example Bar Chart
        df_types = pd.DataFrame({
            'Policy Type': ['Auto', 'Home', 'Life', 'Health'],
            'Count': [550, 320, 180, 197]
        })
        fig_types = create_modern_chart(df_types, 'bar', x='Policy Type', y='Count', 
                                      title="Policies by Type")
        st.plotly_chart(fig_types, use_container_width=True)
    
    with col3:
        # Example Pie Chart
        df_status = pd.DataFrame({
            'Status': ['Active', 'Pending', 'Expired', 'Cancelled'],
            'Count': [1247, 85, 45, 23]
        })
        fig_status = create_modern_chart(df_status, 'pie', x='Status', y='Count', 
                                       title="Policy Status Distribution")
        st.plotly_chart(fig_status, use_container_width=True)

def render_risk_analytics():
    """Render risk analysis section"""
    st.subheader("Risk Assessment Overview")
    
    col1, col2 = st.columns(2)
    with col1:
        # Risk Score Distribution
        policies = generate_mock_policies()
        df_risk = pd.DataFrame([p.risk_score for p in policies], columns=['Risk Score'])
        fig_risk_dist = create_modern_chart(df_risk, 'histogram', x='Risk Score', 
                                          title="Policy Risk Score Distribution")
        st.plotly_chart(fig_risk_dist, use_container_width=True)
    
    with col2:
        # High Risk Policies
        high_risk_policies = [p for p in policies if p.risk_score >= 0.7]
        render_card(
            title="🚨 High Risk Policies",
            content=f"Number of policies with risk score > 0.7: **{len(high_risk_policies)}**",
            footer="Review recommended",
            icon="⚠️",
            color="var(--danger-color)"
        )
        if high_risk_policies:
            st.dataframe(pd.DataFrame([{'ID': p.id, 'Score': f"{p.risk_score:.2f}"} for p in high_risk_policies[:5]]), 
                         use_container_width=True)

def render_geo_analytics():
    """Render geographic insights section"""
    st.subheader("Geographic Distribution")
    
    # Mock geo data
    data = {'State': ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI'],
            'Policies': [150, 120, 100, 90, 80, 70, 60, 55, 50, 45],
            'Claims': [30, 25, 20, 18, 15, 12, 10, 9, 8, 7],
            'AvgRisk': [0.65, 0.55, 0.60, 0.70, 0.50, 0.45, 0.52, 0.68, 0.58, 0.62]}
    df_geo = pd.DataFrame(data)
    
    # Example Choropleth Map
    fig_map = go.Figure(data=go.Choropleth(
        locations=df_geo['State'],
        z=df_geo['Policies'].astype(float),
        locationmode='USA-states',
        colorscale='Blues',
        colorbar_title="Policies",
        marker_line_color='darkgray',
        marker_line_width=0.5,
    ))
    
    theme_config = get_theme_config()
    fig_map.update_layout(
        title_text='Policy Distribution by State',
        geo_scope='usa',
        plot_bgcolor=theme_config["backgroundColor"],
        paper_bgcolor=theme_config["backgroundColor"],
        font_color=theme_config["textColor"],
        margin={"r":0,"t":30,"l":0,"b":0}
    )
    st.plotly_chart(fig_map, use_container_width=True)

def render_fraud_detection():
    """Render enhanced fraud detection interface"""
    render_header("AI-Powered Fraud Detection", "Identify and investigate suspicious activities")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Fraud Score Overview
        claims = generate_mock_claims()
        fraud_scores = [c.fraud_score for c in claims]
        avg_fraud_score = sum(fraud_scores) / len(fraud_scores) if claims else 0
        high_fraud_claims = len([c for c in claims if c.fraud_score >= 0.7])
        
        render_gradient_card(
            title="Fraud Score Summary",
            content=f"""
            Average Fraud Score: <strong>{avg_fraud_score:.2f}</strong><br>
            High Risk Claims (>0.7): <strong>{high_fraud_claims}</strong>
            """,
            gradient_start="var(--warning-color)",
            gradient_end="var(--danger-color)"
        )
        
        # AI Confidence
        render_ai_confidence_indicator(random.uniform(0.85, 0.98), size="large")
    
    with col2:
        # Fraud Score Distribution Chart
        df_fraud = pd.DataFrame(fraud_scores, columns=['Fraud Score'])
        fig_fraud_dist = create_modern_chart(df_fraud, 'histogram', x='Fraud Score', 
                                           title="Claim Fraud Score Distribution")
        st.plotly_chart(fig_fraud_dist, use_container_width=True)
    
    # High Fraud Score Claims Table
    st.subheader("Claims Flagged for High Fraud Risk (Score > 0.7)")
    high_fraud_claims_data = [{
        'Claim ID': c.id, 'Customer': c.customer_name, 'Amount': f"${c.amount:,.2f}",
        'Fraud Score': f"{c.fraud_score:.2f}", 'AI Decision': c.ai_decision
    } for c in claims if c.fraud_score >= 0.7]
    
    render_data_table(high_fraud_claims_data, height=300, interactive=True)

def render_knowledge_base():
    """Render knowledge base interface"""
    render_header("Knowledge Base & Documentation", "Access guidelines, policies, and AI insights")
    
    search_query = st.text_input("🔍 Search Knowledge Base", placeholder="Enter keywords like 'underwriting guidelines' or 'fraud patterns'...")
    
    if search_query:
        st.write(f"Searching for: **{search_query}**")
        # Mock search results
        time.sleep(0.5) # Simulate search time
        results = [
            {"title": f"Guideline: {search_query} Best Practices", "type": "Guideline", "relevance": 0.92},
            {"title": f"Policy Document: Section on {search_query}", "type": "Policy", "relevance": 0.85},
            {"title": f"AI Insight: Common patterns related to {search_query}", "type": "AI Insight", "relevance": 0.78}
        ]
        for result in results:
            render_card(
                title=result["title"],
                content=f"Type: {result['type']} | Relevance: {result['relevance']:.1%}",
                footer="Click to view details",
                icon="📄"
            )
    else:
        # Feature cards for common sections
        st.subheader("Browse Categories")
        col1, col2, col3 = st.columns(3)
        with col1:
            render_feature_card("Underwriting Guidelines", "Access standard procedures for policy underwriting.", "📝", color="var(--info-color)")
        with col2:
            render_feature_card("Claims Procedures", "Step-by-step guide for processing various claim types.", "⚖️", color="var(--success-color)")
        with col3:
            render_feature_card("Fraud Indicators", "Common red flags and patterns identified by AI.", "🕵️", color="var(--warning-color)")

def render_system_config():
    """Render system configuration interface"""
    render_header("System Configuration & Settings", "Manage AI models, integrations, and system parameters")
    
    settings = get_settings()
    
    tabs_data = [
        {"label": "🤖 AI Model Settings", "content": lambda: render_ai_config(settings)},
        {"label": "🔌 Integrations", "content": render_integrations_config},
        {"label": "🔧 General Settings", "content": render_general_config}
    ]
    render_tabs(tabs_data)

def render_ai_config(settings):
    """Render AI model configuration section"""
    st.subheader("AI Provider & Model Selection")
    ai_provider = st.selectbox("AI Provider", ["openai", "anthropic", "google"], index=["openai", "anthropic", "google"].index(settings.ai_provider))
    
    if ai_provider == "openai":
        api_key = st.text_input("OpenAI API Key", type="password", value=settings.openai_api_key or "")
        model = st.selectbox("Model", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
    # Add similar sections for other providers
    
    st.subheader("Confidence Thresholds")
    col1, col2, col3 = st.columns(3)
    with col1:
        underwriting_threshold = st.slider("Underwriting Auto-Approval", 0.0, 1.0, 0.85, 0.01)
    with col2:
        claims_threshold = st.slider("Claims Auto-Approval", 0.0, 1.0, 0.80, 0.01)
    with col3:
        fraud_threshold = st.slider("Fraud Investigation Trigger", 0.0, 1.0, 0.70, 0.01)
        
    if st.button("💾 Save AI Settings"):
        # Logic to save settings (update config files or database)
        render_notification_toast("AI settings saved successfully!", "success")

def render_integrations_config():
    """Render integrations configuration section"""
    st.subheader("Third-Party Integrations")
    
    render_card("CRM Integration (Salesforce)", "Status: <span style='color: var(--success-color);'>Connected</span>", icon="🔗", color="var(--info-color)")
    render_card("Payment Gateway (Stripe)", "Status: <span style='color: var(--success-color);'>Connected</span>", icon="💳", color="var(--success-color)")
    render_card("Communication Platform (Twilio)", "Status: <span style='color: var(--danger-color);'>Disconnected</span>", icon="📞", color="var(--warning-color)")
    
    if st.button("⚙️ Manage Integrations"):
        render_notification_toast("Opening integration management panel...", "info")

def render_general_config():
    """Render general system settings section"""
    st.subheader("General Application Settings")
    
    app_name = st.text_input("Application Name", "Insurance AI Control Tower")
    default_timezone = st.selectbox("Default Timezone", ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"])
    session_timeout = st.number_input("Session Timeout (minutes)", 1, 120, 30)
    
    if st.button("💾 Save General Settings"):
        # Logic to save general settings
        render_notification_toast("General settings saved successfully!", "success")

def render_notifications():
    """Render notifications center"""
    render_header("Notifications & Alerts Center", "View and manage system notifications")
    
    st.subheader("Recent Notifications")
    notifications = st.session_state.notifications + generate_mock_alerts() # Combine session and mock
    
    filter_type = st.selectbox("Filter by Type", ["All", "SLA Violation", "Fraud Detection", "System", "Compliance", "Performance"])
    
    filtered_notifications = notifications
    if filter_type != "All":
        filtered_notifications = [n for n in notifications if n.type == filter_type]
        
    if not filtered_notifications:
        st.info("No notifications match the current filter.")
    else:
        for notification in filtered_notifications:
            alert_type = "danger" if notification.severity == "Critical" else "warning" if notification.severity == "High" else "info"
            status_icon = "✅" if notification.resolved else "🔴"
            render_alert(
                f"{status_icon} [{notification.severity}] {notification.type}: {notification.message}<br><small>{notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</small>",
                alert_type,
                dismissible=True
            )

def render_user_management():
    """Render user management interface"""
    render_header("User Management", "Manage users, roles, and permissions")
    
    # Mock user data
    users = [
        {"Username": "admin", "Role": "Admin", "Last Login": datetime.now() - timedelta(hours=1), "Status": "Active"},
        {"Username": "j.doe", "Role": "Underwriter", "Last Login": datetime.now() - timedelta(days=1), "Status": "Active"},
        {"Username": "s.smith", "Role": "Claims Adjuster", "Last Login": datetime.now() - timedelta(hours=3), "Status": "Active"},
        {"Username": "r.jones", "Role": "Analyst", "Last Login": datetime.now() - timedelta(days=2), "Status": "Inactive"}
    ]
    
    users_data = [{
        'Username': u['Username'], 'Role': u['Role'], 
        'Last Login': u['Last Login'].strftime('%Y-%m-%d %H:%M'),
        'Status': u['Status']
    } for u in users]
    
    render_data_table(users_data, height=300, interactive=True)
    
    st.subheader("Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add New User"):
            render_notification_toast("Opening add user form...", "info")
    with col2:
        if st.button("✏️ Edit Selected User"):
            render_notification_toast("Opening edit user form...", "info")
    with col3:
        if st.button("🔑 Manage Roles & Permissions"):
            render_notification_toast("Opening role management...", "info")

def render_human_escalation():
    """Render human escalation queue"""
    render_header("Human Escalation Queue", "Review cases requiring manual intervention")
    
    # Mock escalation data
    escalations = [
        {"Case ID": "ESC-001", "Type": "Complex Claim", "Reason": "High value, multiple parties", "Assigned To": "Senior Adjuster", "Status": "Pending Review"},
        {"Case ID": "ESC-002", "Type": "Policy Exception", "Reason": "Non-standard coverage request", "Assigned To": "Underwriting Manager", "Status": "Pending Review"},
        {"Case ID": "ESC-003", "Type": "Fraud Investigation", "Reason": "AI flagged high probability", "Assigned To": "Fraud Specialist", "Status": "In Progress"}
    ]
    
    escalations_data = [{
        'Case ID': e['Case ID'], 'Type': e['Type'], 'Reason': e['Reason'],
        'Assigned To': e['Assigned To'], 'Status': e['Status']
    } for e in escalations]
    
    render_data_table(escalations_data, height=400, interactive=True)
    
    st.subheader("Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 View Case Details"):
            render_notification_toast("Loading case details...", "info")
    with col2:
        if st.button("👤 Assign Case"):
            render_notification_toast("Opening case assignment dialog...", "info")

def render_ai_services():
    """Render AI Services overview page"""
    render_header("AI Services Hub", "Explore and manage AI capabilities")
    
    st.write("Overview of available AI agents, models, and their performance.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        render_feature_card(
            title="Underwriting AI",
            description="Automates risk assessment and policy pricing.",
            icon="📝", color="var(--info-color)",
            button_text="View Details", button_key="underwriting_ai"
        )
    with col2:
        render_feature_card(
            title="Claims Processing AI",
            description="Accelerates claim validation and settlement.",
            icon="⚖️", color="var(--success-color)",
            button_text="View Details", button_key="claims_ai"
        )
    with col3:
        render_feature_card(
            title="Fraud Detection AI",
            description="Identifies suspicious patterns and anomalies.",
            icon="🕵️", color="var(--warning-color)",
            button_text="View Details", button_key="fraud_ai"
        )
        
    st.subheader("Overall AI Performance")
    # Add charts or metrics related to overall AI performance
    df_ai_perf = pd.DataFrame({
        'Metric': ['Accuracy', 'Latency (ms)', 'Throughput (req/s)'],
        'Value': [94.2, 850, 15.5]
    })
    st.dataframe(df_ai_perf, use_container_width=True)

# Main application logic
def main():
    """Main application function"""
    render_navigation()
    
    # Floating Action Button (Example: New Claim)
    if render_floating_action_button("➕", tooltip="Submit New Claim", action_key="new_claim"):
        st.session_state.current_page = 'Claims_Processing'
        render_notification_toast("Navigating to New Claim submission...", "info")
        st.experimental_rerun()
    
    # Page routing
    page = st.session_state.current_page
    
    if page == 'Dashboard':
        render_dashboard()
    elif page == 'Policy_Management':
        render_policy_management()
    elif page == 'Claims_Processing':
        render_claims_processing()
    elif page == 'Analytics':
        render_analytics()
    elif page == 'Fraud_Detection':
        render_fraud_detection()
    elif page == 'Knowledge_Base':
        render_knowledge_base()
    elif page == 'System_Config':
        render_system_config()
    elif page == 'Notifications':
        render_notifications()
    elif page == 'User_Management':
        render_user_management()
    elif page == 'Human_Escalation':
        render_human_escalation()
    elif page == 'AI_Services':
        render_ai_services()
    else:
        st.error("Page not found!")
        render_dashboard() # Default to dashboard

if __name__ == "__main__":
    main()
