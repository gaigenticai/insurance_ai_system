"""
Insurance AI System - Comprehensive Dashboard UI (Revamped)

A complete control tower interface for insurance operations with AI integration.
Features: Dashboard, Policy Management, Claims Processing, Analytics, Fraud Detection,
Knowledge Base, System Configuration, Notifications, User Management, and Human Escalation.

This version includes a modern UI with dark/light mode toggle and enhanced data visualizations.
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
from theme_config import initialize_theme_config, apply_theme_css, render_theme_toggle, toggle_theme, get_current_theme, get_theme_config, get_color_palette
from ui_components import (
    render_header, render_metric_card, render_alert, create_modern_chart,
    render_data_table, render_sidebar_navigation, render_progress_bar,
    render_card, render_tabs, render_status_badge, render_notification_toast,
    render_ai_confidence_indicator
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

# Data Models
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

# Mock data generators
def generate_mock_policies(count=50):
    """Generate mock policy data"""
    policies = []
    policy_types = ['Auto', 'Home', 'Life', 'Health', 'Commercial']
    statuses = ['Active', 'Pending', 'Expired', 'Cancelled']
    
    for i in range(count):
        policy = PolicyData(
            id=f"POL-{1000+i}",
            customer_name=f"Customer {i+1}",
            policy_type=random.choice(policy_types),
            status=random.choice(statuses),
            premium=random.uniform(500, 5000),
            risk_score=random.uniform(0.1, 0.9),
            created_date=datetime.now() - timedelta(days=random.randint(1, 365)),
            ai_decision=random.choice(['Approved', 'Rejected', 'Review Required']),
            confidence=random.uniform(0.7, 0.99)
        )
        policies.append(policy)
    
    return policies

def generate_mock_claims(count=30):
    """Generate mock claims data"""
    claims = []
    claim_types = ['Auto Accident', 'Property Damage', 'Medical', 'Theft', 'Fire']
    statuses = ['Open', 'Under Review', 'Approved', 'Denied', 'Closed']
    
    for i in range(count):
        claim = ClaimData(
            id=f"CLM-{2000+i}",
            policy_id=f"POL-{1000+random.randint(0, 49)}",
            customer_name=f"Customer {i+1}",
            claim_type=random.choice(claim_types),
            amount=random.uniform(1000, 50000),
            status=random.choice(statuses),
            created_date=datetime.now() - timedelta(days=random.randint(1, 90)),
            ai_decision=random.choice(['Approve', 'Deny', 'Investigate', 'Escalate']),
            fraud_score=random.uniform(0.0, 1.0),
            confidence=random.uniform(0.6, 0.95)
        )
        claims.append(claim)
    
    return claims

def generate_mock_agents():
    """Generate mock agent activity data"""
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
    """Generate mock alerts"""
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
    """Render the navigation sidebar"""
    theme = get_current_theme()
    
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    
    # Theme toggle in sidebar
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        st.markdown("### 🏢 Insurance AI Control Tower")
    with col2:
        if st.button("🌓" if theme == "light" else "☀️", help="Toggle dark/light mode"):
            toggle_theme()
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # User info
    st.sidebar.markdown(f"**User:** {st.session_state.user_role}")
    st.sidebar.markdown(f"**Session:** {datetime.now().strftime('%H:%M:%S')}")
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
    
    # Quick stats in sidebar
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown("### 📈 Quick Stats")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Active Policies", "1,247", "↑ 23")
        st.metric("AI Accuracy", "94.2%", "↑ 1.2%")
    with col2:
        st.metric("Open Claims", "89", "↓ 5")
        st.metric("Risk Score", "32.5", "↓ 2.1")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Page Components
def render_dashboard():
    """Render the main dashboard"""
    render_header("Insurance AI Control Tower", "Real-time overview of all insurance operations")
    
    # Overview metrics
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
        # AI Agent Activity Heatmap
        st.subheader("🤖 AI Agent Activity Heatmap")
        
        # Generate heatmap data
        agents = ['Underwriting', 'Claims', 'Fraud Detection', 'Actuarial', 'Compliance', 'Customer Service']
        hours = [f"{i:02d}:00" for i in range(24)]
        
        # Create random activity data
        activity_data = []
        for agent in agents:
            for hour in hours:
                activity_data.append({
                    'Agent': agent,
                    'Hour': hour,
                    'Activity': random.randint(0, 100)
                })
        
        df_activity = pd.DataFrame(activity_data)
        pivot_data = df_activity.pivot(index='Agent', columns='Hour', values='Activity')
        
        # Create modern chart
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='Blues',
            hovertemplate='Agent: %{y}<br>Hour: %{x}<br>Activity: %{z}<extra></extra>'
        ))
        
        # Apply theme-aware styling
        theme_config = get_theme_config()
        palette = get_color_palette()
        
        fig_heatmap.update_layout(
            title="Agent Activity by Hour (Last 24h)",
            height=400,
            plot_bgcolor=theme_config["backgroundColor"],
            paper_bgcolor=theme_config["backgroundColor"],
            font_color=theme_config["textColor"],
            margin=dict(l=10, r=10, t=50, b=10),
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Live Agent Feed
        st.subheader("📡 Live Agent Feed")
        agents = generate_mock_agents()
        
        for agent in agents:
            status_color = "success" if agent.status == "Active" else "warning" if agent.status == "Idle" else "danger"
            
            content = f"""
            <strong>{agent.agent_name}</strong> - {agent.status}<br>
            <small>{agent.current_task} | Success Rate: {agent.success_rate:.1%}</small>
            """
            
            render_card(
                title=agent.agent_name,
                content=content,
                footer=f"Last activity: {(datetime.now() - agent.last_activity).seconds // 60} minutes ago",
                icon="👤",
                color=f"var(--{status_color}-color)"
            )
    
    with col2:
        # Alert Stream
        st.subheader("🚨 Alert Stream")
        alerts = generate_mock_alerts()
        
        for alert in alerts:
            alert_type = "danger" if alert.severity == "Critical" else "warning" if alert.severity == "High" else "info"
            status_icon = "✅" if alert.resolved else "🔴"
            
            render_alert(
                f"{status_icon} {alert.type}: {alert.message}<br><small>{alert.timestamp.strftime('%H:%M:%S')}</small>",
                alert_type,
                dismissible=True
            )
        
        # System Health
        render_card(
            title="💚 System Health",
            content="""
            <div class="health-metrics">
                <div class="health-metric">
                    <span class="health-icon good">🟢</span>
                    <span class="health-label">API Response Time:</span>
                    <span class="health-value">245ms</span>
                </div>
                <div class="health-metric">
                    <span class="health-icon good">🟢</span>
                    <span class="health-label">Database Connections:</span>
                    <span class="health-value">12/50</span>
                </div>
                <div class="health-metric">
                    <span class="health-icon warning">🟡</span>
                    <span class="health-label">AI Model Latency:</span>
                    <span class="health-value">1.2s</span>
                </div>
                <div class="health-metric">
                    <span class="health-icon good">🟢</span>
                    <span class="health-label">Error Rate:</span>
                    <span class="health-value">0.3%</span>
                </div>
                <div class="health-metric">
                    <span class="health-icon warning">🟡</span>
                    <span class="health-label">Memory Usage:</span>
                    <span class="health-value">68%</span>
                </div>
            </div>
            
            <style>
            .health-metrics {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .health-metric {
                display: flex;
                align-items: center;
            }
            
            .health-icon {
                margin-right: 0.5rem;
            }
            
            .health-label {
                flex: 1;
                font-weight: 500;
            }
            
            .health-value {
                font-family: monospace;
            }
            </style>
            """,
            footer="Last updated: just now",
            icon="📊"
        )

def render_policy_management():
    """Render policy management interface"""
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
        'Policy ID': p.id,
        'Customer': p.customer_name,
        'Type': p.policy_type,
        'Status': p.status,
        'Premium': f"${p.premium:,.2f}",
        'Risk Score': f"{p.risk_score:.2f}",
        'AI Decision': p.ai_decision,
        'Confidence': f"{p.confidence:.1%}",
        'Created': p.created_date.strftime('%Y-%m-%d')
    } for p in policies]
    
    # Policy viewer with search and modern table
    st.subheader("🔍 Policy Search & Viewer")
    render_data_table(policy_data, interactive=True)
    
    # Policy details and analytics
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Underwriting Decision Analysis")
        
        # Create sample data for decision analysis
        decision_data = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=30, freq='D'),
            'Approved': [random.randint(5, 20) for _ in range(30)],
            'Rejected': [random.randint(1, 8) for _ in range(30)],
            'Review Required': [random.randint(2, 10) for _ in range(30)]
        })
        
        # Create modern chart
        fig = create_modern_chart(
            decision_data,
            'area',
            'Date',
            ['Approved', 'Rejected', 'Review Required'],
            'Underwriting Decisions Over Time'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Risk Distribution")
        
        # Create sample data for risk distribution
        risk_data = pd.DataFrame({
            'Risk Level': ['Low', 'Medium', 'High'],
            'Count': [random.randint(30, 50), random.randint(15, 30), random.randint(5, 15)]
        })
        
        # Create modern chart
        fig = create_modern_chart(
            risk_data,
            'pie',
            'Risk Level',
            'Count',
            'Risk Level Distribution'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_claims_processing():
    """Render claims processing interface"""
    render_header("Claims Processing", "Process and analyze insurance claims")
    
    # Claims filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        claim_type_filter = st.selectbox("Claim Type", ["All", "Auto Accident", "Property Damage", "Medical", "Theft", "Fire"])
    with col2:
        status_filter = st.selectbox("Status", ["All", "Open", "Under Review", "Approved", "Denied", "Closed"])
    with col3:
        fraud_risk_filter = st.selectbox("Fraud Risk", ["All", "Low (0-0.3)", "Medium (0.3-0.7)", "High (0.7-1.0)"])
    with col4:
        ai_decision_filter = st.selectbox("AI Decision", ["All", "Approve", "Deny", "Investigate", "Escalate"])
    
    # Generate and filter claims data
    claims = generate_mock_claims()
    claim_data = [{
        'Claim ID': c.id,
        'Policy ID': c.policy_id,
        'Customer': c.customer_name,
        'Type': c.claim_type,
        'Amount': f"${c.amount:,.2f}",
        'Status': c.status,
        'AI Decision': c.ai_decision,
        'Fraud Score': f"{c.fraud_score:.2f}",
        'Confidence': f"{c.confidence:.1%}",
        'Created': c.created_date.strftime('%Y-%m-%d')
    } for c in claims]
    
    # Claims viewer with search and modern table
    st.subheader("🔍 Claims Search & Viewer")
    render_data_table(claim_data, interactive=True)
    
    # Claims analytics
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Claims by Type")
        
        # Create sample data for claims by type
        claims_by_type = pd.DataFrame({
            'Type': ['Auto Accident', 'Property Damage', 'Medical', 'Theft', 'Fire'],
            'Count': [random.randint(10, 30) for _ in range(5)]
        })
        
        # Create modern chart
        fig = create_modern_chart(
            claims_by_type,
            'bar',
            'Type',
            'Count',
            'Claims by Type'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⏱️ Processing Time")
        
        # Create sample data for processing time
        processing_time = pd.DataFrame({
            'Type': ['Auto Accident', 'Property Damage', 'Medical', 'Theft', 'Fire'],
            'Days': [random.uniform(1, 10) for _ in range(5)]
        })
        
        # Create modern chart
        fig = create_modern_chart(
            processing_time,
            'bar',
            'Type',
            'Days',
            'Average Processing Time (Days)'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_analytics():
    """Render analytics interface"""
    render_header("Analytics & Risk", "Advanced analytics and risk assessment")
    
    # Create tabs for different analytics views
    tabs = [
        {
            "label": "Business Overview",
            "content": render_business_overview
        },
        {
            "label": "Risk Analysis",
            "content": render_risk_analysis
        },
        {
            "label": "Performance Metrics",
            "content": render_performance_metrics
        },
        {
            "label": "Predictive Models",
            "content": render_predictive_models
        }
    ]
    
    render_tabs(tabs)

def render_business_overview():
    """Render business overview analytics"""
    # Key performance indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Revenue", "$1.24M", "↑ 12% YoY", "💰")
    with col2:
        render_metric_card("Claims Ratio", "68.3%", "↓ 2.1% YoY", "📉")
    with col3:
        render_metric_card("Customer Growth", "+156", "↑ 8% YoY", "👥")
    with col4:
        render_metric_card("Avg Premium", "$842", "↑ 5% YoY", "💵")
    
    # Business trends
    st.subheader("📈 Business Performance Trends")
    
    # Create sample data for business trends
    dates = pd.date_range(start='2024-01-01', periods=12, freq='M')
    business_data = pd.DataFrame({
        'Date': dates,
        'Revenue': [random.uniform(900000, 1300000) for _ in range(12)],
        'Expenses': [random.uniform(700000, 900000) for _ in range(12)],
        'Profit': [random.uniform(100000, 400000) for _ in range(12)]
    })
    
    # Create modern chart
    fig = create_modern_chart(
        business_data,
        'line',
        'Date',
        ['Revenue', 'Expenses', 'Profit'],
        'Financial Performance (Last 12 Months)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Policy distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Policy Distribution by Type")
        
        # Create sample data for policy distribution
        policy_dist = pd.DataFrame({
            'Type': ['Auto', 'Home', 'Life', 'Health', 'Commercial'],
            'Count': [random.randint(200, 500) for _ in range(5)]
        })
        
        # Create modern chart
        fig = create_modern_chart(
            policy_dist,
            'pie',
            'Type',
            'Count',
            'Policy Distribution'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🌍 Geographic Distribution")
        
        # Create sample data for geographic distribution
        geo_dist = pd.DataFrame({
            'Region': ['North', 'South', 'East', 'West', 'Central'],
            'Policies': [random.randint(100, 400) for _ in range(5)],
            'Claims': [random.randint(20, 100) for _ in range(5)]
        })
        
        # Create modern chart
        fig = create_modern_chart(
            geo_dist,
            'bar',
            'Region',
            ['Policies', 'Claims'],
            'Geographic Distribution'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_risk_analysis():
    """Render risk analysis analytics"""
    st.subheader("🎯 Risk Score Distribution")
    
    # Create sample data for risk distribution
    risk_scores = [random.uniform(0, 1) for _ in range(1000)]
    risk_df = pd.DataFrame({
        'Risk Score': risk_scores
    })
    
    # Create modern chart
    fig = create_modern_chart(
        risk_df,
        'histogram',
        'Risk Score',
        'count',
        'Risk Score Distribution'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk factors
    st.subheader("🔍 Key Risk Factors")
    
    # Create sample data for risk factors
    risk_factors = pd.DataFrame({
        'Factor': ['Age', 'Location', 'Claim History', 'Credit Score', 'Coverage Level', 'Vehicle Type', 'Property Value'],
        'Importance': [random.uniform(0.5, 1.0) for _ in range(7)]
    })
    
    risk_factors = risk_factors.sort_values('Importance', ascending=False)
    
    # Create modern chart
    fig = create_modern_chart(
        risk_factors,
        'bar',
        'Factor',
        'Importance',
        'Risk Factor Importance'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk trends
    st.subheader("📈 Risk Trends Over Time")
    
    # Create sample data for risk trends
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    risk_trends = pd.DataFrame({
        'Date': dates,
        'Average Risk Score': [random.uniform(0.3, 0.6) for _ in range(30)],
        'High Risk Policies': [random.randint(10, 30) for _ in range(30)]
    })
    
    # Create modern chart
    fig = create_modern_chart(
        risk_trends,
        'line',
        'Date',
        ['Average Risk Score', 'High Risk Policies'],
        'Risk Metrics Over Time'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_performance_metrics():
    """Render performance metrics analytics"""
    # Performance KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Processing Time", "1.8 days", "↓ 0.3 days", "⏱️")
    with col2:
        render_metric_card("Approval Rate", "78.2%", "↑ 2.4%", "✅")
    with col3:
        render_metric_card("AI Accuracy", "94.2%", "↑ 1.2%", "🤖")
    with col4:
        render_metric_card("Customer Satisfaction", "4.7/5", "↑ 0.2", "😊")
    
    # Performance by department
    st.subheader("📊 Performance by Department")
    
    # Create sample data for department performance
    departments = ['Underwriting', 'Claims', 'Customer Service', 'Fraud Detection', 'Actuarial']
    dept_perf = pd.DataFrame({
        'Department': departments,
        'Efficiency': [random.uniform(0.7, 0.95) for _ in range(len(departments))],
        'Accuracy': [random.uniform(0.8, 0.98) for _ in range(len(departments))],
        'Volume': [random.randint(50, 500) for _ in range(len(departments))]
    })
    
    # Create modern chart
    fig = create_modern_chart(
        dept_perf,
        'scatter',
        'Efficiency',
        'Accuracy',
        'Department Performance'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # AI vs Human performance
    st.subheader("🤖 AI vs Human Performance")
    
    # Create sample data for AI vs Human
    metrics = ['Speed', 'Accuracy', 'Consistency', 'Cost Efficiency', 'Customer Satisfaction']
    ai_human = pd.DataFrame({
        'Metric': metrics,
        'AI': [random.uniform(0.7, 0.95) for _ in range(len(metrics))],
        'Human': [random.uniform(0.6, 0.9) for _ in range(len(metrics))]
    })
    
    # Create modern chart
    fig = create_modern_chart(
        ai_human,
        'bar',
        'Metric',
        ['AI', 'Human'],
        'AI vs Human Performance'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_predictive_models():
    """Render predictive models analytics"""
    st.subheader("🔮 Predictive Models Performance")
    
    # Create sample data for model performance
    models = ['Risk Assessment', 'Fraud Detection', 'Premium Pricing', 'Customer Churn', 'Claims Estimation']
    model_perf = pd.DataFrame({
        'Model': models,
        'Accuracy': [random.uniform(0.8, 0.95) for _ in range(len(models))],
        'Precision': [random.uniform(0.75, 0.9) for _ in range(len(models))],
        'Recall': [random.uniform(0.7, 0.9) for _ in range(len(models))],
        'F1 Score': [random.uniform(0.75, 0.92) for _ in range(len(models))]
    })
    
    # Display as modern table
    render_data_table(model_perf.to_dict('records'))
    
    # Forecast
    st.subheader("📈 Business Forecast")
    
    # Create sample data for forecast
    future_dates = pd.date_range(start='2024-07-01', periods=12, freq='M')
    forecast_data = pd.DataFrame({
        'Date': future_dates,
        'Predicted Revenue': [random.uniform(1000000, 1500000) for _ in range(12)],
        'Predicted Claims': [random.uniform(600000, 900000) for _ in range(12)],
        'Confidence Interval': [random.uniform(0.05, 0.15) for _ in range(12)]
    })
    
    # Create modern chart with confidence intervals
    fig = go.Figure()
    
    # Add predicted revenue line
    fig.add_trace(go.Scatter(
        x=forecast_data['Date'],
        y=forecast_data['Predicted Revenue'],
        mode='lines+markers',
        name='Predicted Revenue',
        line=dict(color='rgba(59, 130, 246, 0.8)', width=3)
    ))
    
    # Add upper confidence interval
    fig.add_trace(go.Scatter(
        x=forecast_data['Date'],
        y=forecast_data['Predicted Revenue'] * (1 + forecast_data['Confidence Interval']),
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add lower confidence interval
    fig.add_trace(go.Scatter(
        x=forecast_data['Date'],
        y=forecast_data['Predicted Revenue'] * (1 - forecast_data['Confidence Interval']),
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(59, 130, 246, 0.2)',
        name='Confidence Interval',
        hoverinfo='skip'
    ))
    
    # Apply theme-aware styling
    theme_config = get_theme_config()
    
    fig.update_layout(
        title='12-Month Revenue Forecast with Confidence Intervals',
        height=400,
        plot_bgcolor=theme_config["backgroundColor"],
        paper_bgcolor=theme_config["backgroundColor"],
        font_color=theme_config["textColor"],
        xaxis_title='Date',
        yaxis_title='Revenue ($)',
        hovermode='x unified',
        margin=dict(l=10, r=10, t=50, b=10),
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_fraud_detection():
    """Render fraud detection interface"""
    render_header("Fraud Detection", "AI-powered fraud detection and analysis")
    
    # Fraud metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Fraud Cases", "28", "↑ 3 this month", "🚨")
    with col2:
        render_metric_card("Detection Rate", "96.3%", "↑ 1.2%", "🔍")
    with col3:
        render_metric_card("False Positives", "2.1%", "↓ 0.4%", "✓")
    with col4:
        render_metric_card("Savings", "$342K", "↑ $28K", "💰")
    
    # Fraud risk map
    st.subheader("🗺️ Fraud Risk Heatmap")
    
    # Create sample data for fraud heatmap
    fraud_data = []
    for i in range(100):
        fraud_data.append({
            'Latitude': random.uniform(25, 48),
            'Longitude': random.uniform(-125, -70),
            'Risk Score': random.uniform(0, 1)
        })
    
    fraud_df = pd.DataFrame(fraud_data)
    
    # Create modern chart
    fig = px.density_mapbox(
        fraud_df,
        lat='Latitude',
        lon='Longitude',
        z='Risk Score',
        radius=20,
        center=dict(lat=37, lon=-95),
        zoom=3,
        mapbox_style="carto-darkmatter" if get_current_theme() == "dark" else "carto-positron"
    )
    
    # Apply theme-aware styling
    theme_config = get_theme_config()
    
    fig.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=theme_config["backgroundColor"]
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Fraud detection details
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 Recent Fraud Alerts")
        
        # Sample fraud alerts
        fraud_alerts = [
            {
                "id": "FRD-001",
                "policy": "POL-1042",
                "type": "Multiple Claims",
                "risk_score": 0.87,
                "status": "Under Investigation",
                "detected": datetime.now() - timedelta(hours=3)
            },
            {
                "id": "FRD-002",
                "policy": "POL-1126",
                "type": "Identity Mismatch",
                "risk_score": 0.92,
                "status": "Confirmed Fraud",
                "detected": datetime.now() - timedelta(hours=12)
            },
            {
                "id": "FRD-003",
                "policy": "POL-1078",
                "type": "Suspicious Documentation",
                "risk_score": 0.76,
                "status": "Under Investigation",
                "detected": datetime.now() - timedelta(days=1)
            },
            {
                "id": "FRD-004",
                "policy": "POL-1215",
                "type": "Unusual Claim Pattern",
                "risk_score": 0.81,
                "status": "Escalated",
                "detected": datetime.now() - timedelta(days=2)
            }
        ]
        
        for alert in fraud_alerts:
            content = f"""
            <div class="fraud-alert-details">
                <div><strong>Policy:</strong> {alert['policy']}</div>
                <div><strong>Type:</strong> {alert['type']}</div>
                <div><strong>Status:</strong> {alert['status']}</div>
                <div><strong>Detected:</strong> {alert['detected'].strftime('%Y-%m-%d %H:%M')}</div>
            </div>
            """
            
            render_card(
                title=f"Alert {alert['id']}",
                content=content,
                footer=f"Risk Score: {alert['risk_score']:.2f}",
                icon="🚨",
                color="var(--danger-color)"
            )
    
    with col2:
        st.subheader("📊 Fraud by Type")
        
        # Create sample data for fraud by type
        fraud_types = ['Identity Theft', 'Multiple Claims', 'Exaggerated Damages', 'Staged Accidents', 'Billing Fraud']
        fraud_by_type = pd.DataFrame({
            'Type': fraud_types,
            'Count': [random.randint(3, 15) for _ in range(len(fraud_types))]
        })
        
        # Create modern chart
        fig = create_modern_chart(
            fraud_by_type,
            'bar',
            'Type',
            'Count',
            'Fraud Cases by Type'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # AI confidence in fraud detection
        st.subheader("🤖 AI Confidence Levels")
        
        for i, score in enumerate([0.96, 0.88, 0.76, 0.92]):
            render_ai_confidence_indicator(score)

def render_system_config():
    """Render system configuration interface"""
    render_header("System Configuration", "Configure system settings and preferences")
    
    # Create tabs for different configuration sections
    tabs = [
        {
            "label": "General Settings",
            "content": render_general_settings
        },
        {
            "label": "AI Configuration",
            "content": render_ai_configuration
        },
        {
            "label": "User Interface",
            "content": render_ui_configuration
        },
        {
            "label": "Integrations",
            "content": render_integrations
        }
    ]
    
    render_tabs(tabs)

def render_general_settings():
    """Render general settings configuration"""
    st.subheader("⚙️ System Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("System Name", value="Insurance AI Control Tower")
        st.text_input("Organization", value="Acme Insurance Inc.")
        st.selectbox("Default Language", ["English", "Spanish", "French", "German", "Japanese"])
        st.selectbox("Date Format", ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"])
        st.selectbox("Time Zone", ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"])
    
    with col2:
        st.number_input("Session Timeout (minutes)", min_value=5, max_value=120, value=30)
        st.selectbox("Log Level", ["Debug", "Info", "Warning", "Error", "Critical"])
        st.checkbox("Enable Audit Logging", value=True)
        st.checkbox("Enable Performance Metrics", value=True)
        st.checkbox("Enable User Activity Tracking", value=True)
    
    st.subheader("📧 Notification Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Email Notifications", value=True)
        st.text_input("Admin Email", value="admin@acmeinsurance.com")
        st.checkbox("Daily Summary Report", value=True)
    
    with col2:
        st.checkbox("Critical Alert Notifications", value=True)
        st.checkbox("Performance Alert Notifications", value=True)
        st.checkbox("User Action Notifications", value=False)
    
    if st.button("Save General Settings"):
        render_notification_toast("Settings saved successfully!", "success")

def render_ai_configuration():
    """Render AI configuration settings"""
    st.subheader("🤖 AI Model Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("AI Provider", ["OpenAI", "Anthropic", "Google", "Azure OpenAI", "Hugging Face"])
        st.text_input("API Key", value="sk-••••••••••••••••••••••••••••••••••••••••••••••••••")
        st.selectbox("Primary Model", ["gpt-4o", "gpt-4", "claude-3-opus", "gemini-pro", "llama-3-70b"])
        st.selectbox("Fallback Model", ["gpt-3.5-turbo", "claude-3-haiku", "gemini-flash", "llama-3-8b"])
    
    with col2:
        st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        st.slider("Max Tokens", min_value=100, max_value=8000, value=4000, step=100)
        st.number_input("Request Timeout (seconds)", min_value=10, max_value=300, value=60)
        st.checkbox("Enable Streaming Responses", value=True)
    
    st.subheader("🧠 AI Feature Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.checkbox("Enable Underwriting AI", value=True)
        st.checkbox("Enable Claims Processing AI", value=True)
    
    with col2:
        st.checkbox("Enable Fraud Detection AI", value=True)
        st.checkbox("Enable Customer Service AI", value=True)
    
    with col3:
        st.checkbox("Enable Document Analysis AI", value=True)
        st.checkbox("Enable Risk Assessment AI", value=True)
    
    st.subheader("🔄 Model Retraining")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Retraining Frequency", ["Weekly", "Monthly", "Quarterly", "Manually"])
        st.date_input("Last Retrained", value=datetime.now() - timedelta(days=14))
    
    with col2:
        st.selectbox("Training Data Source", ["Production Data", "Synthetic Data", "Mixed"])
        st.slider("Training Data Percentage", min_value=10, max_value=100, value=30, step=10)
    
    if st.button("Save AI Configuration"):
        render_notification_toast("AI configuration saved successfully!", "success")

def render_ui_configuration():
    """Render UI configuration settings"""
    st.subheader("🎨 Theme Configuration")
    
    current_theme = get_current_theme()
    theme_config = get_theme_config()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Default Theme", ["Light", "Dark", "System Default"], 
                    index=0 if current_theme == "light" else 1)
        st.color_picker("Primary Color", value=theme_config["primaryColor"])
        st.color_picker("Background Color", value=theme_config["backgroundColor"])
        st.color_picker("Secondary Background Color", value=theme_config["secondaryBackgroundColor"])
    
    with col2:
        st.color_picker("Text Color", value=theme_config["textColor"])
        st.selectbox("Font Family", ["Inter", "Roboto", "Open Sans", "Lato", "System Default"])
        st.slider("Border Radius", min_value=0, max_value=20, value=8)
        st.checkbox("Enable Animations", value=True)
    
    st.subheader("📱 Layout Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Default Layout", ["Wide", "Centered", "Narrow"])
        st.selectbox("Sidebar Position", ["Left", "Right", "Hidden"])
        st.checkbox("Collapsible Sidebar", value=True)
    
    with col2:
        st.selectbox("Default Page", ["Dashboard", "Policy Management", "Claims Processing"])
        st.checkbox("Show Quick Stats in Sidebar", value=True)
        st.checkbox("Show Notifications in Header", value=True)
    
    if st.button("Save UI Configuration"):
        render_notification_toast("UI configuration saved successfully!", "success")
        st.rerun()

def render_integrations():
    """Render integrations configuration"""
    st.subheader("🔌 External Integrations")
    
    # Sample integrations
    integrations = [
        {
            "name": "CRM System",
            "status": "Connected",
            "last_sync": datetime.now() - timedelta(minutes=15)
        },
        {
            "name": "Payment Gateway",
            "status": "Connected",
            "last_sync": datetime.now() - timedelta(hours=2)
        },
        {
            "name": "Document Management",
            "status": "Connected",
            "last_sync": datetime.now() - timedelta(hours=1)
        },
        {
            "name": "Email Service",
            "status": "Connected",
            "last_sync": datetime.now() - timedelta(minutes=30)
        },
        {
            "name": "Analytics Platform",
            "status": "Error",
            "last_sync": datetime.now() - timedelta(days=1)
        }
    ]
    
    for integration in integrations:
        status_color = "success" if integration["status"] == "Connected" else "danger"
        
        content = f"""
        <div class="integration-details">
            <div><strong>Status:</strong> {integration["status"]}</div>
            <div><strong>Last Sync:</strong> {integration["last_sync"].strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        """
        
        footer = "Configure" if integration["status"] == "Connected" else "Reconnect"
        
        render_card(
            title=integration["name"],
            content=content,
            footer=footer,
            icon="🔌",
            color=f"var(--{status_color}-color)"
        )
    
    st.subheader("➕ Add New Integration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Integration Type", ["CRM System", "Payment Gateway", "Document Management", "Email Service", "Analytics Platform", "Custom API"])
        st.text_input("Integration Name")
    
    with col2:
        st.text_input("API Endpoint")
        st.text_input("API Key")
    
    if st.button("Add Integration"):
        render_notification_toast("Integration added successfully!", "success")

# Main app function
def main():
    """Main application function"""
    # Render navigation sidebar
    render_navigation()
    
    # Render theme toggle
    render_theme_toggle()
    
    # Render current page
    current_page = st.session_state.current_page
    
    if current_page == "Dashboard":
        render_dashboard()
    elif current_page == "Policy_Management":
        render_policy_management()
    elif current_page == "Claims_Processing":
        render_claims_processing()
    elif current_page == "Analytics":
        render_analytics()
    elif current_page == "Fraud_Detection":
        render_fraud_detection()
    elif current_page == "System_Config":
        render_system_config()
    else:
        # Placeholder for other pages
        render_header(current_page, "This section is under development")
        
        st.info("This section is currently under development. Please check back later.")

if __name__ == "__main__":
    main()
