"""
Professional Insurance AI Backoffice Application

A comprehensive Streamlit application for insurance professionals to leverage AI
for document analysis, risk assessment, claims processing, and actuarial analysis.
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

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from main import InsuranceAIApplication
from config.settings import get_settings
from utils import extract_text_from_files, get_answer

# Page configuration
st.set_page_config(
    page_title="Insurance AI Professional Suite",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2a5298;
    }
    
    .analysis-result {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #2a5298 0%, #1e3c72 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

class ProfessionalInsuranceUI:
    """Professional Insurance AI Application UI"""
    
    def __init__(self):
        self.app = None
        self.settings = get_settings()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        if 'app_initialized' not in st.session_state:
            st.session_state.app_initialized = False
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
        if 'current_analysis' not in st.session_state:
            st.session_state.current_analysis = None
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

    def render_chatbot(self):
        """Render simple QA chatbot."""
        with st.sidebar.expander("💬 Chat with Assistant", expanded=False):
            question = st.text_input("Ask a question", key="pro_chat_input")
            if question:
                answer = get_answer(question)
                st.session_state.chat_history.append(("You", question))
                st.session_state.chat_history.append(("Assistant", answer))

            for speaker, text in st.session_state.chat_history[-6:]:
                st.markdown(f"**{speaker}:** {text}")
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
    
    async def initialize_app(self):
        """Initialize the Insurance AI Application"""
        if not st.session_state.app_initialized:
            try:
                self.app = InsuranceAIApplication()
                await self.app.initialize()
                st.session_state.app_initialized = True
                return True
            except Exception as e:
                st.error(f"Failed to initialize AI system: {e}")
                return False
        return True
    
    def render_header(self):
        """Render the main header"""
        st.markdown("""
        <div class="main-header">
            <h1>🏢 Insurance AI Professional Suite</h1>
            <p>Advanced AI-Powered Insurance Operations Platform</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar navigation"""
        st.sidebar.title("🎯 Navigation")
        
        # System status
        st.sidebar.subheader("📊 System Status")
        if st.session_state.app_initialized:
            st.sidebar.success("✅ AI System Online")
        else:
            st.sidebar.warning("⚠️ AI System Initializing...")
        
        # AI Provider info
        st.sidebar.subheader("🤖 AI Configuration")
        st.sidebar.info(f"Provider: {self.settings.ai.provider.upper()}")
        st.sidebar.info(f"Model: {self.settings.ai.model}")
        
        # Navigation menu
        st.sidebar.subheader("📋 Operations")
        page = st.sidebar.selectbox(
            "Select Operation",
            [
                "🏠 Dashboard",
                "📄 Document Analysis",
                "⚖️ Underwriting Assistant",
                "🔍 Claims Processing",
                "📊 Actuarial Analysis",
                "📈 Analytics & Reports",
                "⚙️ System Settings"
            ]
        )

        self.render_chatbot()

        return page
    
    def render_dashboard(self):
        """Render the main dashboard"""
        st.header("🏠 Dashboard")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>📄 Documents Processed</h3>
                <h2 style="color: #2a5298;">1,247</h2>
                <p style="color: #28a745;">↗️ +12% this month</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>⚖️ Underwriting Decisions</h3>
                <h2 style="color: #2a5298;">856</h2>
                <p style="color: #28a745;">↗️ +8% this month</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>🔍 Claims Processed</h3>
                <h2 style="color: #2a5298;">432</h2>
                <p style="color: #ffc107;">→ +2% this month</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3>💰 Cost Savings</h3>
                <h2 style="color: #2a5298;">$127K</h2>
                <p style="color: #28a745;">↗️ +15% this month</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Recent activity
        st.subheader("📋 Recent Activity")
        
        # Sample data for demonstration
        recent_data = pd.DataFrame({
            'Time': [
                datetime.now() - timedelta(minutes=5),
                datetime.now() - timedelta(minutes=15),
                datetime.now() - timedelta(minutes=30),
                datetime.now() - timedelta(hours=1),
                datetime.now() - timedelta(hours=2)
            ],
            'Operation': [
                'Document Analysis',
                'Underwriting Decision',
                'Claims Processing',
                'Risk Assessment',
                'Actuarial Report'
            ],
            'Status': ['Completed', 'Approved', 'Under Review', 'Completed', 'Generated'],
            'User': ['John Smith', 'Sarah Johnson', 'Mike Davis', 'Lisa Chen', 'Robert Wilson']
        })
        
        st.dataframe(recent_data, use_container_width=True)
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Processing Volume Trend")
            # Sample chart data
            dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
            volumes = [50 + i*2 + (i%7)*10 for i in range(len(dates))]
            
            fig = px.line(x=dates, y=volumes, title="Daily Processing Volume")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Decision Distribution")
            # Sample pie chart data
            decisions = ['Approved', 'Denied', 'Pending Review', 'Referred']
            counts = [65, 15, 12, 8]
            
            fig = px.pie(values=counts, names=decisions, title="Underwriting Decisions")
            st.plotly_chart(fig, use_container_width=True)
    
    def render_document_analysis(self):
        """Render document analysis interface"""
        st.header("📄 Document Analysis")
        st.write("Upload insurance documents for AI-powered analysis and insights.")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload Documents",
            type=['pdf', 'docx', 'txt', 'jpg', 'png'],
            accept_multiple_files=True,
            help="Supported formats: PDF, DOCX, TXT, JPG, PNG"
        )
        
        # Analysis options
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_type = st.selectbox(
                "Analysis Type",
                [
                    "General Document Analysis",
                    "Policy Document Review",
                    "Claims Document Processing",
                    "Application Form Analysis",
                    "Medical Records Review",
                    "Financial Statement Analysis"
                ]
            )
        
        with col2:
            custom_prompt = st.text_area(
                "Custom Analysis Prompt (Optional)",
                placeholder="Enter specific instructions for the AI analysis...",
                height=100
            )
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                extract_entities = st.checkbox("Extract Named Entities", value=True)
                sentiment_analysis = st.checkbox("Sentiment Analysis", value=False)
            
            with col2:
                risk_assessment = st.checkbox("Risk Assessment", value=True)
                compliance_check = st.checkbox("Compliance Check", value=True)
            
            with col3:
                generate_summary = st.checkbox("Generate Summary", value=True)
                extract_key_data = st.checkbox("Extract Key Data", value=True)
        
        # Process documents
        if st.button("🚀 Analyze Documents", type="primary"):
            if uploaded_files:
                self._process_documents(uploaded_files, analysis_type, custom_prompt)
            else:
                st.warning("Please upload at least one document.")
    
    def _process_documents(self, files, analysis_type, custom_prompt):
        """Process uploaded documents"""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, file in enumerate(files):
            status_text.text(f"Processing {file.name}...")
            progress_bar.progress((i + 1) / len(files))
            
            # Simulate document processing
            import time
            time.sleep(1)
            
            # Display results
            st.markdown(f"""
            <div class="analysis-result">
                <h4>📄 {file.name}</h4>
                <p><strong>Analysis Type:</strong> {analysis_type}</p>
                <p><strong>File Size:</strong> {file.size:,} bytes</p>
                <p><strong>Status:</strong> <span style="color: #28a745;">✅ Processed Successfully</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Sample analysis results
            with st.expander(f"📊 Analysis Results - {file.name}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🎯 Key Findings")
                    st.write("• Document type: Insurance Application")
                    st.write("• Completeness: 95%")
                    st.write("• Risk indicators: 2 identified")
                    st.write("• Compliance status: Compliant")
                
                with col2:
                    st.subheader("📈 Risk Assessment")
                    risk_score = 25
                    st.metric("Risk Score", f"{risk_score}/100", "Low Risk")
                    
                    # Risk gauge
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = risk_score,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Risk Level"},
                        gauge = {
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 25], 'color': "lightgreen"},
                                {'range': [25, 50], 'color': "yellow"},
                                {'range': [50, 75], 'color': "orange"},
                                {'range': [75, 100], 'color': "red"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 90
                            }
                        }
                    ))
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
        
        status_text.text("✅ All documents processed successfully!")
    
    def render_underwriting_assistant(self):
        """Render underwriting assistant interface"""
        st.header("⚖️ Underwriting Assistant")
        st.write("AI-powered underwriting decisions and risk assessment.")
        
        # Application input
        with st.form("underwriting_form"):
            st.subheader("📋 Application Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                applicant_name = st.text_input("Applicant Name")
                age = st.number_input("Age", min_value=18, max_value=100, value=35)
                income = st.number_input("Annual Income ($)", min_value=0, value=75000)
                credit_score = st.number_input("Credit Score", min_value=300, max_value=850, value=720)
            
            with col2:
                policy_type = st.selectbox("Policy Type", [
                    "Auto Insurance",
                    "Home Insurance",
                    "Life Insurance",
                    "Health Insurance",
                    "Business Insurance"
                ])
                coverage_amount = st.number_input("Coverage Amount ($)", min_value=0, value=250000)
                property_value = st.number_input("Property Value ($)", min_value=0, value=300000)
                debt_to_income = st.slider("Debt-to-Income Ratio", 0.0, 1.0, 0.25, 0.01)

            uploaded_docs = st.file_uploader(
                "Upload Supporting Documents",
                type=["pdf", "png", "jpg", "jpeg"],
                accept_multiple_files=True,
                help="Scanned forms, IDs, or other relevant files",
            )
            
            # Additional information
            st.subheader("📝 Additional Information")
            additional_info = st.text_area(
                "Additional Notes",
                placeholder="Enter any additional information about the applicant or application...",
                height=100
            )
            
            submitted = st.form_submit_button("🎯 Analyze Application", type="primary")
            
            if submitted:
                extracted_text = extract_text_from_files(uploaded_docs)
                if extracted_text:
                    additional_info = (additional_info + "\n" + extracted_text).strip()
                    st.info("Text extracted from uploaded documents has been appended to notes.")

                self._process_underwriting_application({
                    "applicant_name": applicant_name,
                    "age": age,
                    "income": income,
                    "credit_score": credit_score,
                    "policy_type": policy_type,
                    "coverage_amount": coverage_amount,
                    "property_value": property_value,
                    "debt_to_income_ratio": debt_to_income,
                    "additional_info": additional_info
                })
    
    def _process_underwriting_application(self, application_data):
        """Process underwriting application"""
        with st.spinner("🤖 AI is analyzing the application..."):
            # Simulate AI processing
            import time
            time.sleep(2)
            
            # Sample results
            risk_score = 28
            decision = "APPROVED"
            premium_adjustment = 1.05
            
            # Display results
            st.success("✅ Analysis Complete!")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Risk Score", f"{risk_score}/100", "Low Risk")
            
            with col2:
                st.metric("Decision", decision, "Recommended")
            
            with col3:
                st.metric("Premium Adjustment", f"{premium_adjustment:.2f}x", "+5%")
            
            # Detailed analysis
            st.subheader("📊 Detailed Analysis")
            
            with st.expander("🎯 Risk Factors Analysis"):
                st.write("**Positive Factors:**")
                st.write("• Excellent credit score (720)")
                st.write("• Stable income level")
                st.write("• Low debt-to-income ratio")
                st.write("• Property in low-risk area")
                
                st.write("**Risk Factors:**")
                st.write("• Age group has moderate claim frequency")
                st.write("• Coverage amount is above average")
            
            with st.expander("💰 Premium Calculation"):
                base_premium = 1200
                adjusted_premium = base_premium * premium_adjustment
                
                st.write(f"**Base Premium:** ${base_premium:,.2f}")
                st.write(f"**Risk Adjustment:** {premium_adjustment:.2f}x")
                st.write(f"**Final Premium:** ${adjusted_premium:,.2f}")
            
            with st.expander("📋 Recommendations"):
                st.write("• Approve application with standard terms")
                st.write("• Consider loyalty discount for long-term customers")
                st.write("• Schedule annual review for coverage adequacy")
    
    def render_claims_processing(self):
        """Render claims processing interface"""
        st.header("🔍 Claims Processing")
        st.write("Intelligent claims analysis and processing assistance.")
        
        # Claims input form
        with st.form("claims_form"):
            st.subheader("📋 Claim Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                claim_id = st.text_input("Claim ID", value=f"CL-{datetime.now().strftime('%Y%m%d')}-001")
                policy_number = st.text_input("Policy Number")
                claimant_name = st.text_input("Claimant Name")
                incident_date = st.date_input("Incident Date")
            
            with col2:
                claim_type = st.selectbox("Claim Type", [
                    "Auto Accident",
                    "Property Damage",
                    "Theft",
                    "Fire Damage",
                    "Water Damage",
                    "Medical Claim",
                    "Other"
                ])
                estimated_amount = st.number_input("Estimated Claim Amount ($)", min_value=0, value=5000)
                urgency = st.selectbox("Urgency Level", ["Low", "Medium", "High", "Critical"])
            
            # Incident description
            st.subheader("📝 Incident Description")
            incident_description = st.text_area(
                "Describe the incident",
                placeholder="Provide detailed description of what happened...",
                height=150
            )
            
            # Supporting documents
            st.subheader("📎 Supporting Documents")
            claim_documents = st.file_uploader(
                "Upload supporting documents",
                type=['pdf', 'jpg', 'png', 'docx'],
                accept_multiple_files=True
            )
            
            submitted = st.form_submit_button("🔍 Process Claim", type="primary")
            
            if submitted:
                self._process_claim({
                    "claim_id": claim_id,
                    "policy_number": policy_number,
                    "claimant_name": claimant_name,
                    "incident_date": incident_date,
                    "claim_type": claim_type,
                    "estimated_amount": estimated_amount,
                    "urgency": urgency,
                    "incident_description": incident_description,
                    "documents": claim_documents
                })
    
    def _process_claim(self, claim_data):
        """Process insurance claim"""
        with st.spinner("🤖 AI is analyzing the claim..."):
            import time
            time.sleep(2)
            
            # Sample analysis results
            fraud_risk = 15
            coverage_status = "COVERED"
            settlement_amount = claim_data["estimated_amount"] * 0.95
            
            st.success("✅ Claim Analysis Complete!")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Fraud Risk", f"{fraud_risk}%", "Low")
            
            with col2:
                st.metric("Coverage", coverage_status, "Eligible")
            
            with col3:
                st.metric("Settlement", f"${settlement_amount:,.2f}", "Recommended")
            
            with col4:
                processing_time = "2-3 days"
                st.metric("Processing Time", processing_time, "Standard")
            
            # Detailed analysis
            st.subheader("📊 Detailed Analysis")
            
            with st.expander("🔍 Fraud Detection Analysis"):
                st.write("**Fraud Indicators Checked:**")
                st.write("✅ Incident timing and location")
                st.write("✅ Claimant history and patterns")
                st.write("✅ Claim amount vs. policy limits")
                st.write("✅ Supporting documentation quality")
                
                st.write("**Risk Assessment:**")
                st.write(f"• Overall fraud risk: {fraud_risk}% (Low)")
                st.write("• No suspicious patterns detected")
                st.write("• Documentation appears authentic")
            
            with st.expander("📋 Coverage Analysis"):
                st.write("**Policy Coverage Review:**")
                st.write("✅ Incident covered under policy terms")
                st.write("✅ Policy is active and premiums current")
                st.write("✅ Claim within policy limits")
                st.write("✅ No exclusions apply")
                
                deductible = 500
                st.write(f"**Settlement Calculation:**")
                st.write(f"• Estimated damage: ${claim_data['estimated_amount']:,.2f}")
                st.write(f"• Deductible: ${deductible:,.2f}")
                st.write(f"• Recommended settlement: ${settlement_amount:,.2f}")
            
            with st.expander("⚡ Next Steps"):
                st.write("**Recommended Actions:**")
                st.write("1. Approve claim for settlement")
                st.write("2. Schedule property inspection if needed")
                st.write("3. Process payment within 2-3 business days")
                st.write("4. Send settlement letter to claimant")
                
                if st.button("✅ Approve Settlement"):
                    st.success("Claim approved for settlement!")
    
    def render_actuarial_analysis(self):
        """Render actuarial analysis interface"""
        st.header("📊 Actuarial Analysis")
        st.write("Advanced statistical analysis and risk modeling.")
        
        # Analysis type selection
        analysis_type = st.selectbox(
            "Select Analysis Type",
            [
                "Risk Model Development",
                "Premium Pricing Analysis", 
                "Claims Trend Analysis",
                "Loss Ratio Analysis",
                "Market Segmentation",
                "Predictive Modeling"
            ]
        )
        
        # Data input options
        st.subheader("📈 Data Input")
        
        data_source = st.radio(
            "Data Source",
            ["Upload CSV File", "Use Sample Data", "Connect to Database"]
        )
        
        if data_source == "Upload CSV File":
            uploaded_file = st.file_uploader("Upload CSV Data", type=['csv'])
            if uploaded_file:
                df = pd.read_csv(uploaded_file)
                st.write("Data Preview:")
                st.dataframe(df.head(), use_container_width=True)
        
        elif data_source == "Use Sample Data":
            # Generate sample actuarial data
            import numpy as np
            np.random.seed(42)
            
            n_records = 1000
            sample_data = pd.DataFrame({
                'age': np.random.normal(40, 15, n_records).astype(int),
                'gender': np.random.choice(['M', 'F'], n_records),
                'policy_type': np.random.choice(['Auto', 'Home', 'Life'], n_records),
                'premium': np.random.normal(1200, 400, n_records),
                'claims_count': np.random.poisson(0.3, n_records),
                'claim_amount': np.random.exponential(2000, n_records),
                'region': np.random.choice(['North', 'South', 'East', 'West'], n_records)
            })
            
            st.write("Sample Data Preview:")
            st.dataframe(sample_data.head(), use_container_width=True)
            df = sample_data
        
        # Analysis parameters
        with st.expander("🔧 Analysis Parameters"):
            col1, col2 = st.columns(2)
            
            with col1:
                confidence_level = st.slider("Confidence Level", 0.90, 0.99, 0.95, 0.01)
                time_horizon = st.selectbox("Time Horizon", ["1 Year", "2 Years", "5 Years"])
            
            with col2:
                risk_tolerance = st.selectbox("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"])
                model_type = st.selectbox("Model Type", ["GLM", "Random Forest", "Neural Network"])
        
        # Run analysis
        if st.button("🚀 Run Analysis", type="primary"):
            self._run_actuarial_analysis(analysis_type, df if 'df' in locals() else None)
    
    def _run_actuarial_analysis(self, analysis_type, data):
        """Run actuarial analysis"""
        with st.spinner("🤖 Running actuarial analysis..."):
            import time
            time.sleep(3)
            
            st.success("✅ Analysis Complete!")
            
            # Results tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "📈 Visualizations", "🎯 Insights", "📋 Recommendations"])
            
            with tab1:
                st.subheader("Analysis Summary")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Loss Ratio", "68.5%", "-2.3%")
                    st.metric("Combined Ratio", "95.2%", "-1.8%")
                
                with col2:
                    st.metric("Expected Claims", "1,247", "+5.2%")
                    st.metric("Risk Score", "72/100", "Moderate")
                
                with col3:
                    st.metric("Premium Adequacy", "102.3%", "+0.8%")
                    st.metric("Profit Margin", "4.8%", "+0.3%")
                
                # Key findings
                st.subheader("🎯 Key Findings")
                st.write("• Loss ratios are within acceptable range")
                st.write("• Claims frequency has increased by 5.2% year-over-year")
                st.write("• Premium pricing appears adequate for current risk profile")
                st.write("• Recommend monitoring emerging risk factors")
            
            with tab2:
                st.subheader("Data Visualizations")
                
                if data is not None:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Claims by age group
                        age_groups = pd.cut(data['age'], bins=[0, 30, 45, 60, 100], labels=['<30', '30-45', '45-60', '60+'])
                        age_claims = data.groupby(age_groups)['claims_count'].mean()
                        
                        fig = px.bar(x=age_claims.index, y=age_claims.values, title="Average Claims by Age Group")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Premium distribution
                        fig = px.histogram(data, x='premium', title="Premium Distribution", nbins=30)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Claims trend over time
                    st.subheader("📈 Claims Trend Analysis")
                    dates = pd.date_range(start='2023-01-01', end='2024-01-31', freq='M')
                    claims_trend = [100 + i*2 + np.random.normal(0, 10) for i in range(len(dates))]
                    
                    fig = px.line(x=dates, y=claims_trend, title="Monthly Claims Trend")
                    fig.add_hline(y=np.mean(claims_trend), line_dash="dash", line_color="red", 
                                annotation_text="Average")
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.subheader("🔍 Actuarial Insights")
                
                st.write("**Risk Segmentation Analysis:**")
                st.write("• High-risk segment: Ages 18-25, represents 15% of portfolio but 28% of claims")
                st.write("• Low-risk segment: Ages 45-60, represents 35% of portfolio but 22% of claims")
                st.write("• Geographic concentration: 40% of high-severity claims from urban areas")
                
                st.write("**Predictive Indicators:**")
                st.write("• Credit score correlation with claims: -0.34 (moderate negative)")
                st.write("• Prior claims history: Strong predictor of future claims (R² = 0.67)")
                st.write("• Seasonal patterns: 23% increase in claims during winter months")
                
                st.write("**Emerging Trends:**")
                st.write("• Technology-related claims increasing 12% annually")
                st.write("• Climate-related losses up 18% in coastal regions")
                st.write("• Cyber liability exposure growing across all segments")
            
            with tab4:
                st.subheader("📋 Strategic Recommendations")
                
                st.write("**Immediate Actions (0-3 months):**")
                st.write("• Implement dynamic pricing for high-risk segments")
                st.write("• Enhance underwriting criteria for ages 18-25")
                st.write("• Review geographic concentration limits")
                
                st.write("**Medium-term Initiatives (3-12 months):**")
                st.write("• Develop predictive models for emerging risks")
                st.write("• Implement usage-based insurance programs")
                st.write("• Expand data collection for better risk assessment")
                
                st.write("**Long-term Strategy (1+ years):**")
                st.write("• Invest in climate risk modeling capabilities")
                st.write("• Develop cyber insurance expertise")
                st.write("• Build partnerships for alternative data sources")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📊 Generate Report"):
                        st.success("Detailed report generated!")
                with col2:
                    if st.button("📧 Share Analysis"):
                        st.success("Analysis shared with stakeholders!")
                with col3:
                    if st.button("💾 Save Model"):
                        st.success("Model saved to repository!")
    
    def render_analytics_reports(self):
        """Render analytics and reports interface"""
        st.header("📈 Analytics & Reports")
        st.write("Comprehensive business intelligence and reporting.")
        
        # Report type selection
        report_type = st.selectbox(
            "Select Report Type",
            [
                "Executive Dashboard",
                "Underwriting Performance",
                "Claims Analysis Report",
                "Financial Performance",
                "Risk Management Report",
                "Regulatory Compliance"
            ]
        )
        
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        # Generate report
        if st.button("📊 Generate Report", type="primary"):
            self._generate_report(report_type, start_date, end_date)
    
    def _generate_report(self, report_type, start_date, end_date):
        """Generate analytics report"""
        with st.spinner("📊 Generating report..."):
            import time
            time.sleep(2)
            
            st.success(f"✅ {report_type} generated successfully!")
            
            # Sample report content
            if report_type == "Executive Dashboard":
                # KPI metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Premium", "$12.4M", "+8.2%")
                with col2:
                    st.metric("Claims Ratio", "67.3%", "-2.1%")
                with col3:
                    st.metric("New Policies", "2,847", "+12.5%")
                with col4:
                    st.metric("Customer Satisfaction", "4.6/5", "+0.2")
                
                # Charts
                st.subheader("📈 Performance Trends")
                
                # Sample data for charts
                dates = pd.date_range(start=start_date, end=end_date, freq='D')
                revenue = [100000 + i*1000 + np.random.normal(0, 5000) for i in range(len(dates))]
                
                fig = px.line(x=dates, y=revenue, title="Daily Revenue Trend")
                st.plotly_chart(fig, use_container_width=True)
            
            # Download report
            st.subheader("📥 Download Report")
            
            # Create sample report data
            report_data = {
                'Metric': ['Premium Revenue', 'Claims Paid', 'New Policies', 'Renewals'],
                'Current Period': ['$12.4M', '$8.3M', '2,847', '18,392'],
                'Previous Period': ['$11.5M', '$8.5M', '2,531', '17,845'],
                'Change': ['+7.8%', '-2.4%', '+12.5%', '+3.1%']
            }
            
            df_report = pd.DataFrame(report_data)
            
            # Convert to CSV for download
            csv = df_report.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV Report",
                data=csv,
                file_name=f"{report_type.lower().replace(' ', '_')}_report.csv",
                mime="text/csv"
            )
    
    def render_system_settings(self):
        """Render system settings interface"""
        st.header("⚙️ System Settings")
        st.write("Configure AI system parameters and preferences.")
        
        # AI Configuration
        st.subheader("🤖 AI Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_provider = st.selectbox(
                "AI Provider",
                ["OpenAI", "Anthropic", "Local LLM"],
                index=0 if self.settings.ai.provider == "openai" else 1 if self.settings.ai.provider == "anthropic" else 2
            )
            
            model_options = {
                "OpenAI": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
                "Anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                "Local LLM": ["llama2-7b", "llama2-13b", "mistral-7b"]
            }
            
            current_model = st.selectbox(
                "Model",
                model_options[current_provider],
                index=0
            )
        
        with col2:
            temperature = st.slider("Temperature", 0.0, 1.0, float(self.settings.ai.temperature), 0.1)
            max_tokens = st.number_input("Max Tokens", 100, 4000, self.settings.ai.max_tokens)
        
        # Performance Settings
        st.subheader("⚡ Performance Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_caching = st.checkbox("Enable Caching", value=self.settings.ai.enable_caching)
            enable_fallback = st.checkbox("Enable Provider Fallback", value=self.settings.ai.enable_fallback)
        
        with col2:
            timeout = st.number_input("Request Timeout (seconds)", 10, 120, self.settings.ai.timeout)
            max_retries = st.number_input("Max Retries", 1, 5, self.settings.ai.max_retries)
        
        # Security Settings
        st.subheader("🔒 Security Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            log_level = st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"], index=1)
            enable_audit = st.checkbox("Enable Audit Logging", value=True)
        
        with col2:
            session_timeout = st.number_input("Session Timeout (minutes)", 15, 480, 60)
            require_2fa = st.checkbox("Require Two-Factor Authentication", value=False)
        
        # Save settings
        if st.button("💾 Save Settings", type="primary"):
            st.success("✅ Settings saved successfully!")
            st.info("Some changes may require system restart to take effect.")
        
        # System status
        st.subheader("📊 System Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("System Health", "Healthy", "✅")
            st.metric("AI Provider Status", "Online", "✅")
        
        with col2:
            st.metric("Active Sessions", "23", "+5")
            st.metric("API Calls Today", "1,247", "+12%")
        
        with col3:
            st.metric("Response Time", "1.2s", "-0.3s")
            st.metric("Success Rate", "99.7%", "+0.1%")

def main():
    """Main application function"""
    ui = ProfessionalInsuranceUI()
    
    # Render header
    ui.render_header()
    
    # Render sidebar and get selected page
    page = ui.render_sidebar()
    
    # Initialize app if needed
    if not st.session_state.app_initialized:
        with st.spinner("🚀 Initializing AI System..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(ui.initialize_app())
            if not success:
                st.error("Failed to initialize AI system. Please check configuration.")
                return
    
    # Route to appropriate page
    if page == "🏠 Dashboard":
        ui.render_dashboard()
    elif page == "📄 Document Analysis":
        ui.render_document_analysis()
    elif page == "⚖️ Underwriting Assistant":
        ui.render_underwriting_assistant()
    elif page == "🔍 Claims Processing":
        ui.render_claims_processing()
    elif page == "📊 Actuarial Analysis":
        ui.render_actuarial_analysis()
    elif page == "📈 Analytics & Reports":
        ui.render_analytics_reports()
    elif page == "⚙️ System Settings":
        ui.render_system_settings()

if __name__ == "__main__":
    main()