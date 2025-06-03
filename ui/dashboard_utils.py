"""
Dashboard Utilities

Utility functions for the Insurance AI System Dashboard.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import asyncio
import httpx

class APIClient:
    """API client for dashboard backend communication"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip("/")
        self.timeout = 30
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params or {})
                response.raise_for_status()
                return response.json()
        except Exception as e:
            st.error(f"API Error: {e}")
            return {}
    
    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=data or {})
                response.raise_for_status()
                return response.json()
        except Exception as e:
            st.error(f"API Error: {e}")
            return {}
    
    async def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PUT request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(url, json=data or {})
                response.raise_for_status()
                return response.json()
        except Exception as e:
            st.error(f"API Error: {e}")
            return {}

def get_api_client() -> APIClient:
    """Get API client instance"""
    if 'api_client' not in st.session_state:
        st.session_state.api_client = APIClient()
    return st.session_state.api_client

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_dashboard_metrics() -> Dict[str, Any]:
    """Fetch dashboard metrics with caching"""
    try:
        # Synchronous version for Streamlit compatibility
        import requests
        response = requests.get("http://localhost:8080/api/dashboard/metrics", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.warning(f"Could not fetch live metrics: {e}")
    
    # Return mock data if API is not available
    return {
        "total_policies": 1247,
        "claims_processed": 89,
        "flagged_risks": 15,
        "pending_reviews": 7,
        "ai_accuracy": 0.942
    }

@st.cache_data(ttl=300)
def fetch_policies(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Fetch policies with caching"""
    try:
        import requests
        params = {"limit": limit, "offset": offset}
        response = requests.get("http://localhost:8080/api/policies", params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.warning(f"Could not fetch live policies: {e}")
    
    # Return mock data
    return {
        "policies": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }

@st.cache_data(ttl=300)
def fetch_claims(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Fetch claims with caching"""
    try:
        import requests
        params = {"limit": limit, "offset": offset}
        response = requests.get("http://localhost:8080/api/claims", params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.warning(f"Could not fetch live claims: {e}")
    
    # Return mock data
    return {
        "claims": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value:.1%}"

def format_datetime(dt: datetime) -> str:
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M")

def get_status_color(status: str) -> str:
    """Get color for status"""
    status_colors = {
        "Active": "#28a745",
        "Pending": "#ffc107", 
        "Expired": "#6c757d",
        "Cancelled": "#dc3545",
        "Open": "#17a2b8",
        "Under Review": "#ffc107",
        "Approved": "#28a745",
        "Denied": "#dc3545",
        "Closed": "#6c757d",
        "High": "#dc3545",
        "Medium": "#ffc107",
        "Low": "#28a745",
        "Critical": "#dc3545"
    }
    return status_colors.get(status, "#6c757d")

def create_metric_card(title: str, value: str, delta: str = None, help_text: str = None):
    """Create a metric card"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.metric(
            label=title,
            value=value,
            delta=delta,
            help=help_text
        )

def create_status_badge(status: str) -> str:
    """Create HTML status badge"""
    color = get_status_color(status)
    return f"""
    <span style="
        background-color: {color};
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: bold;
    ">{status}</span>
    """

def create_progress_bar(value: float, max_value: float = 100, color: str = "#2a5298") -> str:
    """Create HTML progress bar"""
    percentage = (value / max_value) * 100
    return f"""
    <div style="
        width: 100%;
        background-color: #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        height: 20px;
    ">
        <div style="
            width: {percentage}%;
            background-color: {color};
            height: 100%;
            transition: width 0.3s ease;
        "></div>
    </div>
    <small>{value}/{max_value} ({percentage:.1f}%)</small>
    """

def create_trend_chart(data: List[Dict], x_col: str, y_col: str, title: str) -> go.Figure:
    """Create a trend line chart"""
    df = pd.DataFrame(data)
    
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        title=title,
        markers=True
    )
    
    fig.update_layout(
        height=300,
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

def create_pie_chart(data: Dict[str, float], title: str) -> go.Figure:
    """Create a pie chart"""
    fig = px.pie(
        values=list(data.values()),
        names=list(data.keys()),
        title=title
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

def create_bar_chart(data: List[Dict], x_col: str, y_col: str, title: str) -> go.Figure:
    """Create a bar chart"""
    df = pd.DataFrame(data)
    
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        title=title
    )
    
    fig.update_layout(
        height=300,
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

def create_heatmap(data: List[List[float]], x_labels: List[str], y_labels: List[str], title: str) -> go.Figure:
    """Create a heatmap"""
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=x_labels,
        y=y_labels,
        colorscale='Blues'
    ))
    
    fig.update_layout(
        title=title,
        height=400,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

def display_data_table(data: List[Dict], columns: List[str] = None, height: int = 400):
    """Display data in a table format"""
    if not data:
        st.info("No data available")
        return
    
    df = pd.DataFrame(data)
    
    if columns:
        df = df[columns]
    
    st.dataframe(df, use_container_width=True, height=height)

def create_alert_card(alert_type: str, severity: str, message: str, timestamp: datetime):
    """Create an alert card"""
    severity_colors = {
        "Critical": "#dc3545",
        "High": "#fd7e14",
        "Medium": "#ffc107",
        "Low": "#28a745"
    }
    
    color = severity_colors.get(severity, "#6c757d")
    
    st.markdown(f"""
    <div style="
        border-left: 4px solid {color};
        background: #f8f9fa;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    ">
        <strong>{alert_type} - {severity}</strong><br>
        {message}<br>
        <small style="color: #6c757d;">{format_datetime(timestamp)}</small>
    </div>
    """, unsafe_allow_html=True)

def show_loading_spinner(text: str = "Loading..."):
    """Show loading spinner"""
    with st.spinner(text):
        return True

def validate_api_connection() -> bool:
    """Validate API connection"""
    try:
        import requests
        response = requests.get("http://localhost:8080/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def show_api_status():
    """Show API connection status"""
    if validate_api_connection():
        st.success("✅ Connected to API")
    else:
        st.error("❌ API connection failed - using mock data")

def export_data_to_csv(data: List[Dict], filename: str):
    """Export data to CSV"""
    if not data:
        st.warning("No data to export")
        return
    
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label=f"Download {filename}",
        data=csv,
        file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def export_data_to_json(data: Dict[str, Any], filename: str):
    """Export data to JSON"""
    if not data:
        st.warning("No data to export")
        return
    
    json_str = json.dumps(data, indent=2, default=str)
    
    st.download_button(
        label=f"Download {filename}",
        data=json_str,
        file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def create_notification_toast(message: str, type: str = "info"):
    """Create a notification toast"""
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)

def format_large_number(number: int) -> str:
    """Format large numbers with K, M, B suffixes"""
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)

def calculate_percentage_change(current: float, previous: float) -> float:
    """Calculate percentage change"""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

def get_time_ago(timestamp: datetime) -> str:
    """Get human-readable time ago"""
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def create_sidebar_metric(label: str, value: str, delta: str = None):
    """Create a sidebar metric"""
    st.sidebar.metric(label, value, delta)

def create_expandable_section(title: str, content_func, expanded: bool = False):
    """Create an expandable section"""
    with st.expander(title, expanded=expanded):
        content_func()

def apply_custom_css():
    """Apply custom CSS styling"""
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
        
        .stMetric {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .sidebar .sidebar-content {
            background: #f8f9fa;
        }
        
        .stSelectbox > div > div {
            background: white;
        }
        
        .stDataFrame {
            border: 1px solid #dee2e6;
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)