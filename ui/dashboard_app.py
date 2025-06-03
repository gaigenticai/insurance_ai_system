"""
Insurance AI System - Comprehensive Dashboard UI

A complete control tower interface for insurance operations with AI integration.
Features: Dashboard, Policy Management, Claims Processing, Analytics, Fraud Detection,
Knowledge Base, System Configuration, Notifications, User Management, and Human Escalation.
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

# Page configuration
st.set_page_config(
    page_title="Insurance AI Control Tower",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #2a5298;
        margin-bottom: 1rem;
    }
    
    .alert-card {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #f39c12;
    }
    
    .success-card {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #28a745;
    }
    
    .danger-card {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #dc3545;
    }
    
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .agent-status {
        display: flex;
        align-items: center;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 5px;
        background: #f8f9fa;
    }
    
    .status-active { border-left: 4px solid #28a745; }
    .status-idle { border-left: 4px solid #ffc107; }
    .status-error { border-left: 4px solid #dc3545; }
    
    .live-feed {
        max-height: 300px;
        overflow-y: auto;
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        font-family: monospace;
        font-size: 0.9em;
    }
    
    .nav-button {
        width: 100%;
        margin-bottom: 0.5rem;
        padding: 0.75rem;
        border: none;
        border-radius: 8px;
        background: #e9ecef;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .nav-button:hover {
        background: #2a5298;
        color: white;
    }
    
    .nav-button.active {
        background: #2a5298;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

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
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown("### 🏢 Insurance AI Control Tower")
    st.sidebar.markdown("---")
    
    # User info
    st.sidebar.markdown(f"**User:** {st.session_state.user_role}")
    st.sidebar.markdown(f"**Session:** {datetime.now().strftime('%H:%M:%S')}")
    st.sidebar.markdown("---")
    
    # Navigation buttons
    pages = {
        "🏠 Dashboard": "Dashboard",
        "📋 Policy Management": "Policy Management", 
        "⚖️ Claims Processing": "Claims Processing",
        "📊 Analytics & Risk": "Analytics",
        "🕵️ Fraud Detection": "Fraud Detection",
        "📚 Knowledge Base": "Knowledge Base",
        "⚙️ System Config": "System Config",
        "📩 Notifications": "Notifications",
        "👤 User Management": "User Management",
        "📞 Human Escalation": "Human Escalation"
    }
    
    for display_name, page_name in pages.items():
        if st.sidebar.button(display_name, key=f"nav_{page_name}"):
            st.session_state.current_page = page_name
            st.rerun()
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Quick stats in sidebar
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown("### 📈 Quick Stats")
    st.sidebar.metric("Active Policies", "1,247", "↑ 23")
    st.sidebar.metric("Open Claims", "89", "↓ 5")
    st.sidebar.metric("AI Accuracy", "94.2%", "↑ 1.2%")
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Page Components
def render_dashboard():
    """Render the main dashboard"""
    st.markdown('<div class="main-header"><h1>🏠 Insurance AI Control Tower</h1><p>Real-time overview of all insurance operations</p></div>', unsafe_allow_html=True)
    
    # Overview metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Policies", "1,247", "↑ 23 today")
    with col2:
        st.metric("Claims Processed", "89", "↑ 12 today")
    with col3:
        st.metric("Flagged Risks", "15", "↓ 3 today")
    with col4:
        st.metric("Pending Reviews", "7", "→ 0 change")
    with col5:
        st.metric("AI Accuracy", "94.2%", "↑ 1.2%")
    
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
        
        fig_heatmap = px.imshow(
            pivot_data,
            title="Agent Activity by Hour (Last 24h)",
            color_continuous_scale="Blues",
            aspect="auto"
        )
        fig_heatmap.update_layout(height=400)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Live Agent Feed
        st.subheader("📡 Live Agent Feed")
        agents = generate_mock_agents()
        
        for agent in agents:
            status_class = f"status-{agent.status.lower()}"
            if agent.status == "Error":
                status_class = "status-error"
            elif agent.status == "Idle":
                status_class = "status-idle"
            else:
                status_class = "status-active"
            
            st.markdown(f"""
            <div class="agent-status {status_class}">
                <strong>{agent.agent_name}</strong> - {agent.status}<br>
                <small>{agent.current_task} | Success Rate: {agent.success_rate:.1%}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Alert Stream
        st.subheader("🚨 Alert Stream")
        alerts = generate_mock_alerts()
        
        for alert in alerts:
            if alert.severity == "Critical":
                card_class = "danger-card"
            elif alert.severity == "High":
                card_class = "alert-card"
            else:
                card_class = "success-card"
            
            status_icon = "✅" if alert.resolved else "🔴"
            
            st.markdown(f"""
            <div class="{card_class}">
                <strong>{status_icon} {alert.type}</strong><br>
                <small>{alert.message}</small><br>
                <small>{alert.timestamp.strftime('%H:%M:%S')}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # System Health
        st.subheader("💚 System Health")
        health_metrics = {
            "API Response Time": (245, "ms", "good"),
            "Database Connections": (12, "/50", "good"),
            "AI Model Latency": (1.2, "s", "warning"),
            "Error Rate": (0.3, "%", "good"),
            "Memory Usage": (68, "%", "warning")
        }
        
        for metric, (value, unit, status) in health_metrics.items():
            color = "🟢" if status == "good" else "🟡" if status == "warning" else "🔴"
            st.markdown(f"{color} **{metric}**: {value}{unit}")

def render_policy_management():
    """Render policy management interface"""
    st.markdown('<div class="main-header"><h1>📋 Policy & Underwriting Management</h1></div>', unsafe_allow_html=True)
    
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
    df_policies = pd.DataFrame([{
        'Policy ID': p.id,
        'Customer': p.customer_name,
        'Type': p.policy_type,
        'Status': p.status,
        'Premium': f"${p.premium:,.2f}",
        'Risk Score': f"{p.risk_score:.2f}",
        'AI Decision': p.ai_decision,
        'Confidence': f"{p.confidence:.1%}",
        'Created': p.created_date.strftime('%Y-%m-%d')
    } for p in policies])
    
    # Policy viewer with search
    st.subheader("🔍 Policy Search & Viewer")
    search_term = st.text_input("Search policies by ID, customer name, or type...")
    
    if search_term:
        mask = df_policies.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        df_filtered = df_policies[mask]
    else:
        df_filtered = df_policies
    
    # Display policies table
    st.dataframe(df_filtered, use_container_width=True, height=400)
    
    # Policy details viewer
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Underwriting Decisions Analysis")
        
        # AI decision distribution
        decision_counts = df_policies['AI Decision'].value_counts()
        fig_decisions = px.pie(
            values=decision_counts.values,
            names=decision_counts.index,
            title="AI Underwriting Decisions Distribution"
        )
        st.plotly_chart(fig_decisions, use_container_width=True)
        
        # Risk score distribution
        risk_scores = [float(p.risk_score) for p in policies]
        fig_risk = px.histogram(
            x=risk_scores,
            nbins=20,
            title="Risk Score Distribution",
            labels={'x': 'Risk Score', 'y': 'Count'}
        )
        st.plotly_chart(fig_risk, use_container_width=True)
    
    with col2:
        st.subheader("⚙️ Custom Underwriting Rules")
        
        st.markdown("**Current Rules:**")
        rules = [
            "Auto policies: Reject if risk score > 0.8",
            "Life policies: Review if age > 65",
            "Commercial: Require manual review if premium > $10k",
            "Health: Flag pre-existing conditions"
        ]
        
        for i, rule in enumerate(rules):
            st.markdown(f"{i+1}. {rule}")
        
        st.markdown("---")
        st.markdown("**Add New Rule:**")
        rule_type = st.selectbox("Rule Type", ["Risk Threshold", "Age Limit", "Premium Limit", "Custom"])
        rule_condition = st.text_input("Condition")
        rule_action = st.selectbox("Action", ["Approve", "Reject", "Review", "Flag"])
        
        if st.button("Add Rule"):
            st.success("Rule added successfully!")
        
        st.markdown("---")
        st.subheader("🎯 AI Explainability")
        
        selected_policy = st.selectbox("Select Policy for Analysis", df_policies['Policy ID'].tolist())
        
        if selected_policy:
            st.markdown("**AI Decision Reasoning:**")
            st.markdown("""
            - **Risk Assessment**: Medium risk (0.65)
            - **Credit Score**: Good (750+)
            - **Claims History**: No previous claims
            - **Demographic Factors**: Standard risk profile
            - **Final Decision**: Approved with standard premium
            """)

def render_claims_processing():
    """Render claims processing interface"""
    st.markdown('<div class="main-header"><h1>⚖️ Claims Processing Center</h1></div>', unsafe_allow_html=True)
    
    # Claims inbox
    st.subheader("📥 Claims Inbox")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        claim_status_filter = st.selectbox("Status", ["All", "Open", "Under Review", "Approved", "Denied", "Closed"])
    with col2:
        claim_type_filter = st.selectbox("Claim Type", ["All", "Auto Accident", "Property Damage", "Medical", "Theft", "Fire"])
    with col3:
        fraud_risk_filter = st.selectbox("Fraud Risk", ["All", "Low", "Medium", "High"])
    with col4:
        sort_by = st.selectbox("Sort By", ["Date", "Amount", "Fraud Score", "Priority"])
    
    # Generate claims data
    claims = generate_mock_claims()
    df_claims = pd.DataFrame([{
        'Claim ID': c.id,
        'Policy ID': c.policy_id,
        'Customer': c.customer_name,
        'Type': c.claim_type,
        'Amount': f"${c.amount:,.2f}",
        'Status': c.status,
        'AI Decision': c.ai_decision,
        'Fraud Score': f"{c.fraud_score:.2f}",
        'Confidence': f"{c.confidence:.1%}",
        'Date': c.created_date.strftime('%Y-%m-%d')
    } for c in claims])
    
    # Claims table
    st.dataframe(df_claims, use_container_width=True, height=300)
    
    # Claim details viewer
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 Claim Details Viewer")
        
        selected_claim = st.selectbox("Select Claim", df_claims['Claim ID'].tolist())
        
        if selected_claim:
            # Mock claim details
            st.markdown("### Claim Summary")
            st.markdown("""
            **Incident Description:** Vehicle collision at intersection of Main St and Oak Ave.
            Police report filed. No injuries reported. Estimated damage to front bumper and headlight.
            
            **Documents Uploaded:**
            - Police Report (PDF)
            - Photos of damage (4 images)
            - Repair estimate from certified shop
            """)
            
            # NLP Summary
            st.markdown("### 🤖 AI Analysis Summary")
            st.markdown("""
            **Key Findings:**
            - Incident location verified through police report
            - Damage consistent with described collision
            - No suspicious patterns detected
            - Customer has clean claims history
            
            **Recommended Action:** Approve claim for $2,450
            **Confidence Level:** 92%
            """)
            
            # Decision buttons
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                if st.button("✅ Approve"):
                    st.success("Claim approved!")
            with col_b:
                if st.button("❌ Deny"):
                    st.error("Claim denied!")
            with col_c:
                if st.button("🔍 Investigate"):
                    st.warning("Claim flagged for investigation!")
            with col_d:
                if st.button("👤 Escalate"):
                    st.info("Claim escalated to human reviewer!")
    
    with col2:
        st.subheader("📋 Audit Trail")
        
        audit_events = [
            {"Time": "2024-01-15 09:30", "Action": "Claim submitted", "User": "Customer Portal"},
            {"Time": "2024-01-15 09:31", "Action": "AI triage completed", "User": "Claims Agent"},
            {"Time": "2024-01-15 09:35", "Action": "Documents validated", "User": "Document Agent"},
            {"Time": "2024-01-15 09:40", "Action": "Fraud check passed", "User": "Fraud Agent"},
            {"Time": "2024-01-15 09:45", "Action": "Pending human review", "User": "System"}
        ]
        
        for event in audit_events:
            st.markdown(f"""
            <div class="success-card">
                <strong>{event['Time']}</strong><br>
                {event['Action']}<br>
                <small>By: {event['User']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.subheader("📊 Processing Stats")
        st.metric("Avg Processing Time", "2.3 hours")
        st.metric("SLA Compliance", "94%")
        st.metric("Auto-Approval Rate", "67%")

def render_analytics():
    """Render analytics and risk dashboard"""
    st.markdown('<div class="main-header"><h1>📊 Actuarial & Risk Analytics</h1></div>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Loss Ratio", "0.65", "↓ 0.03")
    with col2:
        st.metric("Combined Ratio", "0.98", "↓ 0.05")
    with col3:
        st.metric("Customer LTV", "$4,250", "↑ $150")
    with col4:
        st.metric("Churn Rate", "8.2%", "↓ 1.1%")
    
    # Analytics tabs
    tab1, tab2, tab3 = st.tabs(["📈 Trend Analysis", "🎯 AI Insights", "🔮 What-If Simulation"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Loss ratio trend
            dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='M')
            loss_ratios = [0.7 + random.uniform(-0.1, 0.1) for _ in dates]
            
            fig_loss = px.line(
                x=dates,
                y=loss_ratios,
                title="Loss Ratio Trend",
                labels={'x': 'Date', 'y': 'Loss Ratio'}
            )
            fig_loss.add_hline(y=0.65, line_dash="dash", line_color="red", annotation_text="Target")
            st.plotly_chart(fig_loss, use_container_width=True)
            
            # Premium vs payouts
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            premiums = [1200000, 1250000, 1180000, 1300000, 1350000, 1280000]
            payouts = [780000, 812500, 767000, 845000, 877500, 832000]
            
            fig_premium = go.Figure()
            fig_premium.add_trace(go.Bar(name='Premiums', x=months, y=premiums))
            fig_premium.add_trace(go.Bar(name='Payouts', x=months, y=payouts))
            fig_premium.update_layout(title="Premiums vs Payouts", barmode='group')
            st.plotly_chart(fig_premium, use_container_width=True)
        
        with col2:
            # Customer segments
            segments = ['Low Risk', 'Medium Risk', 'High Risk', 'Premium']
            segment_counts = [450, 320, 180, 97]
            
            fig_segments = px.pie(
                values=segment_counts,
                names=segments,
                title="Customer Risk Segments"
            )
            st.plotly_chart(fig_segments, use_container_width=True)
            
            # Churn analysis
            churn_data = {
                'Segment': ['Low Risk', 'Medium Risk', 'High Risk', 'Premium'],
                'Churn Rate': [0.05, 0.08, 0.15, 0.03],
                'Count': [450, 320, 180, 97]
            }
            df_churn = pd.DataFrame(churn_data)
            
            fig_churn = px.bar(
                df_churn,
                x='Segment',
                y='Churn Rate',
                title="Churn Rate by Segment"
            )
            st.plotly_chart(fig_churn, use_container_width=True)
    
    with tab2:
        st.subheader("🧠 AI-Learned Insights")
        
        insights = [
            {
                "title": "Fraud Ring Detection",
                "description": "AI identified a potential fraud ring involving 12 claims with similar damage patterns and shared repair shops.",
                "confidence": 0.89,
                "impact": "High",
                "action": "Investigation initiated"
            },
            {
                "title": "Risk Cluster Analysis", 
                "description": "Geographic cluster of high-risk policies identified in downtown area, likely due to increased theft rates.",
                "confidence": 0.76,
                "impact": "Medium",
                "action": "Premium adjustment recommended"
            },
            {
                "title": "Seasonal Pattern",
                "description": "Claims spike detected during winter months for auto policies, suggesting weather-related incidents.",
                "confidence": 0.92,
                "impact": "Low",
                "action": "Seasonal pricing model updated"
            }
        ]
        
        for insight in insights:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{insight['title']}</h4>
                <p>{insight['description']}</p>
                <p><strong>Confidence:</strong> {insight['confidence']:.1%} | 
                   <strong>Impact:</strong> {insight['impact']} | 
                   <strong>Action:</strong> {insight['action']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.subheader("🔮 What-If Simulation Tool")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("**Adjust Variables:**")
            premium_change = st.slider("Premium Adjustment (%)", -20, 20, 0)
            deductible_change = st.slider("Deductible Change (%)", -50, 50, 0)
            coverage_change = st.slider("Coverage Limit Change (%)", -30, 30, 0)
            
            if st.button("Run Simulation"):
                st.success("Simulation completed!")
        
        with col2:
            # Simulation results
            st.markdown("**Projected Outcomes:**")
            
            base_metrics = {
                "Annual Premium Revenue": 15600000,
                "Expected Claims": 10140000,
                "Profit Margin": 5460000,
                "Customer Retention": 0.918
            }
            
            for metric, base_value in base_metrics.items():
                # Simple simulation logic
                if "Premium" in metric:
                    new_value = base_value * (1 + premium_change/100)
                elif "Claims" in metric:
                    new_value = base_value * (1 - premium_change/200)  # Inverse relationship
                elif "Profit" in metric:
                    new_value = base_value * (1 + premium_change/100) * 1.5
                else:
                    new_value = base_value * (1 - abs(premium_change)/1000)
                
                change = new_value - base_value
                change_pct = (change / base_value) * 100
                
                if isinstance(base_value, float) and base_value < 1:
                    st.metric(metric, f"{new_value:.1%}", f"{change_pct:+.1f}%")
                else:
                    st.metric(metric, f"${new_value:,.0f}", f"{change_pct:+.1f}%")

def render_fraud_detection():
    """Render fraud detection and ethics monitoring"""
    st.markdown('<div class="main-header"><h1>🕵️ Fraud & Ethics Monitoring</h1></div>', unsafe_allow_html=True)
    
    # Fraud overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Fraud Cases Detected", "23", "↑ 5")
    with col2:
        st.metric("False Positive Rate", "3.2%", "↓ 0.8%")
    with col3:
        st.metric("Savings from Detection", "$127K", "↑ $23K")
    with col4:
        st.metric("Model Accuracy", "96.8%", "↑ 1.2%")
    
    # Fraud detection tabs
    tab1, tab2, tab3 = st.tabs(["🚨 Anomaly Detection", "⚖️ Ethics Monitoring", "🗣️ Dispute Management"])
    
    with tab1:
        st.subheader("🔍 Anomaly Detection Viewer")
        
        # Flagged claims
        flagged_claims = [
            {
                "Claim ID": "CLM-2045",
                "Risk Score": 0.89,
                "Reason": "Unusual damage pattern, multiple similar claims from same area",
                "Status": "Under Investigation",
                "Flagged Date": "2024-01-15"
            },
            {
                "Claim ID": "CLM-2051", 
                "Risk Score": 0.76,
                "Reason": "Repair shop not in network, high estimate",
                "Status": "Pending Review",
                "Flagged Date": "2024-01-14"
            },
            {
                "Claim ID": "CLM-2038",
                "Risk Score": 0.82,
                "Reason": "Customer filed 3 claims in 6 months",
                "Status": "Escalated",
                "Flagged Date": "2024-01-13"
            }
        ]
        
        df_flagged = pd.DataFrame(flagged_claims)
        st.dataframe(df_flagged, use_container_width=True)
        
        # Fraud patterns visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Fraud score distribution
            fraud_scores = [random.uniform(0, 1) for _ in range(100)]
            fig_fraud = px.histogram(
                x=fraud_scores,
                nbins=20,
                title="Fraud Score Distribution",
                labels={'x': 'Fraud Score', 'y': 'Count'}
            )
            fig_fraud.add_vline(x=0.7, line_dash="dash", line_color="red", annotation_text="Threshold")
            st.plotly_chart(fig_fraud, use_container_width=True)
        
        with col2:
            # Geographic fraud hotspots
            locations = ['Downtown', 'Suburbs', 'Industrial', 'Residential', 'Commercial']
            fraud_counts = [15, 8, 12, 5, 18]
            
            fig_geo = px.bar(
                x=locations,
                y=fraud_counts,
                title="Fraud Cases by Location",
                labels={'x': 'Area', 'y': 'Fraud Cases'}
            )
            st.plotly_chart(fig_geo, use_container_width=True)
    
    with tab2:
        st.subheader("⚖️ Ethical AI Monitoring")
        
        # Ethics violations
        ethics_issues = [
            {
                "Issue": "Potential Age Bias",
                "Description": "AI model showing lower approval rates for applicants over 65",
                "Severity": "Medium",
                "Status": "Under Review",
                "Date": "2024-01-10"
            },
            {
                "Issue": "Geographic Discrimination",
                "Description": "Higher premiums consistently assigned to specific zip codes",
                "Severity": "High", 
                "Status": "Investigating",
                "Date": "2024-01-08"
            },
            {
                "Issue": "Gender Disparity",
                "Description": "Slight variance in claim approval rates between genders",
                "Severity": "Low",
                "Status": "Monitoring",
                "Date": "2024-01-05"
            }
        ]
        
        for issue in ethics_issues:
            severity_class = "danger-card" if issue["Severity"] == "High" else "alert-card" if issue["Severity"] == "Medium" else "success-card"
            
            st.markdown(f"""
            <div class="{severity_class}">
                <h4>{issue['Issue']} - {issue['Severity']} Severity</h4>
                <p>{issue['Description']}</p>
                <p><strong>Status:</strong> {issue['Status']} | <strong>Date:</strong> {issue['Date']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Bias metrics
        st.subheader("📊 Bias Detection Metrics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Demographic Parity", "0.95", "Target: >0.90")
        with col2:
            st.metric("Equal Opportunity", "0.92", "Target: >0.85")
        with col3:
            st.metric("Calibration Score", "0.88", "Target: >0.80")
    
    with tab3:
        st.subheader("🗣️ Dispute Management")
        
        # Active disputes
        disputes = [
            {
                "Dispute ID": "DSP-001",
                "Claim ID": "CLM-2045",
                "Customer": "John Smith",
                "Issue": "Claim denial disputed",
                "Status": "Open",
                "Assigned To": "Sarah Johnson",
                "Created": "2024-01-12"
            },
            {
                "Dispute ID": "DSP-002", 
                "Claim ID": "CLM-2038",
                "Customer": "Mary Davis",
                "Issue": "Premium increase questioned",
                "Status": "In Progress",
                "Assigned To": "Mike Wilson",
                "Created": "2024-01-10"
            }
        ]
        
        df_disputes = pd.DataFrame(disputes)
        st.dataframe(df_disputes, use_container_width=True)
        
        # Dispute details
        selected_dispute = st.selectbox("Select Dispute for Details", df_disputes['Dispute ID'].tolist())
        
        if selected_dispute:
            st.markdown("### Dispute Resolution Thread")
            
            thread_messages = [
                {"Time": "2024-01-12 14:30", "User": "John Smith", "Message": "I believe my claim was wrongly denied. The damage was clearly from the accident."},
                {"Time": "2024-01-12 15:45", "User": "Sarah Johnson", "Message": "Thank you for contacting us. I'm reviewing your case and will respond within 24 hours."},
                {"Time": "2024-01-13 09:15", "User": "Sarah Johnson", "Message": "After review, I can see the AI flagged inconsistencies. Let me escalate this for human review."},
                {"Time": "2024-01-13 16:20", "User": "Claims Manager", "Message": "Case reviewed. Claim approved for $2,450. Apologies for the initial error."}
            ]
            
            for msg in thread_messages:
                st.markdown(f"""
                <div class="success-card">
                    <strong>{msg['User']}</strong> - {msg['Time']}<br>
                    {msg['Message']}
                </div>
                """, unsafe_allow_html=True)
            
            # Add response
            st.text_area("Add Response", placeholder="Type your response here...")
            if st.button("Send Response"):
                st.success("Response sent!")

def render_knowledge_base():
    """Render knowledge base and model feedback"""
    st.markdown('<div class="main-header"><h1>📚 Knowledge Base & Model Feedback</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📖 Agent Learning", "👍 Manual Feedback", "🎭 Scenario Builder"])
    
    with tab1:
        st.subheader("🧠 Agent Learning History")
        
        # Learning metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Model Updates", "47", "↑ 3 this week")
        with col2:
            st.metric("Training Examples", "12,450", "↑ 234")
        with col3:
            st.metric("Accuracy Improvement", "+2.3%", "Last 30 days")
        with col4:
            st.metric("Feedback Incorporated", "89%", "↑ 5%")
        
        # Learning timeline
        st.subheader("📈 Learning Evolution Timeline")
        
        learning_events = [
            {"Date": "2024-01-15", "Event": "Fraud detection model updated", "Impact": "+1.2% accuracy"},
            {"Date": "2024-01-12", "Event": "New underwriting rules learned", "Impact": "Reduced manual reviews by 15%"},
            {"Date": "2024-01-08", "Event": "Claims processing optimization", "Impact": "-0.5 hours avg processing time"},
            {"Date": "2024-01-05", "Event": "Customer service responses improved", "Impact": "+8% satisfaction score"},
            {"Date": "2024-01-01", "Event": "Quarterly model retrain completed", "Impact": "Overall system performance +3.1%"}
        ]
        
        for event in learning_events:
            st.markdown(f"""
            <div class="success-card">
                <strong>{event['Date']}</strong> - {event['Event']}<br>
                <small>Impact: {event['Impact']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Model performance over time
        dates = pd.date_range(start='2023-06-01', end='2024-01-15', freq='W')
        accuracy_scores = [0.85 + (i * 0.002) + random.uniform(-0.01, 0.01) for i in range(len(dates))]
        
        fig_learning = px.line(
            x=dates,
            y=accuracy_scores,
            title="Model Accuracy Evolution",
            labels={'x': 'Date', 'y': 'Accuracy Score'}
        )
        st.plotly_chart(fig_learning, use_container_width=True)
    
    with tab2:
        st.subheader("👍 Manual Feedback Injection")
        
        # Feedback form
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Rate Recent AI Decisions:**")
            
            recent_decisions = [
                {"ID": "CLM-2045", "Decision": "Approve $2,450", "AI Confidence": "92%"},
                {"ID": "POL-1089", "Decision": "Reject application", "AI Confidence": "87%"},
                {"ID": "CLM-2051", "Decision": "Flag for review", "AI Confidence": "76%"}
            ]
            
            for decision in recent_decisions:
                st.markdown(f"**{decision['ID']}**: {decision['Decision']} (Confidence: {decision['AI Confidence']})")
                rating = st.radio(
                    f"Rating for {decision['ID']}",
                    ["Correct", "Incorrect", "Partially Correct"],
                    key=f"rating_{decision['ID']}"
                )
                feedback_text = st.text_input(f"Feedback for {decision['ID']}", key=f"feedback_{decision['ID']}")
                st.markdown("---")
        
        with col2:
            st.markdown("**Feedback Statistics:**")
            
            feedback_stats = {
                "Total Feedback Items": 1247,
                "Positive Feedback": 1089,
                "Negative Feedback": 158,
                "Feedback Accuracy": "87.3%",
                "Avg Response Time": "2.3 hours"
            }
            
            for stat, value in feedback_stats.items():
                st.metric(stat, value)
            
            # Feedback trends
            feedback_trend = [85, 87, 89, 88, 90, 87, 89]
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            fig_feedback = px.line(
                x=days,
                y=feedback_trend,
                title="Weekly Feedback Quality Trend",
                labels={'x': 'Day', 'y': 'Quality Score'}
            )
            st.plotly_chart(fig_feedback, use_container_width=True)
        
        if st.button("Submit All Feedback"):
            st.success("Feedback submitted! Models will be updated in the next training cycle.")
    
    with tab3:
        st.subheader("🎭 Scenario Builder & Testing")
        
        # Scenario creation
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Create Test Scenario:**")
            
            scenario_type = st.selectbox("Scenario Type", ["Underwriting", "Claims Processing", "Fraud Detection", "Customer Service"])
            scenario_name = st.text_input("Scenario Name")
            
            st.markdown("**Scenario Parameters:**")
            if scenario_type == "Underwriting":
                age = st.slider("Applicant Age", 18, 80, 35)
                income = st.number_input("Annual Income", 20000, 200000, 50000)
                credit_score = st.slider("Credit Score", 300, 850, 700)
                coverage = st.number_input("Coverage Amount", 50000, 1000000, 250000)
            
            elif scenario_type == "Claims Processing":
                claim_amount = st.number_input("Claim Amount", 500, 50000, 5000)
                claim_type = st.selectbox("Claim Type", ["Auto", "Property", "Medical", "Theft"])
                has_police_report = st.checkbox("Police Report Filed")
                customer_history = st.selectbox("Customer History", ["Clean", "1 Previous Claim", "Multiple Claims"])
            
            test_description = st.text_area("Scenario Description", placeholder="Describe the test scenario in detail...")
            
            if st.button("Run Scenario Test"):
                st.success("Scenario test completed! Results shown on the right.")
        
        with col2:
            st.markdown("**Test Results:**")
            
            if scenario_type == "Underwriting":
                st.markdown("""
                **AI Decision:** Approved
                **Confidence:** 89%
                **Premium:** $1,247/year
                **Risk Score:** 0.34 (Low)
                
                **Decision Factors:**
                - Good credit score (+)
                - Stable income (+)
                - Age within standard range (+)
                - No previous claims (+)
                """)
            
            elif scenario_type == "Claims Processing":
                st.markdown("""
                **AI Decision:** Approve
                **Confidence:** 76%
                **Processing Time:** 1.2 hours
                **Fraud Score:** 0.12 (Low)
                
                **Decision Factors:**
                - Police report validates incident (+)
                - Damage consistent with description (+)
                - Customer has clean history (+)
                - Claim amount within normal range (+)
                """)
            
            # Performance comparison
            st.markdown("**Performance Comparison:**")
            comparison_data = {
                "Metric": ["Accuracy", "Speed", "Confidence", "Consistency"],
                "Current Model": [89, 92, 87, 94],
                "Previous Model": [85, 88, 83, 89]
            }
            df_comparison = pd.DataFrame(comparison_data)
            
            fig_comparison = px.bar(
                df_comparison,
                x="Metric",
                y=["Current Model", "Previous Model"],
                title="Model Performance Comparison",
                barmode="group"
            )
            st.plotly_chart(fig_comparison, use_container_width=True)

def render_system_config():
    """Render system configuration interface"""
    st.markdown('<div class="main-header"><h1>⚙️ System Configuration</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🏢 Institution Config", "🤖 Agent Settings", "🔧 Model Configuration"])
    
    with tab1:
        st.subheader("🏢 Institution Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Business Rules:**")
            
            # Risk thresholds
            st.markdown("**Risk Assessment Thresholds:**")
            low_risk_threshold = st.slider("Low Risk Threshold", 0.0, 1.0, 0.3, 0.01)
            high_risk_threshold = st.slider("High Risk Threshold", 0.0, 1.0, 0.7, 0.01)
            
            # Coverage limits
            st.markdown("**Coverage Limits:**")
            min_coverage = st.number_input("Minimum Coverage", 10000, 100000, 25000)
            max_coverage = st.number_input("Maximum Coverage", 500000, 5000000, 1000000)
            
            # Approval thresholds
            st.markdown("**Auto-Approval Thresholds:**")
            auto_approve_threshold = st.slider("Auto-Approve Confidence", 0.5, 1.0, 0.85, 0.01)
            auto_reject_threshold = st.slider("Auto-Reject Confidence", 0.5, 1.0, 0.90, 0.01)
        
        with col2:
            st.markdown("**Current Configuration:**")
            
            config_display = {
                "Institution Name": "Acme Insurance Co.",
                "License Number": "INS-12345-TX",
                "Regulatory Jurisdiction": "Texas",
                "Business Hours": "8:00 AM - 6:00 PM CST",
                "SLA Target": "24 hours",
                "Compliance Framework": "NAIC Standards"
            }
            
            for key, value in config_display.items():
                st.markdown(f"**{key}:** {value}")
            
            st.markdown("---")
            st.markdown("**Risk Model Settings:**")
            
            risk_factors = [
                "Age Weight: 0.25",
                "Credit Score Weight: 0.30", 
                "Claims History Weight: 0.35",
                "Geographic Weight: 0.10"
            ]
            
            for factor in risk_factors:
                st.markdown(f"• {factor}")
        
        if st.button("Save Institution Configuration"):
            st.success("Configuration saved successfully!")
    
    with tab2:
        st.subheader("🤖 Agent Roles & Permissions")
        
        # Agent configuration table
        agents_config = [
            {"Agent": "Underwriting Agent", "Status": "Active", "Permissions": "Read/Write Policies", "Rate Limit": "100/hour"},
            {"Agent": "Claims Agent", "Status": "Active", "Permissions": "Read/Write Claims", "Rate Limit": "150/hour"},
            {"Agent": "Fraud Detection Agent", "Status": "Active", "Permissions": "Read All Data", "Rate Limit": "200/hour"},
            {"Agent": "Actuarial Agent", "Status": "Active", "Permissions": "Read Analytics", "Rate Limit": "50/hour"},
            {"Agent": "Compliance Agent", "Status": "Active", "Permissions": "Read/Audit", "Rate Limit": "75/hour"},
            {"Agent": "Customer Service Agent", "Status": "Active", "Permissions": "Read Customer Data", "Rate Limit": "300/hour"}
        ]
        
        df_agents = pd.DataFrame(agents_config)
        st.dataframe(df_agents, use_container_width=True)
        
        # Agent details configuration
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Configure Agent:**")
            selected_agent = st.selectbox("Select Agent", df_agents['Agent'].tolist())
            
            if selected_agent:
                agent_status = st.selectbox("Status", ["Active", "Inactive", "Maintenance"])
                rate_limit = st.number_input("Rate Limit (requests/hour)", 10, 1000, 100)
                
                st.markdown("**Permissions:**")
                can_read_policies = st.checkbox("Read Policies", True)
                can_write_policies = st.checkbox("Write Policies", False)
                can_read_claims = st.checkbox("Read Claims", True)
                can_write_claims = st.checkbox("Write Claims", False)
                can_access_analytics = st.checkbox("Access Analytics", True)
        
        with col2:
            st.markdown("**Agent Performance:**")
            
            # Mock performance data for selected agent
            performance_data = {
                "Requests Today": 847,
                "Success Rate": "98.2%",
                "Avg Response Time": "1.2s",
                "Error Rate": "1.8%",
                "Last Active": "2 minutes ago"
            }
            
            for metric, value in performance_data.items():
                st.metric(metric, value)
            
            # Performance chart
            hours = list(range(24))
            requests = [random.randint(20, 80) for _ in hours]
            
            fig_performance = px.line(
                x=hours,
                y=requests,
                title="Agent Activity (24h)",
                labels={'x': 'Hour', 'y': 'Requests'}
            )
            st.plotly_chart(fig_performance, use_container_width=True)
        
        if st.button("Update Agent Configuration"):
            st.success("Agent configuration updated!")
    
    with tab3:
        st.subheader("🔧 Model Settings & LLM Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Primary AI Provider:**")
            ai_provider = st.selectbox("AI Provider", ["OpenAI", "Anthropic", "Local LLM", "Azure OpenAI"])
            
            if ai_provider == "OpenAI":
                model_name = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"])
                temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
                max_tokens = st.number_input("Max Tokens", 100, 4000, 1000)
            
            st.markdown("**Memory Configuration:**")
            enable_memory = st.checkbox("Enable Conversation Memory", True)
            memory_window = st.number_input("Memory Window (messages)", 5, 50, 10)
            
            st.markdown("**Prompt Engineering:**")
            use_chain_of_thought = st.checkbox("Chain-of-Thought Prompting", True)
            use_few_shot = st.checkbox("Few-Shot Learning", True)
            use_role_based = st.checkbox("Role-Based Prompts", True)
        
        with col2:
            st.markdown("**Model Performance:**")
            
            model_metrics = {
                "Current Model": "gpt-3.5-turbo",
                "Avg Response Time": "1.8s",
                "Token Usage (24h)": "45,230",
                "Cost (24h)": "$12.45",
                "Uptime": "99.8%"
            }
            
            for metric, value in model_metrics.items():
                st.metric(metric, value)
            
            st.markdown("**Prompt Templates:**")
            
            prompt_templates = [
                "Underwriting Analysis",
                "Claims Processing", 
                "Fraud Detection",
                "Customer Service",
                "Risk Assessment"
            ]
            
            selected_template = st.selectbox("Edit Template", prompt_templates)
            
            if selected_template:
                template_text = st.text_area(
                    "Template Content",
                    value="You are an expert insurance underwriter. Analyze the following application...",
                    height=150
                )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Save Model Configuration"):
                st.success("Model configuration saved!")
        with col2:
            if st.button("Test Configuration"):
                st.info("Running configuration test...")
        with col3:
            if st.button("Reset to Defaults"):
                st.warning("Configuration reset to defaults!")

def render_notifications():
    """Render notifications and logging interface"""
    st.markdown('<div class="main-header"><h1>📩 Notifications & System Logging</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔔 Active Notifications", "📋 Event Logs", "⚙️ Alert Settings"])
    
    with tab1:
        st.subheader("🔔 Active Notifications")
        
        # Notification filters
        col1, col2, col3 = st.columns(3)
        with col1:
            severity_filter = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"])
        with col2:
            type_filter = st.selectbox("Type", ["All", "SLA Breach", "System Error", "Fraud Alert", "Compliance"])
        with col3:
            status_filter = st.selectbox("Status", ["All", "Unread", "Read", "Acknowledged"])
        
        # Mock notifications
        notifications = [
            {
                "ID": "NOT-001",
                "Type": "SLA Breach",
                "Severity": "High",
                "Message": "Claim CLM-2045 has exceeded 48-hour processing SLA",
                "Time": "2 hours ago",
                "Status": "Unread",
                "Action": "Review Required"
            },
            {
                "ID": "NOT-002", 
                "Type": "Fraud Alert",
                "Severity": "Critical",
                "Message": "Potential fraud ring detected - 8 related claims identified",
                "Time": "30 minutes ago",
                "Status": "Unread",
                "Action": "Investigate"
            },
            {
                "ID": "NOT-003",
                "Type": "System Error",
                "Severity": "Medium",
                "Message": "AI model response time degraded - average 3.2s (target: 2.0s)",
                "Time": "1 hour ago",
                "Status": "Acknowledged",
                "Action": "Monitor"
            },
            {
                "ID": "NOT-004",
                "Type": "Compliance",
                "Severity": "High", 
                "Message": "Quarterly regulatory report due in 3 days",
                "Time": "4 hours ago",
                "Status": "Read",
                "Action": "Prepare Report"
            },
            {
                "ID": "NOT-005",
                "Type": "Customer Complaint",
                "Severity": "Medium",
                "Message": "Customer escalation received for claim denial CLM-2038",
                "Time": "6 hours ago",
                "Status": "Read",
                "Action": "Review Case"
            }
        ]
        
        # Display notifications
        for notif in notifications:
            if notif["Severity"] == "Critical":
                card_class = "danger-card"
            elif notif["Severity"] == "High":
                card_class = "alert-card"
            else:
                card_class = "success-card"
            
            status_icon = "🔴" if notif["Status"] == "Unread" else "🟡" if notif["Status"] == "Acknowledged" else "🟢"
            
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{status_icon} {notif['Type']} - {notif['Severity']}</strong><br>
                        {notif['Message']}<br>
                        <small>{notif['Time']} | Action: {notif['Action']}</small>
                    </div>
                    <div>
                        <button style="margin: 2px; padding: 5px 10px; border: none; border-radius: 3px; background: #007bff; color: white;">Acknowledge</button>
                        <button style="margin: 2px; padding: 5px 10px; border: none; border-radius: 3px; background: #28a745; color: white;">Resolve</button>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Notification summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Notifications", "47", "↑ 8 today")
        with col2:
            st.metric("Unread", "12", "↑ 3")
        with col3:
            st.metric("Critical", "3", "↑ 1")
        with col4:
            st.metric("Avg Response Time", "23 min", "↓ 5 min")
    
    with tab2:
        st.subheader("📋 System Event Logs")
        
        # Log filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            log_level = st.selectbox("Log Level", ["All", "ERROR", "WARN", "INFO", "DEBUG"])
        with col2:
            component = st.selectbox("Component", ["All", "AI Service", "Database", "API", "Authentication"])
        with col3:
            time_range = st.selectbox("Time Range", ["Last Hour", "Last 24 Hours", "Last Week", "Last Month"])
        with col4:
            search_logs = st.text_input("Search Logs", placeholder="Search log messages...")
        
        # Mock log entries
        log_entries = [
            {
                "Timestamp": "2024-01-15 14:32:15",
                "Level": "INFO",
                "Component": "AI Service",
                "Message": "Underwriting analysis completed for policy POL-1089",
                "User": "system",
                "Request ID": "req-789123"
            },
            {
                "Timestamp": "2024-01-15 14:31:45",
                "Level": "WARN", 
                "Component": "API",
                "Message": "Rate limit approaching for user admin@company.com",
                "User": "admin@company.com",
                "Request ID": "req-789122"
            },
            {
                "Timestamp": "2024-01-15 14:30:22",
                "Level": "ERROR",
                "Component": "Database",
                "Message": "Connection timeout to PostgreSQL database",
                "User": "system",
                "Request ID": "req-789121"
            },
            {
                "Timestamp": "2024-01-15 14:29:18",
                "Level": "INFO",
                "Component": "Authentication",
                "Message": "User login successful",
                "User": "underwriter@company.com",
                "Request ID": "req-789120"
            },
            {
                "Timestamp": "2024-01-15 14:28:55",
                "Level": "DEBUG",
                "Component": "AI Service",
                "Message": "LLM API call completed - tokens used: 245",
                "User": "system",
                "Request ID": "req-789119"
            }
        ]
        
        # Display logs in a table format
        df_logs = pd.DataFrame(log_entries)
        st.dataframe(df_logs, use_container_width=True, height=400)
        
        # Log analytics
        col1, col2 = st.columns(2)
        
        with col1:
            # Log level distribution
            log_levels = ["INFO", "WARN", "ERROR", "DEBUG"]
            log_counts = [45, 12, 8, 23]
            
            fig_logs = px.pie(
                values=log_counts,
                names=log_levels,
                title="Log Level Distribution (24h)"
            )
            st.plotly_chart(fig_logs, use_container_width=True)
        
        with col2:
            # Error trend
            hours = list(range(24))
            error_counts = [random.randint(0, 5) for _ in hours]
            
            fig_errors = px.line(
                x=hours,
                y=error_counts,
                title="Error Count by Hour",
                labels={'x': 'Hour', 'y': 'Error Count'}
            )
            st.plotly_chart(fig_errors, use_container_width=True)
        
        # Export logs
        if st.button("Export Logs (JSON)"):
            st.download_button(
                label="Download Log Export",
                data=json.dumps(log_entries, indent=2),
                file_name=f"system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with tab3:
        st.subheader("⚙️ Alert Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**SLA Alert Settings:**")
            
            sla_claims_hours = st.number_input("Claims Processing SLA (hours)", 1, 72, 24)
            sla_underwriting_hours = st.number_input("Underwriting SLA (hours)", 1, 168, 48)
            sla_response_time = st.number_input("API Response Time SLA (seconds)", 1, 10, 3)
            
            st.markdown("**Fraud Detection Alerts:**")
            fraud_threshold = st.slider("Fraud Score Alert Threshold", 0.0, 1.0, 0.7, 0.01)
            fraud_cluster_size = st.number_input("Fraud Cluster Alert Size", 2, 20, 5)
            
            st.markdown("**System Performance Alerts:**")
            cpu_threshold = st.slider("CPU Usage Alert (%)", 50, 100, 80)
            memory_threshold = st.slider("Memory Usage Alert (%)", 50, 100, 85)
            error_rate_threshold = st.slider("Error Rate Alert (%)", 1, 20, 5)
        
        with col2:
            st.markdown("**Notification Channels:**")
            
            email_notifications = st.checkbox("Email Notifications", True)
            if email_notifications:
                email_addresses = st.text_area("Email Recipients", "admin@company.com\nmanager@company.com")
            
            slack_notifications = st.checkbox("Slack Notifications", False)
            if slack_notifications:
                slack_webhook = st.text_input("Slack Webhook URL")
            
            sms_notifications = st.checkbox("SMS Notifications", False)
            if sms_notifications:
                sms_numbers = st.text_area("SMS Recipients", "+1234567890")
            
            st.markdown("**Alert Frequency:**")
            alert_frequency = st.selectbox("Alert Frequency", ["Immediate", "Every 5 minutes", "Every 15 minutes", "Hourly"])
            
            st.markdown("**Quiet Hours:**")
            enable_quiet_hours = st.checkbox("Enable Quiet Hours")
            if enable_quiet_hours:
                quiet_start = st.time_input("Quiet Hours Start", datetime.strptime("22:00", "%H:%M").time())
                quiet_end = st.time_input("Quiet Hours End", datetime.strptime("06:00", "%H:%M").time())
        
        if st.button("Save Alert Configuration"):
            st.success("Alert configuration saved successfully!")

def render_user_management():
    """Render user management and access control"""
    st.markdown('<div class="main-header"><h1>👤 User Management & Access Control</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👥 User Accounts", "🔐 Role Management", "📊 Session Logs"])
    
    with tab1:
        st.subheader("👥 User Account Management")
        
        # User search and filters
        col1, col2, col3 = st.columns(3)
        with col1:
            user_search = st.text_input("Search Users", placeholder="Name, email, or role...")
        with col2:
            role_filter = st.selectbox("Filter by Role", ["All", "Admin", "Underwriter", "Claims Adjuster", "Actuary", "Compliance"])
        with col3:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive", "Suspended"])
        
        # Mock user data
        users = [
            {
                "ID": "USR-001",
                "Name": "John Smith",
                "Email": "john.smith@company.com",
                "Role": "Admin",
                "Status": "Active",
                "Last Login": "2024-01-15 09:30",
                "Sessions": 247,
                "Created": "2023-06-15"
            },
            {
                "ID": "USR-002",
                "Name": "Sarah Johnson", 
                "Email": "sarah.johnson@company.com",
                "Role": "Underwriter",
                "Status": "Active",
                "Last Login": "2024-01-15 14:22",
                "Sessions": 189,
                "Created": "2023-08-20"
            },
            {
                "ID": "USR-003",
                "Name": "Mike Wilson",
                "Email": "mike.wilson@company.com", 
                "Role": "Claims Adjuster",
                "Status": "Active",
                "Last Login": "2024-01-15 11:45",
                "Sessions": 156,
                "Created": "2023-09-10"
            },
            {
                "ID": "USR-004",
                "Name": "Lisa Chen",
                "Email": "lisa.chen@company.com",
                "Role": "Actuary",
                "Status": "Inactive",
                "Last Login": "2024-01-10 16:30",
                "Sessions": 98,
                "Created": "2023-11-05"
            },
            {
                "ID": "USR-005",
                "Name": "David Brown",
                "Email": "david.brown@company.com",
                "Role": "Compliance",
                "Status": "Active", 
                "Last Login": "2024-01-15 08:15",
                "Sessions": 134,
                "Created": "2023-07-22"
            }
        ]
        
        df_users = pd.DataFrame(users)
        st.dataframe(df_users, use_container_width=True)
        
        # User management actions
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("👤 User Details")
            
            selected_user = st.selectbox("Select User", df_users['Name'].tolist())
            
            if selected_user:
                user_data = df_users[df_users['Name'] == selected_user].iloc[0]
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.text_input("Full Name", value=user_data['Name'])
                    st.text_input("Email", value=user_data['Email'])
                    st.selectbox("Role", ["Admin", "Underwriter", "Claims Adjuster", "Actuary", "Compliance"], 
                               index=["Admin", "Underwriter", "Claims Adjuster", "Actuary", "Compliance"].index(user_data['Role']))
                
                with col_b:
                    st.selectbox("Status", ["Active", "Inactive", "Suspended"], 
                               index=["Active", "Inactive", "Suspended"].index(user_data['Status']))
                    st.text_input("Department", value="Insurance Operations")
                    st.text_input("Manager", value="Jane Doe")
                
                # Permissions
                st.markdown("**Permissions:**")
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    st.checkbox("View Policies", True)
                    st.checkbox("Edit Policies", user_data['Role'] in ['Admin', 'Underwriter'])
                    st.checkbox("View Claims", True)
                with col_p2:
                    st.checkbox("Edit Claims", user_data['Role'] in ['Admin', 'Claims Adjuster'])
                    st.checkbox("View Analytics", True)
                    st.checkbox("Export Data", user_data['Role'] in ['Admin', 'Actuary'])
                with col_p3:
                    st.checkbox("System Admin", user_data['Role'] == 'Admin')
                    st.checkbox("User Management", user_data['Role'] == 'Admin')
                    st.checkbox("Audit Logs", user_data['Role'] in ['Admin', 'Compliance'])
        
        with col2:
            st.subheader("🔧 Quick Actions")
            
            if st.button("Reset Password"):
                st.success("Password reset email sent!")
            
            if st.button("Suspend User"):
                st.warning("User suspended!")
            
            if st.button("Activate User"):
                st.success("User activated!")
            
            if st.button("Delete User"):
                st.error("User deleted!")
            
            st.markdown("---")
            st.subheader("📈 User Statistics")
            
            user_stats = {
                "Total Users": 47,
                "Active Users": 42,
                "Inactive Users": 5,
                "New This Month": 3,
                "Avg Sessions/User": 156
            }
            
            for stat, value in user_stats.items():
                st.metric(stat, value)
        
        # Add new user
        with st.expander("➕ Add New User"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Full Name", key="new_name")
                new_email = st.text_input("Email", key="new_email")
                new_role = st.selectbox("Role", ["Underwriter", "Claims Adjuster", "Actuary", "Compliance", "Admin"], key="new_role")
            with col2:
                new_department = st.text_input("Department", key="new_dept")
                new_manager = st.text_input("Manager", key="new_manager")
                send_welcome = st.checkbox("Send Welcome Email", True)
            
            if st.button("Create User"):
                st.success(f"User {new_name} created successfully!")
    
    with tab2:
        st.subheader("🔐 Role-Based Access Control")
        
        # Role definitions
        roles = {
            "Admin": {
                "description": "Full system access and user management",
                "permissions": ["All Permissions"],
                "users": 2,
                "color": "#dc3545"
            },
            "Underwriter": {
                "description": "Policy creation, editing, and risk assessment",
                "permissions": ["View/Edit Policies", "Risk Assessment", "AI Underwriting"],
                "users": 12,
                "color": "#007bff"
            },
            "Claims Adjuster": {
                "description": "Claims processing and investigation",
                "permissions": ["View/Edit Claims", "Fraud Detection", "Settlement Authorization"],
                "users": 18,
                "color": "#28a745"
            },
            "Actuary": {
                "description": "Risk analysis and pricing models",
                "permissions": ["View Analytics", "Export Data", "Model Configuration"],
                "users": 8,
                "color": "#ffc107"
            },
            "Compliance": {
                "description": "Regulatory compliance and audit",
                "permissions": ["Audit Logs", "Compliance Reports", "Ethics Monitoring"],
                "users": 7,
                "color": "#6f42c1"
            }
        }
        
        # Role overview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            for role_name, role_data in roles.items():
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: {role_data['color']};">
                    <h4>{role_name} ({role_data['users']} users)</h4>
                    <p>{role_data['description']}</p>
                    <p><strong>Permissions:</strong> {', '.join(role_data['permissions'])}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📊 Role Distribution")
            
            role_names = list(roles.keys())
            role_counts = [roles[role]['users'] for role in role_names]
            
            fig_roles = px.pie(
                values=role_counts,
                names=role_names,
                title="Users by Role"
            )
            st.plotly_chart(fig_roles, use_container_width=True)
            
            st.subheader("🔧 Role Management")
            
            selected_role = st.selectbox("Edit Role", role_names)
            
            if selected_role:
                st.text_input("Role Name", value=selected_role)
                st.text_area("Description", value=roles[selected_role]['description'])
                
                st.markdown("**Permissions:**")
                all_permissions = [
                    "View Policies", "Edit Policies", "View Claims", "Edit Claims",
                    "View Analytics", "Export Data", "User Management", "System Admin",
                    "Audit Logs", "AI Configuration", "Fraud Detection"
                ]
                
                for perm in all_permissions:
                    st.checkbox(perm, key=f"perm_{perm}")
                
                if st.button("Update Role"):
                    st.success("Role updated successfully!")
    
    with tab3:
        st.subheader("📊 Session Logs & Activity Monitoring")
        
        # Session filters
        col1, col2, col3 = st.columns(3)
        with col1:
            session_user_filter = st.selectbox("User", ["All"] + df_users['Name'].tolist())
        with col2:
            session_time_filter = st.selectbox("Time Range", ["Last Hour", "Last 24 Hours", "Last Week", "Last Month"])
        with col3:
            session_action_filter = st.selectbox("Action Type", ["All", "Login", "Logout", "Policy Access", "Claims Access", "Config Change"])
        
        # Mock session data
        session_logs = [
            {
                "Timestamp": "2024-01-15 14:30:22",
                "User": "John Smith",
                "Action": "Login",
                "IP Address": "192.168.1.100",
                "User Agent": "Chrome 120.0.0.0",
                "Status": "Success",
                "Details": "Successful login"
            },
            {
                "Timestamp": "2024-01-15 14:25:15",
                "User": "Sarah Johnson",
                "Action": "Policy Access",
                "IP Address": "192.168.1.101",
                "User Agent": "Firefox 121.0.0.0",
                "Status": "Success",
                "Details": "Viewed policy POL-1089"
            },
            {
                "Timestamp": "2024-01-15 14:20:08",
                "User": "Mike Wilson",
                "Action": "Claims Access",
                "IP Address": "192.168.1.102",
                "User Agent": "Chrome 120.0.0.0",
                "Status": "Success",
                "Details": "Processed claim CLM-2045"
            },
            {
                "Timestamp": "2024-01-15 14:15:33",
                "User": "Unknown",
                "Action": "Login",
                "IP Address": "203.0.113.1",
                "User Agent": "Unknown",
                "Status": "Failed",
                "Details": "Invalid credentials"
            },
            {
                "Timestamp": "2024-01-15 14:10:45",
                "User": "David Brown",
                "Action": "Config Change",
                "IP Address": "192.168.1.103",
                "User Agent": "Chrome 120.0.0.0",
                "Status": "Success",
                "Details": "Updated AI model settings"
            }
        ]
        
        df_sessions = pd.DataFrame(session_logs)
        st.dataframe(df_sessions, use_container_width=True, height=300)
        
        # Session analytics
        col1, col2 = st.columns(2)
        
        with col1:
            # Login success rate
            success_rate = 0.94
            failed_logins = 12
            
            st.metric("Login Success Rate", f"{success_rate:.1%}", "↑ 2.1%")
            st.metric("Failed Logins (24h)", failed_logins, "↓ 3")
            st.metric("Active Sessions", 23, "→ 0")
            st.metric("Avg Session Duration", "2.3 hours", "↑ 15 min")
            
            # Security alerts
            st.markdown("**Security Alerts:**")
            security_alerts = [
                "Multiple failed logins from IP 203.0.113.1",
                "Unusual login time for user Lisa Chen",
                "New device login for Mike Wilson"
            ]
            
            for alert in security_alerts:
                st.markdown(f"🔴 {alert}")
        
        with col2:
            # Activity heatmap
            hours = list(range(24))
            activity = [random.randint(5, 25) for _ in hours]
            
            fig_activity = px.bar(
                x=hours,
                y=activity,
                title="User Activity by Hour",
                labels={'x': 'Hour', 'y': 'Active Users'}
            )
            st.plotly_chart(fig_activity, use_container_width=True)
            
            # Geographic distribution
            locations = ['Office Network', 'VPN', 'Mobile', 'Home', 'Unknown']
            location_counts = [45, 23, 12, 8, 2]
            
            fig_geo = px.pie(
                values=location_counts,
                names=locations,
                title="Login Locations"
            )
            st.plotly_chart(fig_geo, use_container_width=True)

def render_human_escalation():
    """Render human escalation and co-pilot interface"""
    st.markdown('<div class="main-header"><h1>📞 Human Escalation & AI Co-Pilot</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🤝 Live Co-Pilot", "👤 Case Assignment", "🔄 Reprocessing Queue"])
    
    with tab1:
        st.subheader("🤝 AI Co-Pilot Chat Interface")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Chat interface
            st.markdown("### 💬 Chat with AI Assistant")
            
            # Chat history
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = [
                    {"role": "assistant", "message": "Hello! I'm your AI co-pilot. How can I assist you today?", "timestamp": "14:30:00"},
                    {"role": "user", "message": "I need help analyzing claim CLM-2045. The AI flagged it for fraud but I'm not sure why.", "timestamp": "14:30:15"},
                    {"role": "assistant", "message": "Let me analyze claim CLM-2045 for you. I found several factors that triggered the fraud alert:\n\n1. **Unusual damage pattern**: The reported damage doesn't match typical collision patterns\n2. **Repair shop**: The chosen repair shop has been flagged in 3 other suspicious claims\n3. **Timing**: Claim filed exactly 24 hours after policy activation\n4. **Amount**: $4,500 claim is 2.3x higher than average for this incident type\n\nWould you like me to provide more details on any of these factors?", "timestamp": "14:30:45"}
                ]
            
            # Display chat history
            chat_container = st.container()
            with chat_container:
                for chat in st.session_state.chat_history:
                    if chat["role"] == "user":
                        st.markdown(f"""
                        <div style="text-align: right; margin: 10px 0;">
                            <div style="background: #007bff; color: white; padding: 10px; border-radius: 10px; display: inline-block; max-width: 70%;">
                                {chat['message']}
                            </div>
                            <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
                                You - {chat['timestamp']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="text-align: left; margin: 10px 0;">
                            <div style="background: #f1f3f4; padding: 10px; border-radius: 10px; display: inline-block; max-width: 70%;">
                                {chat['message']}
                            </div>
                            <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
                                AI Assistant - {chat['timestamp']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Chat input
            user_input = st.text_input("Type your message...", key="chat_input")
            
            col_send, col_clear = st.columns([1, 4])
            with col_send:
                if st.button("Send") and user_input:
                    # Add user message
                    st.session_state.chat_history.append({
                        "role": "user",
                        "message": user_input,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    
                    # Generate AI response (mock)
                    ai_responses = [
                        "I understand your concern. Let me analyze that for you...",
                        "Based on the data, I recommend the following approach...",
                        "That's a great question. Here's what I found...",
                        "I can help you with that. Let me pull up the relevant information..."
                    ]
                    
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "message": random.choice(ai_responses),
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    
                    st.rerun()
            
            with col_clear:
                if st.button("Clear Chat"):
                    st.session_state.chat_history = []
                    st.rerun()
        
        with col2:
            st.subheader("🎯 Quick Actions")
            
            # Quick action buttons
            if st.button("🔍 Analyze Current Case"):
                st.info("Analyzing case with AI...")
            
            if st.button("📊 Get Risk Assessment"):
                st.info("Generating risk assessment...")
            
            if st.button("🕵️ Check Fraud Indicators"):
                st.info("Checking fraud indicators...")
            
            if st.button("📋 Generate Summary"):
                st.info("Generating case summary...")
            
            if st.button("⚖️ Suggest Decision"):
                st.info("AI is analyzing and will suggest a decision...")
            
            st.markdown("---")
            st.subheader("📈 Co-Pilot Stats")
            
            copilot_stats = {
                "Queries Today": 47,
                "Avg Response Time": "1.2s",
                "Accuracy Rating": "94%",
                "Cases Assisted": 23,
                "Time Saved": "3.2 hours"
            }
            
            for stat, value in copilot_stats.items():
                st.metric(stat, value)
            
            st.markdown("---")
            st.subheader("🔧 AI Settings")
            
            ai_mode = st.selectbox("AI Mode", ["Detailed Analysis", "Quick Insights", "Expert Mode"])
            confidence_threshold = st.slider("Confidence Threshold", 0.5, 1.0, 0.8)
            include_explanations = st.checkbox("Include Explanations", True)
    
    with tab2:
        st.subheader("👤 Human Case Assignment")
        
        # Assignment overview
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pending Assignment", "12", "↑ 3")
        with col2:
            st.metric("Assigned Cases", "34", "↑ 7")
        with col3:
            st.metric("Completed Today", "18", "↑ 5")
        with col4:
            st.metric("Avg Resolution Time", "4.2 hours", "↓ 0.8h")
        
        # Cases requiring human assignment
        st.subheader("📋 Cases Requiring Human Review")
        
        pending_cases = [
            {
                "Case ID": "CLM-2045",
                "Type": "Claims",
                "Priority": "High",
                "Reason": "Fraud suspicion - requires investigation",
                "AI Confidence": "67%",
                "Estimated Time": "2-4 hours",
                "Suggested Assignee": "Mike Wilson (Claims Specialist)"
            },
            {
                "Case ID": "POL-1089",
                "Type": "Underwriting",
                "Priority": "Medium", 
                "Reason": "Complex risk profile - manual review needed",
                "AI Confidence": "72%",
                "Estimated Time": "1-2 hours",
                "Suggested Assignee": "Sarah Johnson (Senior Underwriter)"
            },
            {
                "Case ID": "DSP-003",
                "Type": "Dispute",
                "Priority": "High",
                "Reason": "Customer escalation - requires personal attention",
                "AI Confidence": "N/A",
                "Estimated Time": "3-5 hours",
                "Suggested Assignee": "David Brown (Compliance Manager)"
            },
            {
                "Case ID": "CLM-2051",
                "Type": "Claims",
                "Priority": "Low",
                "Reason": "Unusual damage pattern - verification needed",
                "AI Confidence": "78%",
                "Estimated Time": "1 hour",
                "Suggested Assignee": "Lisa Chen (Claims Adjuster)"
            }
        ]
        
        for case in pending_cases:
            priority_color = "#dc3545" if case["Priority"] == "High" else "#ffc107" if case["Priority"] == "Medium" else "#28a745"
            
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {priority_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4>{case['Case ID']} - {case['Type']} ({case['Priority']} Priority)</h4>
                        <p><strong>Reason:</strong> {case['Reason']}</p>
                        <p><strong>AI Confidence:</strong> {case['AI Confidence']} | <strong>Est. Time:</strong> {case['Estimated Time']}</p>
                        <p><strong>Suggested:</strong> {case['Suggested Assignee']}</p>
                    </div>
                    <div>
                        <button style="margin: 2px; padding: 8px 15px; border: none; border-radius: 5px; background: #007bff; color: white;">Assign</button>
                        <button style="margin: 2px; padding: 8px 15px; border: none; border-radius: 5px; background: #28a745; color: white;">Auto-Assign</button>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Assignment interface
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📝 Manual Assignment")
            
            case_to_assign = st.selectbox("Select Case", [case["Case ID"] for case in pending_cases])
            assignee = st.selectbox("Assign To", [
                "Sarah Johnson (Senior Underwriter)",
                "Mike Wilson (Claims Specialist)", 
                "Lisa Chen (Claims Adjuster)",
                "David Brown (Compliance Manager)",
                "John Smith (Admin)"
            ])
            priority = st.selectbox("Set Priority", ["Low", "Medium", "High", "Critical"])
            due_date = st.date_input("Due Date", datetime.now() + timedelta(days=1))
            notes = st.text_area("Assignment Notes", placeholder="Add any special instructions...")
            
            if st.button("Assign Case"):
                st.success(f"Case {case_to_assign} assigned to {assignee}!")
        
        with col2:
            st.subheader("👥 Team Workload")
            
            team_workload = [
                {"Name": "Sarah Johnson", "Active Cases": 8, "Capacity": "75%", "Specialization": "Underwriting"},
                {"Name": "Mike Wilson", "Active Cases": 12, "Capacity": "90%", "Specialization": "Claims"},
                {"Name": "Lisa Chen", "Active Cases": 6, "Capacity": "60%", "Specialization": "Claims"},
                {"Name": "David Brown", "Active Cases": 4, "Capacity": "40%", "Specialization": "Compliance"},
                {"Name": "John Smith", "Active Cases": 2, "Capacity": "20%", "Specialization": "Admin"}
            ]
            
            for member in team_workload:
                capacity_color = "#dc3545" if int(member["Capacity"].rstrip('%')) > 85 else "#ffc107" if int(member["Capacity"].rstrip('%')) > 70 else "#28a745"
                
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid {capacity_color};">
                    <strong>{member['Name']}</strong> ({member['Specialization']})<br>
                    Active Cases: {member['Active Cases']} | Capacity: {member['Capacity']}
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.subheader("🔄 Reprocessing & Re-analysis Queue")
        
        # Reprocessing metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Queue Length", "8", "↓ 2")
        with col2:
            st.metric("Processing Rate", "15/hour", "↑ 3")
        with col3:
            st.metric("Success Rate", "92%", "↑ 5%")
        with col4:
            st.metric("Avg Processing Time", "12 min", "↓ 3 min")
        
        # Reprocessing queue
        st.subheader("📋 Reprocessing Queue")
        
        reprocess_queue = [
            {
                "Item ID": "CLM-2038",
                "Type": "Claim Re-analysis",
                "Reason": "New evidence provided",
                "Status": "Processing",
                "Requested By": "Mike Wilson",
                "Requested At": "2024-01-15 13:45",
                "Priority": "High"
            },
            {
                "Item ID": "POL-1087",
                "Type": "Policy Re-evaluation", 
                "Reason": "Updated risk model",
                "Status": "Queued",
                "Requested By": "Sarah Johnson",
                "Requested At": "2024-01-15 12:30",
                "Priority": "Medium"
            },
            {
                "Item ID": "CLM-2042",
                "Type": "Fraud Re-check",
                "Reason": "False positive reported",
                "Status": "Queued",
                "Requested By": "Lisa Chen",
                "Requested At": "2024-01-15 11:15",
                "Priority": "Low"
            }
        ]
        
        df_reprocess = pd.DataFrame(reprocess_queue)
        st.dataframe(df_reprocess, use_container_width=True)
        
        # Reprocessing controls
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🔄 Request Reprocessing")
            
            reprocess_type = st.selectbox("Reprocessing Type", [
                "Claim Re-analysis",
                "Policy Re-evaluation", 
                "Fraud Re-check",
                "Risk Re-assessment",
                "Complete Re-processing"
            ])
            
            item_id = st.text_input("Item ID (Policy/Claim/etc.)")
            reason = st.text_area("Reason for Reprocessing", placeholder="Explain why reprocessing is needed...")
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            
            # Advanced options
            with st.expander("Advanced Options"):
                use_latest_model = st.checkbox("Use Latest AI Model", True)
                include_human_feedback = st.checkbox("Include Human Feedback", False)
                force_reprocess = st.checkbox("Force Complete Reprocessing", False)
                notify_completion = st.checkbox("Notify on Completion", True)
            
            if st.button("Submit for Reprocessing"):
                st.success(f"Item {item_id} queued for reprocessing!")
        
        with col2:
            st.subheader("📊 Reprocessing Analytics")
            
            # Reprocessing reasons
            reasons = ["New Evidence", "Model Update", "False Positive", "Human Override", "System Error"]
            reason_counts = [12, 8, 15, 6, 4]
            
            fig_reasons = px.pie(
                values=reason_counts,
                names=reasons,
                title="Reprocessing Reasons (Last 30 Days)"
            )
            st.plotly_chart(fig_reasons, use_container_width=True)
            
            # Success rate trend
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            success_rates = [88, 92, 89, 94, 91, 87, 93]
            
            fig_success = px.line(
                x=days,
                y=success_rates,
                title="Reprocessing Success Rate",
                labels={'x': 'Day', 'y': 'Success Rate (%)'}
            )
            st.plotly_chart(fig_success, use_container_width=True)
            
            st.markdown("**Recent Completions:**")
            completions = [
                "CLM-2035: Approved after re-analysis",
                "POL-1082: Risk score updated", 
                "CLM-2040: Fraud flag removed",
                "POL-1085: Premium adjusted"
            ]
            
            for completion in completions:
                st.markdown(f"✅ {completion}")

# Main application
def main():
    """Main application function"""
    
    # Render navigation
    render_navigation()
    
    # Render current page
    if st.session_state.current_page == 'Dashboard':
        render_dashboard()
    elif st.session_state.current_page == 'Policy Management':
        render_policy_management()
    elif st.session_state.current_page == 'Claims Processing':
        render_claims_processing()
    elif st.session_state.current_page == 'Analytics':
        render_analytics()
    elif st.session_state.current_page == 'Fraud Detection':
        render_fraud_detection()
    elif st.session_state.current_page == 'Knowledge Base':
        render_knowledge_base()
    elif st.session_state.current_page == 'System Config':
        render_system_config()
    elif st.session_state.current_page == 'Notifications':
        render_notifications()
    elif st.session_state.current_page == 'User Management':
        render_user_management()
    elif st.session_state.current_page == 'Human Escalation':
        render_human_escalation()

if __name__ == "__main__":
    main()