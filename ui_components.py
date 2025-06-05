"""
Modern UI Components for Insurance AI Dashboard

This module provides reusable UI components with modern design and theme support
for the Insurance AI Dashboard.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any, List, Optional, Union, Tuple

# Import theme configuration
from theme_config import get_current_theme, get_theme_config, get_color_palette

def render_header(title: str, subtitle: str = None):
    """Render a modern header with title and optional subtitle"""
    theme = get_current_theme()
    palette = get_color_palette()
    
    header_html = f"""
    <div class="main-header animate-fade-in">
        <h1>{title}</h1>
        {f"<p>{subtitle}</p>" if subtitle else ""}
    </div>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)

def render_metric_card(title: str, value: str, delta: str = None, icon: str = None, help_text: str = None):
    """Render a modern metric card with animation"""
    palette = get_color_palette()
    
    delta_html = ""
    if delta:
        if delta.startswith("↑"):
            delta_color = palette["success"]
        elif delta.startswith("↓"):
            delta_color = palette["danger"]
        else:
            delta_color = palette["muted"]
        
        delta_html = f'<p style="color: {delta_color};">{delta}</p>'
    
    icon_html = f'<div class="metric-icon">{icon}</div>' if icon else ''
    
    card_html = f"""
    <div class="metric-card animate-fade-in">
        <div class="metric-content">
            <h3>{title}</h3>
            <h2 style="color: var(--primary-color);">{value}</h2>
            {delta_html}
        </div>
        {icon_html}
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def render_alert(message: str, alert_type: str = "info", dismissible: bool = False):
    """Render a modern alert component
    
    Parameters:
    - message: Alert message text
    - alert_type: One of "success", "warning", "danger", "info"
    - dismissible: Whether the alert can be dismissed
    """
    alert_class = f"{alert_type}-card"
    
    alert_icons = {
        "success": "✅",
        "warning": "⚠️",
        "danger": "🚨",
        "info": "ℹ️"
    }
    
    icon = alert_icons.get(alert_type, "ℹ️")
    
    dismiss_button = """
    <button class="dismiss-button" onclick="this.parentElement.style.display='none';">×</button>
    """ if dismissible else ""
    
    alert_html = f"""
    <div class="{alert_class} animate-fade-in">
        {dismiss_button}
        <strong>{icon} </strong>
        {message}
    </div>
    """
    
    st.markdown(alert_html, unsafe_allow_html=True)

def create_modern_chart(data_frame: pd.DataFrame, chart_type: str, 
                       x: str, y: Union[str, List[str]], 
                       title: str = None, color: str = None,
                       height: int = 400) -> go.Figure:
    """Create a modern, theme-aware chart
    
    Parameters:
    - data_frame: Pandas DataFrame with the data
    - chart_type: One of "line", "bar", "scatter", "pie", "area"
    - x: Column name for x-axis
    - y: Column name(s) for y-axis
    - title: Chart title
    - color: Column name for color differentiation
    - height: Chart height in pixels
    
    Returns:
    - Plotly figure object
    """
    theme = get_current_theme()
    config = get_theme_config()
    palette = get_color_palette()
    
    # Set theme-aware colors
    bg_color = config["backgroundColor"]
    text_color = config["textColor"]
    grid_color = palette["border"]
    
    # Create the appropriate chart type
    if chart_type == "line":
        fig = px.line(data_frame, x=x, y=y, color=color, title=title)
    elif chart_type == "bar":
        fig = px.bar(data_frame, x=x, y=y, color=color, title=title)
    elif chart_type == "scatter":
        fig = px.scatter(data_frame, x=x, y=y, color=color, title=title)
    elif chart_type == "pie":
        fig = px.pie(data_frame, values=y, names=x, title=title)
    elif chart_type == "area":
        fig = px.area(data_frame, x=x, y=y, color=color, title=title)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")
    
    # Apply theme-aware styling
    fig.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font_color=text_color,
        title_font_color=text_color,
        legend_title_font_color=text_color,
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        hovermode="closest",
        xaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            gridwidth=0.5,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            gridwidth=0.5,
            zeroline=False
        )
    )
    
    # Add subtle animation
    fig.update_traces(
        mode='lines+markers' if chart_type == "line" else None,
        marker=dict(size=8, opacity=0.8),
        line=dict(width=3),
        hovertemplate='<b>%{x}</b><br>%{y}<extra></extra>'
    )
    
    return fig

def render_data_table(data: List[Dict], columns: List[str] = None, 
                     height: int = 400, interactive: bool = True):
    """Render a modern, theme-aware data table
    
    Parameters:
    - data: List of dictionaries containing the data
    - columns: List of column names to display
    - height: Table height in pixels
    - interactive: Whether to enable sorting and filtering
    """
    if not data:
        st.info("No data available")
        return
    
    df = pd.DataFrame(data)
    
    if columns:
        df = df[columns]
    
    # Apply custom styling
    st.markdown("""
    <style>
    .dataframe-container {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid var(--border-color);
        background: var(--secondary-background-color);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, height=height)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if interactive:
        col1, col2 = st.columns([1, 1])
        with col1:
            search_term = st.text_input("🔍 Search", key=f"search_{id(data)}")
            if search_term:
                mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                st.dataframe(df[mask], use_container_width=True, height=height)
        
        with col2:
            st.download_button(
                "📥 Download Data",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

def render_sidebar_navigation(items: List[Dict[str, str]], title: str = "Navigation"):
    """Render a modern sidebar navigation
    
    Parameters:
    - items: List of dictionaries with 'id', 'label', and 'icon' keys
    - title: Navigation section title
    """
    theme = get_current_theme()
    palette = get_color_palette()
    
    st.sidebar.markdown(f"### {title}")
    
    for item in items:
        item_id = item.get('id', '')
        label = item.get('label', '')
        icon = item.get('icon', '')
        
        if st.sidebar.button(f"{icon} {label}", key=f"nav_{item_id}"):
            st.session_state.current_page = item_id
            st.rerun()
    
    st.sidebar.markdown("---")

def render_progress_bar(value: float, max_value: float = 100, 
                       label: str = None, color: str = None):
    """Render a modern, animated progress bar
    
    Parameters:
    - value: Current value
    - max_value: Maximum value
    - label: Optional label text
    - color: Optional color override
    """
    palette = get_color_palette()
    
    if not color:
        color = "var(--primary-color)"
    
    percentage = min(100, (value / max_value) * 100)
    
    label_html = f"<div class='progress-label'>{label}</div>" if label else ""
    
    progress_html = f"""
    <div class="progress-container">
        {label_html}
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: {percentage}%; background-color: {color};"></div>
        </div>
        <div class="progress-text">{value}/{max_value} ({percentage:.1f}%)</div>
    </div>
    
    <style>
    .progress-container {{
        margin: 1rem 0;
    }}
    
    .progress-label {{
        margin-bottom: 0.25rem;
        font-weight: 500;
    }}
    
    .progress-bar-bg {{
        background-color: var(--border-color);
        border-radius: 10px;
        height: 10px;
        overflow: hidden;
        width: 100%;
    }}
    
    .progress-bar-fill {{
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease-in-out;
    }}
    
    .progress-text {{
        font-size: 0.8rem;
        color: var(--muted-color);
        margin-top: 0.25rem;
        text-align: right;
    }}
    </style>
    """
    
    st.markdown(progress_html, unsafe_allow_html=True)

def render_card(title: str, content: str, footer: str = None, 
               icon: str = None, color: str = None):
    """Render a modern content card
    
    Parameters:
    - title: Card title
    - content: Card content (can include HTML)
    - footer: Optional footer text/HTML
    - icon: Optional icon
    - color: Optional accent color
    """
    palette = get_color_palette()
    
    if not color:
        color = "var(--primary-color)"
    
    icon_html = f'<span class="card-icon">{icon}</span>' if icon else ''
    footer_html = f'<div class="card-footer">{footer}</div>' if footer else ''
    
    card_html = f"""
    <div class="content-card animate-fade-in">
        <div class="card-header" style="border-color: {color};">
            {icon_html}
            <h3>{title}</h3>
        </div>
        <div class="card-body">
            {content}
        </div>
        {footer_html}
    </div>
    
    <style>
    .content-card {{
        background-color: var(--secondary-background-color);
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px var(--shadow);
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }}
    
    .card-header {{
        padding: 1rem;
        border-bottom: 1px solid var(--border-color);
        display: flex;
        align-items: center;
        border-left: 4px solid {color};
    }}
    
    .card-icon {{
        margin-right: 0.5rem;
        font-size: 1.2rem;
    }}
    
    .card-body {{
        padding: 1rem;
    }}
    
    .card-footer {{
        padding: 0.75rem 1rem;
        border-top: 1px solid var(--border-color);
        font-size: 0.9rem;
        color: var(--muted-color);
    }}
    </style>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def render_tabs(tabs: List[Dict[str, Any]]):
    """Render modern, theme-aware tabs
    
    Parameters:
    - tabs: List of dictionaries with 'label' and 'content' keys
    """
    if not tabs:
        return
    
    # Create tab labels
    tab_labels = [tab.get('label', f"Tab {i+1}") for i, tab in enumerate(tabs)]
    
    # Create streamlit tabs
    st_tabs = st.tabs(tab_labels)
    
    # Render content for each tab
    for i, tab in enumerate(tabs):
        with st_tabs[i]:
            content_func = tab.get('content')
            if callable(content_func):
                content_func()
            else:
                st.markdown(str(content_func), unsafe_allow_html=True)

def render_status_badge(status: str, size: str = "medium"):
    """Render a modern status badge
    
    Parameters:
    - status: Status text
    - size: One of "small", "medium", "large"
    """
    status_colors = {
        "Active": "var(--success-color)",
        "Pending": "var(--warning-color)",
        "Expired": "var(--muted-color)",
        "Cancelled": "var(--danger-color)",
        "Open": "var(--info-color)",
        "Under Review": "var(--warning-color)",
        "Approved": "var(--success-color)",
        "Denied": "var(--danger-color)",
        "Closed": "var(--muted-color)",
        "High": "var(--danger-color)",
        "Medium": "var(--warning-color)",
        "Low": "var(--success-color)",
        "Critical": "var(--danger-color)"
    }
    
    color = status_colors.get(status, "var(--muted-color)")
    
    size_class = {
        "small": "badge-sm",
        "medium": "badge-md",
        "large": "badge-lg"
    }.get(size, "badge-md")
    
    badge_html = f"""
    <span class="status-badge {size_class}" style="background-color: {color};">
        {status}
    </span>
    
    <style>
    .status-badge {{
        display: inline-block;
        color: white;
        border-radius: 12px;
        font-weight: 500;
        text-align: center;
    }}
    
    .badge-sm {{
        padding: 0.1rem 0.5rem;
        font-size: 0.7rem;
    }}
    
    .badge-md {{
        padding: 0.2rem 0.75rem;
        font-size: 0.8rem;
    }}
    
    .badge-lg {{
        padding: 0.3rem 1rem;
        font-size: 0.9rem;
    }}
    </style>
    """
    
    st.markdown(badge_html, unsafe_allow_html=True)

def render_notification_toast(message: str, notification_type: str = "info", 
                             duration: int = 3000, position: str = "top-right"):
    """Render a modern notification toast
    
    Parameters:
    - message: Notification message
    - notification_type: One of "success", "warning", "error", "info"
    - duration: Display duration in milliseconds
    - position: One of "top-right", "top-left", "bottom-right", "bottom-left"
    """
    notification_id = f"notification_{int(datetime.now().timestamp() * 1000)}"
    
    notification_icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }
    
    icon = notification_icons.get(notification_type, "ℹ️")
    
    toast_html = f"""
    <div id="{notification_id}" class="notification-toast {notification_type} {position}">
        <div class="notification-icon">{icon}</div>
        <div class="notification-content">{message}</div>
        <button class="notification-close" onclick="closeNotification('{notification_id}')">×</button>
    </div>
    
    <script>
    function closeNotification(id) {{
        const notification = document.getElementById(id);
        notification.classList.add('notification-hiding');
        setTimeout(() => {{
            notification.remove();
        }}, 300);
    }}
    
    // Auto-close after duration
    setTimeout(() => {{
        const notification = document.getElementById('{notification_id}');
        if (notification) {{
            notification.classList.add('notification-hiding');
            setTimeout(() => {{
                notification.remove();
            }}, 300);
        }}
    }}, {duration});
    </script>
    
    <style>
    .notification-toast {{
        position: fixed;
        display: flex;
        align-items: center;
        min-width: 300px;
        max-width: 500px;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px var(--shadow);
        z-index: 9999;
        animation: notification-slide-in 0.3s ease-out forwards;
    }}
    
    .notification-hiding {{
        animation: notification-slide-out 0.3s ease-in forwards;
    }}
    
    .notification-icon {{
        margin-right: 0.75rem;
        font-size: 1.2rem;
    }}
    
    .notification-content {{
        flex: 1;
    }}
    
    .notification-close {{
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        opacity: 0.7;
        transition: opacity 0.2s;
    }}
    
    .notification-close:hover {{
        opacity: 1;
    }}
    
    /* Types */
    .notification-toast.success {{
        background-color: var(--success-color);
        color: white;
    }}
    
    .notification-toast.warning {{
        background-color: var(--warning-color);
        color: white;
    }}
    
    .notification-toast.error {{
        background-color: var(--danger-color);
        color: white;
    }}
    
    .notification-toast.info {{
        background-color: var(--info-color);
        color: white;
    }}
    
    /* Positions */
    .notification-toast.top-right {{
        top: 20px;
        right: 20px;
    }}
    
    .notification-toast.top-left {{
        top: 20px;
        left: 20px;
    }}
    
    .notification-toast.bottom-right {{
        bottom: 20px;
        right: 20px;
    }}
    
    .notification-toast.bottom-left {{
        bottom: 20px;
        left: 20px;
    }}
    
    /* Animations */
    @keyframes notification-slide-in {{
        from {{
            transform: translateX(100%);
            opacity: 0;
        }}
        to {{
            transform: translateX(0);
            opacity: 1;
        }}
    }}
    
    @keyframes notification-slide-out {{
        from {{
            transform: translateX(0);
            opacity: 1;
        }}
        to {{
            transform: translateX(100%);
            opacity: 0;
        }}
    }}
    </style>
    """
    
    st.markdown(toast_html, unsafe_allow_html=True)

def render_ai_confidence_indicator(confidence: float, size: str = "medium"):
    """Render an AI confidence indicator
    
    Parameters:
    - confidence: Confidence score (0.0 to 1.0)
    - size: One of "small", "medium", "large"
    """
    # Determine color based on confidence
    if confidence >= 0.8:
        color = "var(--success-color)"
        label = "High Confidence"
    elif confidence >= 0.5:
        color = "var(--warning-color)"
        label = "Medium Confidence"
    else:
        color = "var(--danger-color)"
        label = "Low Confidence"
    
    size_class = {
        "small": "confidence-sm",
        "medium": "confidence-md",
        "large": "confidence-lg"
    }.get(size, "confidence-md")
    
    percentage = int(confidence * 100)
    
    indicator_html = f"""
    <div class="confidence-indicator {size_class}">
        <div class="confidence-bar-container">
            <div class="confidence-bar" style="width: {percentage}%; background-color: {color};"></div>
        </div>
        <div class="confidence-details">
            <span class="confidence-percentage">{percentage}%</span>
            <span class="confidence-label">{label}</span>
        </div>
    </div>
    
    <style>
    .confidence-indicator {{
        margin: 0.5rem 0;
    }}
    
    .confidence-bar-container {{
        background-color: var(--border-color);
        border-radius: 10px;
        overflow: hidden;
    }}
    
    .confidence-bar {{
        height: 8px;
        border-radius: 10px;
        transition: width 0.5s ease;
    }}
    
    .confidence-details {{
        display: flex;
        justify-content: space-between;
        margin-top: 0.25rem;
        font-size: 0.8rem;
    }}
    
    .confidence-percentage {{
        font-weight: 600;
    }}
    
    .confidence-label {{
        color: var(--muted-color);
    }}
    
    /* Sizes */
    .confidence-sm .confidence-bar {{
        height: 4px;
    }}
    
    .confidence-sm .confidence-details {{
        font-size: 0.7rem;
    }}
    
    .confidence-lg .confidence-bar {{
        height: 12px;
    }}
    
    .confidence-lg .confidence-details {{
        font-size: 0.9rem;
    }}
    </style>
    """
    
    st.markdown(indicator_html, unsafe_allow_html=True)
