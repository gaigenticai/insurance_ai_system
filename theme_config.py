"""
Theme Configuration System for Insurance AI Dashboard

This module provides a robust theme configuration system that enables
dynamic switching between light and dark modes, as well as custom theming
capabilities for the Insurance AI Dashboard.
"""

import streamlit as st
from typing import Dict, Any, Optional
import json
import os

# Theme configuration constants
LIGHT_THEME = {
    "primaryColor": "#2563EB",        # Royal Blue
    "backgroundColor": "#F9FAFB",     # Off White
    "secondaryBackgroundColor": "#F3F4F6",  # Light Gray
    "textColor": "#111827",           # Near Black
    "font": "Inter, sans-serif"
}

DARK_THEME = {
    "primaryColor": "#3B82F6",        # Bright Blue
    "backgroundColor": "#111827",     # Near Black
    "secondaryBackgroundColor": "#1F2937",  # Dark Gray
    "textColor": "#F9FAFB",           # Off White
    "font": "Inter, sans-serif"
}

# Additional color palette for components
LIGHT_PALETTE = {
    "accent": "#3B82F6",      # Bright Blue
    "success": "#10B981",     # Emerald
    "warning": "#F59E0B",     # Amber
    "danger": "#EF4444",      # Red
    "info": "#6366F1",        # Indigo
    "muted": "#9CA3AF",       # Gray
    "border": "#E5E7EB",      # Light Border
    "shadow": "rgba(0, 0, 0, 0.1)"  # Light Shadow
}

DARK_PALETTE = {
    "accent": "#60A5FA",      # Light Blue
    "success": "#34D399",     # Light Emerald
    "warning": "#FBBF24",     # Light Amber
    "danger": "#F87171",      # Light Red
    "info": "#818CF8",        # Light Indigo
    "muted": "#6B7280",       # Dark Gray
    "border": "#374151",      # Dark Border
    "shadow": "rgba(0, 0, 0, 0.25)"  # Dark Shadow
}

def initialize_theme_config():
    """Initialize theme configuration in session state"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    if 'theme_config' not in st.session_state:
        st.session_state.theme_config = LIGHT_THEME
    
    if 'color_palette' not in st.session_state:
        st.session_state.color_palette = LIGHT_PALETTE

def toggle_theme():
    """Toggle between light and dark themes"""
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
        st.session_state.theme_config = DARK_THEME
        st.session_state.color_palette = DARK_PALETTE
    else:
        st.session_state.theme = 'light'
        st.session_state.theme_config = LIGHT_THEME
        st.session_state.color_palette = LIGHT_PALETTE
    
    # Save theme preference
    save_theme_preference(st.session_state.theme)

def save_theme_preference(theme: str):
    """Save theme preference to a file"""
    config_dir = os.path.join(os.path.expanduser('~'), '.streamlit')
    os.makedirs(config_dir, exist_ok=True)
    
    config_path = os.path.join(config_dir, 'config.toml')
    
    # Create or update theme section in config.toml
    theme_config = f"""
[theme]
base = "{theme}"
primaryColor = "{st.session_state.theme_config['primaryColor']}"
backgroundColor = "{st.session_state.theme_config['backgroundColor']}"
secondaryBackgroundColor = "{st.session_state.theme_config['secondaryBackgroundColor']}"
textColor = "{st.session_state.theme_config['textColor']}"
font = "{st.session_state.theme_config['font']}"
"""
    
    # Write to config file
    with open(config_path, 'w') as f:
        f.write(theme_config)

def get_current_theme() -> str:
    """Get the current theme name"""
    return st.session_state.theme

def get_theme_config() -> Dict[str, Any]:
    """Get the current theme configuration"""
    return st.session_state.theme_config

def get_color_palette() -> Dict[str, str]:
    """Get the current color palette"""
    return st.session_state.color_palette

def apply_theme_css():
    """Apply theme CSS to the Streamlit app"""
    theme = get_current_theme()
    config = get_theme_config()
    palette = get_color_palette()
    
    # Create CSS variables for the theme
    css = f"""
    <style>
        :root {{
            --primary-color: {config['primaryColor']};
            --background-color: {config['backgroundColor']};
            --secondary-background-color: {config['secondaryBackgroundColor']};
            --text-color: {config['textColor']};
            --font: {config['font']};
            
            --accent-color: {palette['accent']};
            --success-color: {palette['success']};
            --warning-color: {palette['warning']};
            --danger-color: {palette['danger']};
            --info-color: {palette['info']};
            --muted-color: {palette['muted']};
            --border-color: {palette['border']};
            --shadow: {palette['shadow']};
        }}
        
        /* Base styles */
        .main {{
            background-color: var(--background-color);
            color: var(--text-color);
        }}
        
        .sidebar .sidebar-content {{
            background-color: var(--secondary-background-color);
        }}
        
        /* Custom component styles */
        .metric-card {{
            background: var(--secondary-background-color);
            border-left: 4px solid var(--primary-color);
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 4px 6px var(--shadow);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px var(--shadow);
        }}
        
        .main-header {{
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--accent-color) 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px var(--shadow);
            animation: gradient-shift 8s ease infinite;
            background-size: 200% 200%;
        }}
        
        @keyframes gradient-shift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        /* Alert styles */
        .success-card {{
            background: color-mix(in srgb, var(--success-color) 15%, var(--background-color));
            border-left: 4px solid var(--success-color);
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            transition: transform 0.3s ease;
        }}
        
        .success-card:hover {{
            transform: translateX(5px);
        }}
        
        .warning-card {{
            background: color-mix(in srgb, var(--warning-color) 15%, var(--background-color));
            border-left: 4px solid var(--warning-color);
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            transition: transform 0.3s ease;
        }}
        
        .warning-card:hover {{
            transform: translateX(5px);
        }}
        
        .danger-card {{
            background: color-mix(in srgb, var(--danger-color) 15%, var(--background-color));
            border-left: 4px solid var(--danger-color);
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            transition: transform 0.3s ease;
        }}
        
        .danger-card:hover {{
            transform: translateX(5px);
        }}
        
        .info-card {{
            background: color-mix(in srgb, var(--info-color) 15%, var(--background-color));
            border-left: 4px solid var(--info-color);
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            transition: transform 0.3s ease;
        }}
        
        .info-card:hover {{
            transform: translateX(5px);
        }}
        
        /* Theme toggle button */
        .theme-toggle {{
            position: fixed;
            top: 0.5rem;
            right: 0.5rem;
            z-index: 9999;
            background: var(--secondary-background-color);
            border: 1px solid var(--border-color);
            border-radius: 50%;
            width: 2.5rem;
            height: 2.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 2px 4px var(--shadow);
            transition: all 0.3s ease;
        }}
        
        .theme-toggle:hover {{
            transform: translateY(-2px) rotate(15deg);
            box-shadow: 0 4px 8px var(--shadow);
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .animate-fade-in {{
            animation: fadeIn 0.5s ease-in-out;
        }}
        
        /* Enhanced Streamlit elements */
        .stButton > button {{
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--accent-color) 100%);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px var(--shadow);
        }}
        
        .stTextInput > div > div > input {{
            border-radius: 8px;
            border: 1px solid var(--border-color);
            padding: 0.5rem;
            background-color: var(--secondary-background-color);
            color: var(--text-color);
            transition: all 0.3s ease;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary-color) 30%, transparent);
        }}
        
        .stSelectbox > div > div {{
            border-radius: 8px;
            border: 1px solid var(--border-color);
            background-color: var(--secondary-background-color);
            color: var(--text-color);
        }}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--secondary-background-color);
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--primary-color);
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--accent-color);
        }}
        
        /* Glassmorphism effects */
        .glass-effect {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        /* 3D effects */
        .effect-3d {{
            transform-style: preserve-3d;
            perspective: 1000px;
        }}
        
        /* Neumorphism effects */
        .neumorphic {{
            border-radius: 15px;
            background: var(--secondary-background-color);
            box-shadow: 
                8px 8px 16px rgba(0, 0, 0, 0.1),
                -8px -8px 16px rgba(255, 255, 255, 0.1);
        }}
    </style>
    """
    
    # Apply the CSS
    st.markdown(css, unsafe_allow_html=True)

def render_theme_toggle():
    """Render the theme toggle button"""
    theme = get_current_theme()
    icon = "🌙" if theme == 'light' else "☀️"
    
    toggle_html = f"""
    <div class="theme-toggle" onclick="toggleTheme()" title="Toggle {theme} mode">
        {icon}
    </div>
    
    <script>
    function toggleTheme() {{
        // This will trigger a form submission to toggle the theme
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'theme_toggle';
        input.value = 'toggle';
        
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    }}
    </script>
    """
    
    st.markdown(toggle_html, unsafe_allow_html=True)
    
    # Handle the form submission
    if st.button('Toggle Theme', key='theme_toggle_button', help="Switch between light and dark mode"):
        toggle_theme()
        # Use experimental_rerun for compatibility with older Streamlit versions
        st.experimental_rerun()
