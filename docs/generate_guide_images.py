"""
Generate placeholder images for the Insurance AI System User Guide.
Creates professional-looking mockup images for documentation.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns

# Set style for professional appearance
plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

def create_directory():
    """Create images directory if it doesn't exist."""
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    os.makedirs(images_dir, exist_ok=True)
    return images_dir

def create_dashboard_overview(images_dir):
    """Create dashboard overview mockup."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('Insurance AI System - Dashboard Overview', fontsize=20, fontweight='bold')
    
    # Metrics cards
    metrics = ['Documents\nProcessed\n1,247', 'Underwriting\nDecisions\n856', 
               'Claims\nProcessed\n432', 'Cost Savings\n$127K']
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    
    for i, (metric, color) in enumerate(zip(metrics, colors)):
        ax = plt.subplot(2, 4, i+1)
        ax.text(0.5, 0.5, metric, ha='center', va='center', fontsize=14, 
                fontweight='bold', color='white')
        ax.set_facecolor(color)
        ax.set_xticks([])
        ax.set_yticks([])
    
    # Recent activity table
    ax = plt.subplot(2, 2, 3)
    activities = [
        ['5 min ago', 'Document Analysis', 'Completed', 'John Smith'],
        ['15 min ago', 'Underwriting Decision', 'Approved', 'Sarah Johnson'],
        ['30 min ago', 'Claims Processing', 'Under Review', 'Mike Davis'],
        ['1 hour ago', 'Risk Assessment', 'Completed', 'Lisa Chen']
    ]
    
    table = ax.table(cellText=activities, 
                    colLabels=['Time', 'Operation', 'Status', 'User'],
                    cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    ax.axis('off')
    ax.set_title('Recent Activity', fontweight='bold', pad=20)
    
    # Performance chart
    ax = plt.subplot(2, 2, 4)
    dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
    volumes = [50 + i*2 + np.random.normal(0, 5) for i in range(30)]
    ax.plot(dates, volumes, linewidth=2, color='#2E86AB')
    ax.fill_between(dates, volumes, alpha=0.3, color='#2E86AB')
    ax.set_title('Processing Volume Trend', fontweight='bold')
    ax.set_ylabel('Daily Volume')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, 'dashboard_overview.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_sidebar_navigation(images_dir):
    """Create sidebar navigation mockup."""
    fig, ax = plt.subplots(figsize=(6, 12))
    
    # Navigation items
    nav_items = [
        '🏠 Dashboard',
        '📄 Document Analysis', 
        '⚖️ Underwriting Assistant',
        '🔍 Claims Processing',
        '📊 Actuarial Analysis',
        '📈 Analytics & Reports',
        '⚙️ System Settings'
    ]
    
    # Create sidebar background
    sidebar = patches.Rectangle((0, 0), 1, 1, linewidth=2, 
                               edgecolor='#E0E0E0', facecolor='#F8F9FA')
    ax.add_patch(sidebar)
    
    # Add navigation items
    for i, item in enumerate(nav_items):
        y_pos = 0.9 - (i * 0.12)
        
        # Highlight first item (Dashboard)
        if i == 0:
            highlight = patches.Rectangle((0.05, y_pos-0.04), 0.9, 0.08, 
                                        facecolor='#2E86AB', alpha=0.2)
            ax.add_patch(highlight)
        
        ax.text(0.1, y_pos, item, fontsize=12, fontweight='bold' if i == 0 else 'normal',
                color='#2E86AB' if i == 0 else '#333333')
    
    # Add system status
    ax.text(0.1, 0.15, '🤖 AI System Status', fontsize=10, fontweight='bold', color='#333333')
    ax.text(0.1, 0.10, '✅ AI System Online', fontsize=9, color='#28A745')
    ax.text(0.1, 0.06, 'Provider: OPENAI', fontsize=9, color='#6C757D')
    ax.text(0.1, 0.02, 'Model: GPT-4', fontsize=9, color='#6C757D')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('Navigation Sidebar', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, 'sidebar_navigation.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_document_analysis_interface(images_dir):
    """Create document analysis interface mockup."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Document Analysis Interface', fontsize=20, fontweight='bold')
    
    # Upload area
    upload_box = patches.Rectangle((0.1, 0.3), 0.8, 0.4, linewidth=2, 
                                  edgecolor='#2E86AB', facecolor='#F8F9FA', linestyle='--')
    ax1.add_patch(upload_box)
    ax1.text(0.5, 0.5, '📄 Drop files here or click to upload\n\nSupported: PDF, DOCX, TXT, JPG, PNG', 
             ha='center', va='center', fontsize=12, color='#6C757D')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_title('Document Upload', fontweight='bold')
    ax1.axis('off')
    
    # Analysis configuration
    config_items = [
        'Analysis Type: Policy Document Review',
        'Custom Prompt: [Optional]',
        '☑ Extract Named Entities',
        '☑ Risk Assessment', 
        '☑ Generate Summary',
        '☐ Sentiment Analysis'
    ]
    
    for i, item in enumerate(config_items):
        ax2.text(0.1, 0.9 - (i * 0.15), item, fontsize=11, 
                color='#2E86AB' if '☑' in item else '#333333')
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_title('Analysis Configuration', fontweight='bold')
    ax2.axis('off')
    
    # Processing status
    files = ['policy_document.pdf', 'application_form.docx', 'medical_records.pdf']
    statuses = ['✅ Completed', '🔄 Processing...', '⏳ Queued']
    
    for i, (file, status) in enumerate(zip(files, statuses)):
        y_pos = 0.8 - (i * 0.25)
        ax3.text(0.1, y_pos, f'📄 {file}', fontsize=11, fontweight='bold')
        ax3.text(0.1, y_pos - 0.1, status, fontsize=10, 
                color='#28A745' if '✅' in status else '#FFC107' if '🔄' in status else '#6C757D')
    
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.set_title('Processing Status', fontweight='bold')
    ax3.axis('off')
    
    # Risk gauge
    theta = np.linspace(0, np.pi, 100)
    risk_score = 25  # Low risk
    
    # Create gauge background
    ax4.plot(np.cos(theta), np.sin(theta), 'k-', linewidth=8, alpha=0.3)
    
    # Color segments
    segments = [(0, 0.25, '#28A745'), (0.25, 0.5, '#FFC107'), (0.5, 0.75, '#FD7E14'), (0.75, 1, '#DC3545')]
    for start, end, color in segments:
        segment_theta = theta[int(start*100):int(end*100)]
        ax4.plot(np.cos(segment_theta), np.sin(segment_theta), color=color, linewidth=8)
    
    # Risk indicator
    risk_angle = np.pi * (1 - risk_score/100)
    ax4.plot([0, np.cos(risk_angle)], [0, np.sin(risk_angle)], 'k-', linewidth=4)
    ax4.plot(np.cos(risk_angle), np.sin(risk_angle), 'ko', markersize=8)
    
    ax4.text(0, -0.3, f'Risk Score: {risk_score}', ha='center', fontsize=14, fontweight='bold')
    ax4.text(0, -0.5, 'Low Risk', ha='center', fontsize=12, color='#28A745')
    ax4.set_xlim(-1.2, 1.2)
    ax4.set_ylim(-0.6, 1.2)
    ax4.set_title('Risk Assessment', fontweight='bold')
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, 'document_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_underwriting_interface(images_dir):
    """Create underwriting interface mockup."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Underwriting Assistant Interface', fontsize=20, fontweight='bold')
    
    # Application form
    form_fields = [
        'Applicant Name: John Smith',
        'Age: 35',
        'Annual Income: $75,000',
        'Credit Score: 720',
        'Policy Type: Auto Insurance',
        'Coverage Amount: $250,000'
    ]
    
    for i, field in enumerate(form_fields):
        ax1.text(0.1, 0.9 - (i * 0.12), field, fontsize=11, color='#333333')
        # Add input box visual
        input_box = patches.Rectangle((0.05, 0.85 - (i * 0.12)), 0.9, 0.08, 
                                    linewidth=1, edgecolor='#CED4DA', facecolor='white')
        ax1.add_patch(input_box)
    
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_title('Application Form', fontweight='bold')
    ax1.axis('off')
    
    # AI Analysis button and options
    analyze_button = patches.Rectangle((0.2, 0.7), 0.6, 0.15, 
                                     linewidth=2, edgecolor='#2E86AB', facecolor='#2E86AB')
    ax2.add_patch(analyze_button)
    ax2.text(0.5, 0.775, '🎯 Analyze Application', ha='center', va='center', 
             fontsize=12, fontweight='bold', color='white')
    
    options = ['🤖 Use AI Analysis: ✅', 'Analysis Mode: Direct AI', 'Risk Assessment: Enabled']
    for i, option in enumerate(options):
        ax2.text(0.1, 0.5 - (i * 0.1), option, fontsize=10, color='#333333')
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_title('Analysis Options', fontweight='bold')
    ax2.axis('off')
    
    # Results metrics
    metrics = [
        ('Risk Score', '28/100', '#28A745'),
        ('Decision', 'APPROVED', '#28A745'),
        ('Premium Adj.', '1.05x', '#FFC107')
    ]
    
    for i, (label, value, color) in enumerate(metrics):
        x_pos = 0.1 + (i * 0.3)
        metric_box = patches.Rectangle((x_pos, 0.4), 0.25, 0.4, 
                                     linewidth=2, edgecolor=color, facecolor='white')
        ax3.add_patch(metric_box)
        ax3.text(x_pos + 0.125, 0.65, value, ha='center', va='center', 
                fontsize=14, fontweight='bold', color=color)
        ax3.text(x_pos + 0.125, 0.5, label, ha='center', va='center', 
                fontsize=10, color='#333333')
    
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.set_title('Analysis Results', fontweight='bold')
    ax3.axis('off')
    
    # Risk factors analysis
    factors = [
        '✅ Excellent credit score (720)',
        '✅ Stable income level', 
        '✅ Low debt-to-income ratio',
        '⚠️ Age group moderate risk',
        '⚠️ Coverage above average'
    ]
    
    for i, factor in enumerate(factors):
        color = '#28A745' if '✅' in factor else '#FFC107'
        ax4.text(0.1, 0.9 - (i * 0.15), factor, fontsize=10, color=color)
    
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.set_title('Risk Factors Analysis', fontweight='bold')
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, 'underwriting_interface.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_claims_interface(images_dir):
    """Create claims processing interface mockup."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Claims Processing Interface', fontsize=20, fontweight='bold')
    
    # Claim details form
    claim_fields = [
        'Claim ID: CL-20250603-001',
        'Policy Number: POL-123456',
        'Claimant: Jane Doe',
        'Incident Date: 2025-06-01',
        'Claim Type: Auto Accident',
        'Estimated Amount: $5,000'
    ]
    
    for i, field in enumerate(claim_fields):
        ax1.text(0.1, 0.9 - (i * 0.12), field, fontsize=11, color='#333333')
        input_box = patches.Rectangle((0.05, 0.85 - (i * 0.12)), 0.9, 0.08, 
                                    linewidth=1, edgecolor='#CED4DA', facecolor='white')
        ax1.add_patch(input_box)
    
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_title('Claim Details', fontweight='bold')
    ax1.axis('off')
    
    # Supporting documents
    documents = ['📷 accident_photos.jpg', '📄 police_report.pdf', '📋 repair_estimate.pdf']
    for i, doc in enumerate(documents):
        ax2.text(0.1, 0.8 - (i * 0.2), doc, fontsize=11, color='#333333')
        doc_box = patches.Rectangle((0.05, 0.75 - (i * 0.2)), 0.9, 0.1, 
                                  linewidth=1, edgecolor='#28A745', facecolor='#F8F9FA')
        ax2.add_patch(doc_box)
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_title('Supporting Documents', fontweight='bold')
    ax2.axis('off')
    
    # Analysis results
    results = [
        ('Fraud Risk', '15%', '#28A745'),
        ('Coverage', 'COVERED', '#28A745'),
        ('Settlement', '$4,750', '#2E86AB'),
        ('Processing', '2-3 days', '#6C757D')
    ]
    
    for i, (label, value, color) in enumerate(results):
        y_pos = 0.8 - (i * 0.2)
        ax3.text(0.1, y_pos, label, fontsize=11, fontweight='bold', color='#333333')
        ax3.text(0.1, y_pos - 0.08, value, fontsize=14, fontweight='bold', color=color)
    
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.set_title('Analysis Results', fontweight='bold')
    ax3.axis('off')
    
    # Fraud detection indicators
    indicators = [
        '✅ Incident timing normal',
        '✅ Claimant history clean',
        '✅ Amount within limits',
        '✅ Documentation authentic',
        '⚠️ Minor inconsistencies noted'
    ]
    
    for i, indicator in enumerate(indicators):
        color = '#28A745' if '✅' in indicator else '#FFC107'
        ax4.text(0.1, 0.9 - (i * 0.15), indicator, fontsize=10, color=color)
    
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.set_title('Fraud Detection Analysis', fontweight='bold')
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, 'claims_interface.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_actuarial_interface(images_dir):
    """Create actuarial analysis interface mockup."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Actuarial Analysis Interface', fontsize=20, fontweight='bold')
    
    # Analysis type selection
    analysis_types = [
        '• Risk Model Development',
        '• Premium Pricing Analysis',
        '• Claims Trend Analysis ✓',
        '• Loss Ratio Analysis',
        '• Market Segmentation',
        '• Predictive Modeling'
    ]
    
    for i, analysis_type in enumerate(analysis_types):
        color = '#2E86AB' if '✓' in analysis_type else '#333333'
        weight = 'bold' if '✓' in analysis_type else 'normal'
        ax1.text(0.1, 0.9 - (i * 0.12), analysis_type, fontsize=11, 
                color=color, fontweight=weight)
    
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_title('Analysis Type Selection', fontweight='bold')
    ax1.axis('off')
    
    # Data input options
    data_options = [
        '📊 Data Source: Sample Data',
        '📈 Confidence Level: 95%',
        '⏰ Time Horizon: 1 Year',
        '🎯 Risk Tolerance: Moderate',
        '🤖 Model Type: Random Forest'
    ]
    
    for i, option in enumerate(data_options):
        ax2.text(0.1, 0.9 - (i * 0.15), option, fontsize=11, color='#333333')
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_title('Analysis Parameters', fontweight='bold')
    ax2.axis('off')
    
    # Key metrics
    metrics = [
        ('Loss Ratio', '68.5%', '#28A745'),
        ('Combined Ratio', '95.2%', '#28A745'),
        ('Expected Claims', '1,247', '#FFC107'),
        ('Risk Score', '72/100', '#FD7E14')
    ]
    
    for i, (label, value, color) in enumerate(metrics):
        x_pos = 0.1 + (i % 2) * 0.45
        y_pos = 0.7 if i < 2 else 0.3
        
        metric_box = patches.Rectangle((x_pos, y_pos), 0.35, 0.25, 
                                     linewidth=2, edgecolor=color, facecolor='white')
        ax3.add_patch(metric_box)
        ax3.text(x_pos + 0.175, y_pos + 0.15, value, ha='center', va='center', 
                fontsize=14, fontweight='bold', color=color)
        ax3.text(x_pos + 0.175, y_pos + 0.05, label, ha='center', va='center', 
                fontsize=10, color='#333333')
    
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.set_title('Key Metrics', fontweight='bold')
    ax3.axis('off')
    
    # Trend visualization
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    claims = [120, 135, 128, 142, 155, 148]
    
    ax4.plot(months, claims, marker='o', linewidth=2, markersize=6, color='#2E86AB')
    ax4.fill_between(months, claims, alpha=0.3, color='#2E86AB')
    ax4.set_title('Claims Trend Analysis', fontweight='bold')
    ax4.set_ylabel('Claims Count')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, 'actuarial_interface.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_system_settings(images_dir):
    """Create system settings interface mockup."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('System Settings Interface', fontsize=20, fontweight='bold')
    
    # AI Configuration
    ai_settings = [
        'AI Provider: OpenAI ▼',
        'Model: GPT-4 ▼',
        'Temperature: 0.7 ━━━━━━━○━━',
        'Max Tokens: 2000',
        '☑ Enable Caching',
        '☑ Enable Fallback'
    ]
    
    for i, setting in enumerate(ai_settings):
        ax1.text(0.1, 0.9 - (i * 0.12), setting, fontsize=11, color='#333333')
    
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_title('🤖 AI Configuration', fontweight='bold')
    ax1.axis('off')
    
    # Performance Settings
    perf_settings = [
        'Request Timeout: 30s',
        'Max Retries: 3',
        'Connection Pool: 10',
        'Rate Limit: 100/min',
        '☑ Enable Compression',
        '☑ Enable Monitoring'
    ]
    
    for i, setting in enumerate(perf_settings):
        ax2.text(0.1, 0.9 - (i * 0.12), setting, fontsize=11, color='#333333')
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_title('⚡ Performance Settings', fontweight='bold')
    ax2.axis('off')
    
    # Security Settings
    security_settings = [
        'Log Level: INFO ▼',
        '☑ Enable Audit Logging',
        'Session Timeout: 60 min',
        '☐ Require 2FA',
        '☑ Data Encryption',
        '☑ Secure Headers'
    ]
    
    for i, setting in enumerate(security_settings):
        ax3.text(0.1, 0.9 - (i * 0.12), setting, fontsize=11, color='#333333')
    
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.set_title('🔒 Security Settings', fontweight='bold')
    ax3.axis('off')
    
    # System Status
    status_items = [
        ('System Health', 'Healthy', '#28A745'),
        ('AI Provider', 'Online', '#28A745'),
        ('Active Sessions', '23', '#2E86AB'),
        ('Response Time', '1.2s', '#28A745'),
        ('Success Rate', '99.7%', '#28A745'),
        ('API Calls Today', '1,247', '#6C757D')
    ]
    
    for i, (label, value, color) in enumerate(status_items):
        y_pos = 0.9 - (i * 0.12)
        ax4.text(0.1, y_pos, f'{label}:', fontsize=10, color='#333333')
        ax4.text(0.6, y_pos, value, fontsize=10, fontweight='bold', color=color)
    
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.set_title('📊 System Status', fontweight='bold')
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, 'system_settings.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_analytics_reports(images_dir):
    """Create analytics and reports interface mockup."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Analytics & Reports Interface', fontsize=20, fontweight='bold')
    
    # Report types
    report_types = [
        '📊 Executive Dashboard ✓',
        '⚖️ Underwriting Performance',
        '🔍 Claims Analysis Report',
        '💰 Financial Performance',
        '🛡️ Risk Management Report',
        '📋 Regulatory Compliance'
    ]
    
    for i, report_type in enumerate(report_types):
        color = '#2E86AB' if '✓' in report_type else '#333333'
        weight = 'bold' if '✓' in report_type else 'normal'
        ax1.text(0.1, 0.9 - (i * 0.12), report_type, fontsize=11, 
                color=color, fontweight=weight)
    
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_title('Report Types', fontweight='bold')
    ax1.axis('off')
    
    # Executive KPIs
    kpis = [
        ('Total Premium', '$12.4M', '+8.2%', '#28A745'),
        ('Claims Ratio', '67.3%', '-2.1%', '#28A745'),
        ('New Policies', '2,847', '+12.5%', '#28A745'),
        ('Customer Sat.', '4.6/5', '+0.2', '#28A745')
    ]
    
    for i, (label, value, change, color) in enumerate(kpis):
        x_pos = 0.1 + (i % 2) * 0.45
        y_pos = 0.7 if i < 2 else 0.3
        
        kpi_box = patches.Rectangle((x_pos, y_pos), 0.35, 0.25, 
                                  linewidth=2, edgecolor='#E0E0E0', facecolor='white')
        ax2.add_patch(kpi_box)
        ax2.text(x_pos + 0.175, y_pos + 0.18, value, ha='center', va='center', 
                fontsize=12, fontweight='bold', color='#333333')
        ax2.text(x_pos + 0.175, y_pos + 0.12, label, ha='center', va='center', 
                fontsize=9, color='#6C757D')
        ax2.text(x_pos + 0.175, y_pos + 0.05, change, ha='center', va='center', 
                fontsize=9, color=color)
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_title('Executive KPIs', fontweight='bold')
    ax2.axis('off')
    
    # Revenue trend
    dates = pd.date_range(start='2025-01-01', end='2025-06-01', freq='M')
    revenue = [10.2, 10.8, 11.5, 11.9, 12.1, 12.4]
    
    ax3.plot(dates, revenue, marker='o', linewidth=3, markersize=8, color='#2E86AB')
    ax3.fill_between(dates, revenue, alpha=0.3, color='#2E86AB')
    ax3.set_title('Revenue Trend (Millions $)', fontweight='bold')
    ax3.set_ylabel('Revenue ($M)')
    ax3.grid(True, alpha=0.3)
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
    
    # Download options
    download_options = [
        '📥 Download CSV Report',
        '📄 Download PDF Report',
        '📊 Download Excel Report',
        '📋 Download PowerPoint',
        '📧 Email Report',
        '🔗 Share Link'
    ]
    
    for i, option in enumerate(download_options):
        ax4.text(0.1, 0.9 - (i * 0.12), option, fontsize=11, color='#2E86AB')
        download_box = patches.Rectangle((0.05, 0.85 - (i * 0.12)), 0.9, 0.08, 
                                       linewidth=1, edgecolor='#2E86AB', facecolor='#F8F9FA')
        ax4.add_patch(download_box)
    
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.set_title('Export Options', fontweight='bold')
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, 'analytics_reports.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_ai_configuration_images(images_dir):
    """Create AI configuration setup images."""
    # OpenAI Setup
    fig, ax = plt.subplots(figsize=(12, 8))
    
    setup_steps = [
        '1. Visit OpenAI Platform (platform.openai.com)',
        '2. Create account or sign in',
        '3. Navigate to API Keys section',
        '4. Generate new API key',
        '5. Copy API key securely',
        '6. Set environment variables:'
    ]
    
    for i, step in enumerate(setup_steps):
        ax.text(0.1, 0.9 - (i * 0.12), step, fontsize=12, color='#333333')
    
    # Code block
    code_box = patches.Rectangle((0.1, 0.15), 0.8, 0.2, 
                               linewidth=1, edgecolor='#E0E0E0', facecolor='#F8F9FA')
    ax.add_patch(code_box)
    
    code_text = """export AI_PROVIDER=openai
export OPENAI_API_KEY=your_api_key_here
export AI_MODEL=gpt-4"""
    
    ax.text(0.12, 0.25, code_text, fontsize=10, fontfamily='monospace', 
            color='#333333', verticalalignment='center')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('OpenAI Configuration Setup', fontsize=16, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, 'openai_setup.png'), dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Generate all user guide images."""
    print("🎨 Generating user guide images...")
    
    # Create images directory
    images_dir = create_directory()
    
    # Generate all images
    image_functions = [
        create_dashboard_overview,
        create_sidebar_navigation,
        create_document_analysis_interface,
        create_underwriting_interface,
        create_claims_interface,
        create_actuarial_interface,
        create_system_settings,
        create_analytics_reports,
        create_ai_configuration_images
    ]
    
    for i, func in enumerate(image_functions, 1):
        print(f"📸 Generating image {i}/{len(image_functions)}: {func.__name__}")
        try:
            func(images_dir)
            print(f"✅ Generated: {func.__name__}")
        except Exception as e:
            print(f"❌ Error generating {func.__name__}: {e}")
    
    print(f"\n🎉 All images generated successfully!")
    print(f"📁 Images saved to: {images_dir}")
    
    # List generated files
    image_files = [f for f in os.listdir(images_dir) if f.endswith('.png')]
    print(f"\n📋 Generated {len(image_files)} images:")
    for file in sorted(image_files):
        print(f"   • {file}")

if __name__ == "__main__":
    main()