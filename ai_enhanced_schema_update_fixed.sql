-- =====================================================
-- AI-Enhanced Insurance System Schema Update (FIXED)
-- =====================================================
-- This script updates the existing insurance_ai schema to support
-- the new AI features including multi-provider AI, document analysis,
-- professional UI, and comprehensive audit trails.
-- 
-- COMPATIBILITY: 100% backward compatible with existing schema
-- EXECUTION: Safe to run on existing databases
-- FIX: Resolved RAISE statement and conflict issues
-- =====================================================

-- Ensure we're working in the correct schema
SET search_path TO insurance_ai, public;

-- =====================================================
-- 1. AI PROVIDER MANAGEMENT
-- =====================================================

-- AI Providers table - stores AI provider configurations
CREATE TABLE IF NOT EXISTS insurance_ai.ai_providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES insurance_ai.institutions(id) ON DELETE CASCADE,
    provider_name VARCHAR(50) NOT NULL, -- 'openai', 'anthropic', 'local', etc.
    provider_type VARCHAR(50) NOT NULL, -- 'cloud', 'local', 'hybrid'
    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
    api_endpoint VARCHAR(500),
    api_key_hash VARCHAR(255), -- Hashed API key for security
    model_name VARCHAR(100),
    max_tokens INTEGER DEFAULT 4000,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    priority_order INTEGER DEFAULT 1,
    cost_per_token DECIMAL(10,8) DEFAULT 0.0,
    rate_limit_per_minute INTEGER DEFAULT 60,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_health_check TIMESTAMP WITH TIME ZONE,
    health_status VARCHAR(20) DEFAULT 'unknown',
    UNIQUE (institution_id, provider_name),
    CONSTRAINT valid_provider_type CHECK (provider_type IN ('cloud', 'local', 'hybrid')),
    CONSTRAINT valid_health_status CHECK (health_status IN ('healthy', 'degraded', 'unhealthy', 'unknown'))
);

-- AI Models table - stores AI model configurations and versions
CREATE TABLE IF NOT EXISTS insurance_ai.ai_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id UUID NOT NULL REFERENCES insurance_ai.ai_providers(id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'text', 'vision', 'embedding', etc.
    capabilities JSONB NOT NULL DEFAULT '[]'::jsonb, -- ['text_analysis', 'document_processing', etc.]
    context_window INTEGER DEFAULT 4000,
    max_output_tokens INTEGER DEFAULT 1000,
    supports_streaming BOOLEAN DEFAULT FALSE,
    supports_function_calling BOOLEAN DEFAULT FALSE,
    cost_per_input_token DECIMAL(10,8) DEFAULT 0.0,
    cost_per_output_token DECIMAL(10,8) DEFAULT 0.0,
    performance_metrics JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (provider_id, model_name, model_version),
    CONSTRAINT valid_model_type CHECK (model_type IN ('text', 'vision', 'embedding', 'multimodal'))
);

-- =====================================================
-- 2. DOCUMENT MANAGEMENT & ANALYSIS
-- =====================================================

-- Documents table - stores document metadata and content
CREATE TABLE IF NOT EXISTS insurance_ai.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES insurance_ai.institutions(id) ON DELETE CASCADE,
    application_id UUID REFERENCES insurance_ai.applications(id) ON DELETE SET NULL,
    claim_id UUID REFERENCES insurance_ai.claims(id) ON DELETE SET NULL,
    document_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL, -- 'policy', 'claim', 'medical', 'financial', etc.
    file_type VARCHAR(10) NOT NULL, -- 'pdf', 'docx', 'txt', 'jpg', 'png'
    file_size_bytes BIGINT,
    file_hash VARCHAR(64), -- SHA-256 hash for deduplication
    storage_path VARCHAR(500),
    content_text TEXT, -- Extracted text content
    metadata JSONB DEFAULT '{}'::jsonb,
    upload_source VARCHAR(50) DEFAULT 'manual', -- 'manual', 'api', 'email', 'scan'
    uploaded_by VARCHAR(100),
    is_processed BOOLEAN DEFAULT FALSE,
    is_sensitive BOOLEAN DEFAULT FALSE,
    retention_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_document_type CHECK (document_type IN ('policy', 'claim', 'medical', 'financial', 'identity', 'application', 'other')),
    CONSTRAINT valid_file_type CHECK (file_type IN ('pdf', 'docx', 'txt', 'jpg', 'png', 'tiff', 'doc')),
    CONSTRAINT valid_upload_source CHECK (upload_source IN ('manual', 'api', 'email', 'scan', 'ui'))
);

-- Document Analysis table - stores AI document analysis results
CREATE TABLE IF NOT EXISTS insurance_ai.document_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES insurance_ai.documents(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL, -- 'policy_review', 'claim_validation', 'risk_assessment', etc.
    ai_provider_id UUID REFERENCES insurance_ai.ai_providers(id) ON DELETE SET NULL,
    ai_model_id UUID REFERENCES insurance_ai.ai_models(id) ON DELETE SET NULL,
    analysis_prompt TEXT,
    analysis_result JSONB NOT NULL DEFAULT '{}'::jsonb,
    confidence_score DECIMAL(5,4), -- 0.0000 to 1.0000
    processing_time_ms INTEGER,
    token_usage JSONB DEFAULT '{}'::jsonb, -- {'input_tokens': 100, 'output_tokens': 50}
    cost_usd DECIMAL(10,6) DEFAULT 0.0,
    risk_indicators JSONB DEFAULT '[]'::jsonb,
    extracted_entities JSONB DEFAULT '{}'::jsonb,
    compliance_flags JSONB DEFAULT '[]'::jsonb,
    quality_score DECIMAL(5,4),
    is_reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by VARCHAR(100),
    review_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_analysis_type CHECK (analysis_type IN ('policy_review', 'claim_validation', 'risk_assessment', 'fraud_detection', 'compliance_check', 'general_analysis'))
);

-- =====================================================
-- 3. AI ANALYSIS SESSIONS & RESPONSES
-- =====================================================

-- AI Analysis Sessions table - tracks AI analysis sessions
CREATE TABLE IF NOT EXISTS insurance_ai.ai_analysis_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES insurance_ai.institutions(id) ON DELETE CASCADE,
    session_type VARCHAR(50) NOT NULL, -- 'underwriting', 'claims', 'actuarial', 'document'
    user_id VARCHAR(100),
    application_id UUID REFERENCES insurance_ai.applications(id) ON DELETE SET NULL,
    claim_id UUID REFERENCES insurance_ai.claims(id) ON DELETE SET NULL,
    document_ids UUID[], -- Array of document IDs
    ai_provider_id UUID REFERENCES insurance_ai.ai_providers(id) ON DELETE SET NULL,
    session_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    analysis_results JSONB DEFAULT '{}'::jsonb,
    total_cost_usd DECIMAL(10,6) DEFAULT 0.0,
    total_tokens_used INTEGER DEFAULT 0,
    processing_time_ms INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT valid_session_type CHECK (session_type IN ('underwriting', 'claims', 'actuarial', 'document', 'general')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled'))
);

-- AI Responses Cache table - caches AI responses for performance
CREATE TABLE IF NOT EXISTS insurance_ai.ai_responses_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key VARCHAR(64) NOT NULL UNIQUE, -- SHA-256 hash of prompt + model + params
    ai_provider_id UUID REFERENCES insurance_ai.ai_providers(id) ON DELETE CASCADE,
    ai_model_id UUID REFERENCES insurance_ai.ai_models(id) ON DELETE CASCADE,
    prompt_hash VARCHAR(64) NOT NULL,
    response_data JSONB NOT NULL,
    token_usage JSONB DEFAULT '{}'::jsonb,
    cost_usd DECIMAL(10,6) DEFAULT 0.0,
    hit_count INTEGER DEFAULT 1,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 4. AI PROMPT TEMPLATES & CONFIGURATION
-- =====================================================

-- AI Prompt Templates table - stores and versions prompt templates
CREATE TABLE IF NOT EXISTS insurance_ai.ai_prompt_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES insurance_ai.institutions(id) ON DELETE CASCADE,
    template_name VARCHAR(100) NOT NULL,
    template_version VARCHAR(20) NOT NULL DEFAULT '1.0',
    template_type VARCHAR(50) NOT NULL, -- 'underwriting', 'claims', 'actuarial', 'document'
    template_content TEXT NOT NULL,
    template_variables JSONB DEFAULT '[]'::jsonb, -- ['applicant_name', 'risk_factors', etc.]
    model_requirements JSONB DEFAULT '{}'::jsonb, -- {'min_context_window': 4000, 'supports_functions': true}
    performance_metrics JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (institution_id, template_name, template_version),
    CONSTRAINT valid_template_type CHECK (template_type IN ('underwriting', 'claims', 'actuarial', 'document', 'general'))
);

-- =====================================================
-- 5. AI METRICS & MONITORING
-- =====================================================

-- AI Metrics table - tracks AI performance and usage
CREATE TABLE IF NOT EXISTS insurance_ai.ai_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES insurance_ai.institutions(id) ON DELETE CASCADE,
    ai_provider_id UUID REFERENCES insurance_ai.ai_providers(id) ON DELETE SET NULL,
    ai_model_id UUID REFERENCES insurance_ai.ai_models(id) ON DELETE SET NULL,
    metric_type VARCHAR(50) NOT NULL, -- 'usage', 'performance', 'cost', 'accuracy'
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6) NOT NULL,
    metric_unit VARCHAR(20), -- 'tokens', 'requests', 'seconds', 'usd', 'percentage'
    aggregation_period VARCHAR(20) NOT NULL, -- 'hour', 'day', 'week', 'month'
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_metric_type CHECK (metric_type IN ('usage', 'performance', 'cost', 'accuracy', 'latency', 'error_rate')),
    CONSTRAINT valid_aggregation_period CHECK (aggregation_period IN ('hour', 'day', 'week', 'month', 'quarter', 'year'))
);

-- =====================================================
-- 6. USER SESSIONS & UI PREFERENCES
-- =====================================================

-- User Sessions table - tracks user sessions for the professional UI
CREATE TABLE IF NOT EXISTS insurance_ai.user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES insurance_ai.institutions(id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    user_role VARCHAR(50) DEFAULT 'user',
    login_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP WITH TIME ZONE,
    ip_address INET,
    user_agent TEXT,
    session_data JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT valid_user_role CHECK (user_role IN ('admin', 'underwriter', 'claims_adjuster', 'actuary', 'user', 'viewer'))
);

-- System Settings table - stores system-wide configuration
CREATE TABLE IF NOT EXISTS insurance_ai.system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES insurance_ai.institutions(id) ON DELETE CASCADE,
    setting_category VARCHAR(50) NOT NULL, -- 'ai', 'ui', 'security', 'notifications'
    setting_key VARCHAR(100) NOT NULL,
    setting_value JSONB NOT NULL,
    setting_type VARCHAR(20) NOT NULL, -- 'string', 'number', 'boolean', 'object', 'array'
    is_encrypted BOOLEAN DEFAULT FALSE,
    is_user_configurable BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    UNIQUE (institution_id, setting_category, setting_key),
    CONSTRAINT valid_setting_category CHECK (setting_category IN ('ai', 'ui', 'security', 'notifications', 'integrations', 'compliance')),
    CONSTRAINT valid_setting_type CHECK (setting_type IN ('string', 'number', 'boolean', 'object', 'array'))
);

-- =====================================================
-- 7. ENHANCED AUDIT TRAIL
-- =====================================================

-- AI Audit Trail table - detailed AI decision audit trail
CREATE TABLE IF NOT EXISTS insurance_ai.ai_audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES insurance_ai.institutions(id) ON DELETE CASCADE,
    session_id UUID REFERENCES insurance_ai.ai_analysis_sessions(id) ON DELETE SET NULL,
    ai_provider_id UUID REFERENCES insurance_ai.ai_providers(id) ON DELETE SET NULL,
    ai_model_id UUID REFERENCES insurance_ai.ai_models(id) ON DELETE SET NULL,
    operation_type VARCHAR(50) NOT NULL, -- 'analysis', 'decision', 'recommendation'
    entity_type VARCHAR(50) NOT NULL, -- 'application', 'claim', 'document'
    entity_id UUID NOT NULL,
    user_id VARCHAR(100),
    prompt_template_id UUID REFERENCES insurance_ai.ai_prompt_templates(id) ON DELETE SET NULL,
    input_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    output_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    decision_factors JSONB DEFAULT '{}'::jsonb,
    confidence_scores JSONB DEFAULT '{}'::jsonb,
    bias_indicators JSONB DEFAULT '{}'::jsonb,
    explainability_data JSONB DEFAULT '{}'::jsonb,
    human_override BOOLEAN DEFAULT FALSE,
    override_reason TEXT,
    compliance_flags JSONB DEFAULT '[]'::jsonb,
    processing_time_ms INTEGER,
    token_usage JSONB DEFAULT '{}'::jsonb,
    cost_usd DECIMAL(10,6) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_operation_type CHECK (operation_type IN ('analysis', 'decision', 'recommendation', 'classification', 'extraction')),
    CONSTRAINT valid_entity_type CHECK (entity_type IN ('application', 'claim', 'document', 'policy', 'customer'))
);

-- =====================================================
-- 8. ENHANCED EXISTING TABLES
-- =====================================================

-- Add AI-related columns to existing underwriting_decisions table
DO $$ 
BEGIN
    -- Add AI provider tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'insurance_ai' AND table_name = 'underwriting_decisions' AND column_name = 'ai_provider_id') THEN
        ALTER TABLE insurance_ai.underwriting_decisions ADD COLUMN ai_provider_id UUID REFERENCES insurance_ai.ai_providers(id) ON DELETE SET NULL;
    END IF;
    
    -- Add AI model tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'insurance_ai' AND table_name = 'underwriting_decisions' AND column_name = 'ai_model_id') THEN
        ALTER TABLE insurance_ai.underwriting_decisions ADD COLUMN ai_model_id UUID REFERENCES insurance_ai.ai_models(id) ON DELETE SET NULL;
    END IF;
    
    -- Add AI confidence score
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'insurance_ai' AND table_name = 'underwriting_decisions' AND column_name = 'ai_confidence_score') THEN
        ALTER TABLE insurance_ai.underwriting_decisions ADD COLUMN ai_confidence_score DECIMAL(5,4);
    END IF;
    
    -- Add processing time
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'insurance_ai' AND table_name = 'underwriting_decisions' AND column_name = 'processing_time_ms') THEN
        ALTER TABLE insurance_ai.underwriting_decisions ADD COLUMN processing_time_ms INTEGER;
    END IF;
    
    -- Add token usage
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'insurance_ai' AND table_name = 'underwriting_decisions' AND column_name = 'token_usage') THEN
        ALTER TABLE insurance_ai.underwriting_decisions ADD COLUMN token_usage JSONB DEFAULT '{}'::jsonb;
    END IF;
    
    -- Add cost tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'insurance_ai' AND table_name = 'underwriting_decisions' AND column_name = 'ai_cost_usd') THEN
        ALTER TABLE insurance_ai.underwriting_decisions ADD COLUMN ai_cost_usd DECIMAL(10,6) DEFAULT 0.0;
    END IF;
END $$;

-- Add AI-related columns to existing claim_decisions table
DO $$ 
BEGIN
    -- Add AI provider tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'insurance_ai' AND table_name = 'claim_decisions' AND column_name = 'ai_provider_id') THEN
        ALTER TABLE insurance_ai.claim_decisions ADD COLUMN ai_provider_id UUID REFERENCES insurance_ai.ai_providers(id) ON DELETE SET NULL;
    END IF;
    
    -- Add AI model tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'insurance_ai' AND table_name = 'claim_decisions' AND column_name = 'ai_model_id') THEN
        ALTER TABLE insurance_ai.claim_decisions ADD COLUMN ai_model_id UUID REFERENCES insurance_ai.ai_models(id) ON DELETE SET NULL;
    END IF;
    
    -- Add fraud risk score
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'insurance_ai' AND table_name = 'claim_decisions' AND column_name = 'fraud_risk_score') THEN
        ALTER TABLE insurance_ai.claim_decisions ADD COLUMN fraud_risk_score DECIMAL(5,4);
    END IF;
    
    -- Add AI confidence score
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'insurance_ai' AND table_name = 'claim_decisions' AND column_name = 'ai_confidence_score') THEN
        ALTER TABLE insurance_ai.claim_decisions ADD COLUMN ai_confidence_score DECIMAL(5,4);
    END IF;
    
    -- Add processing time
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'insurance_ai' AND table_name = 'claim_decisions' AND column_name = 'processing_time_ms') THEN
        ALTER TABLE insurance_ai.claim_decisions ADD COLUMN processing_time_ms INTEGER;
    END IF;
    
    -- Add token usage
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'insurance_ai' AND table_name = 'claim_decisions' AND column_name = 'token_usage') THEN
        ALTER TABLE insurance_ai.claim_decisions ADD COLUMN token_usage JSONB DEFAULT '{}'::jsonb;
    END IF;
    
    -- Add cost tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'insurance_ai' AND table_name = 'claim_decisions' AND column_name = 'ai_cost_usd') THEN
        ALTER TABLE insurance_ai.claim_decisions ADD COLUMN ai_cost_usd DECIMAL(10,6) DEFAULT 0.0;
    END IF;
END $$;

-- =====================================================
-- 9. INDEXES FOR PERFORMANCE
-- =====================================================

-- AI Providers indexes
CREATE INDEX IF NOT EXISTS idx_ai_providers_institution ON insurance_ai.ai_providers(institution_id);
CREATE INDEX IF NOT EXISTS idx_ai_providers_active ON insurance_ai.ai_providers(is_active);
CREATE INDEX IF NOT EXISTS idx_ai_providers_primary ON insurance_ai.ai_providers(is_primary);
CREATE INDEX IF NOT EXISTS idx_ai_providers_health ON insurance_ai.ai_providers(health_status);

-- AI Models indexes
CREATE INDEX IF NOT EXISTS idx_ai_models_provider ON insurance_ai.ai_models(provider_id);
CREATE INDEX IF NOT EXISTS idx_ai_models_active ON insurance_ai.ai_models(is_active);
CREATE INDEX IF NOT EXISTS idx_ai_models_type ON insurance_ai.ai_models(model_type);

-- Documents indexes
CREATE INDEX IF NOT EXISTS idx_documents_institution ON insurance_ai.documents(institution_id);
CREATE INDEX IF NOT EXISTS idx_documents_application ON insurance_ai.documents(application_id);
CREATE INDEX IF NOT EXISTS idx_documents_claim ON insurance_ai.documents(claim_id);
CREATE INDEX IF NOT EXISTS idx_documents_type ON insurance_ai.documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_processed ON insurance_ai.documents(is_processed);
CREATE INDEX IF NOT EXISTS idx_documents_hash ON insurance_ai.documents(file_hash);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON insurance_ai.documents(created_at);

-- Document Analysis indexes
CREATE INDEX IF NOT EXISTS idx_document_analysis_document ON insurance_ai.document_analysis(document_id);
CREATE INDEX IF NOT EXISTS idx_document_analysis_type ON insurance_ai.document_analysis(analysis_type);
CREATE INDEX IF NOT EXISTS idx_document_analysis_provider ON insurance_ai.document_analysis(ai_provider_id);
CREATE INDEX IF NOT EXISTS idx_document_analysis_confidence ON insurance_ai.document_analysis(confidence_score);
CREATE INDEX IF NOT EXISTS idx_document_analysis_created_at ON insurance_ai.document_analysis(created_at);

-- AI Analysis Sessions indexes
CREATE INDEX IF NOT EXISTS idx_ai_sessions_institution ON insurance_ai.ai_analysis_sessions(institution_id);
CREATE INDEX IF NOT EXISTS idx_ai_sessions_type ON insurance_ai.ai_analysis_sessions(session_type);
CREATE INDEX IF NOT EXISTS idx_ai_sessions_user ON insurance_ai.ai_analysis_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_sessions_status ON insurance_ai.ai_analysis_sessions(status);
CREATE INDEX IF NOT EXISTS idx_ai_sessions_created_at ON insurance_ai.ai_analysis_sessions(created_at);

-- AI Responses Cache indexes
CREATE INDEX IF NOT EXISTS idx_ai_cache_provider ON insurance_ai.ai_responses_cache(ai_provider_id);
CREATE INDEX IF NOT EXISTS idx_ai_cache_accessed ON insurance_ai.ai_responses_cache(last_accessed);
CREATE INDEX IF NOT EXISTS idx_ai_cache_expires ON insurance_ai.ai_responses_cache(expires_at);

-- AI Prompt Templates indexes
CREATE INDEX IF NOT EXISTS idx_ai_templates_institution ON insurance_ai.ai_prompt_templates(institution_id);
CREATE INDEX IF NOT EXISTS idx_ai_templates_type ON insurance_ai.ai_prompt_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_ai_templates_active ON insurance_ai.ai_prompt_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_ai_templates_default ON insurance_ai.ai_prompt_templates(is_default);

-- AI Metrics indexes
CREATE INDEX IF NOT EXISTS idx_ai_metrics_institution ON insurance_ai.ai_metrics(institution_id);
CREATE INDEX IF NOT EXISTS idx_ai_metrics_provider ON insurance_ai.ai_metrics(ai_provider_id);
CREATE INDEX IF NOT EXISTS idx_ai_metrics_type ON insurance_ai.ai_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_ai_metrics_period ON insurance_ai.ai_metrics(period_start, period_end);

-- User Sessions indexes
CREATE INDEX IF NOT EXISTS idx_user_sessions_institution ON insurance_ai.user_sessions(institution_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON insurance_ai.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON insurance_ai.user_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_sessions_activity ON insurance_ai.user_sessions(last_activity);

-- System Settings indexes
CREATE INDEX IF NOT EXISTS idx_system_settings_institution ON insurance_ai.system_settings(institution_id);
CREATE INDEX IF NOT EXISTS idx_system_settings_category ON insurance_ai.system_settings(setting_category);

-- AI Audit Trail indexes
CREATE INDEX IF NOT EXISTS idx_ai_audit_institution ON insurance_ai.ai_audit_trail(institution_id);
CREATE INDEX IF NOT EXISTS idx_ai_audit_session ON insurance_ai.ai_audit_trail(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_audit_entity ON insurance_ai.ai_audit_trail(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_ai_audit_user ON insurance_ai.ai_audit_trail(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_audit_created_at ON insurance_ai.ai_audit_trail(created_at);

-- =====================================================
-- 10. TRIGGERS FOR UPDATED_AT COLUMNS
-- =====================================================

-- Create triggers for new tables with updated_at columns
DO $$
BEGIN
    -- Only create triggers if they don't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE trigger_name = 'update_ai_providers_updated_at') THEN
        CREATE TRIGGER update_ai_providers_updated_at
        BEFORE UPDATE ON insurance_ai.ai_providers
        FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE trigger_name = 'update_ai_models_updated_at') THEN
        CREATE TRIGGER update_ai_models_updated_at
        BEFORE UPDATE ON insurance_ai.ai_models
        FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE trigger_name = 'update_documents_updated_at') THEN
        CREATE TRIGGER update_documents_updated_at
        BEFORE UPDATE ON insurance_ai.documents
        FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE trigger_name = 'update_document_analysis_updated_at') THEN
        CREATE TRIGGER update_document_analysis_updated_at
        BEFORE UPDATE ON insurance_ai.document_analysis
        FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE trigger_name = 'update_ai_analysis_sessions_updated_at') THEN
        CREATE TRIGGER update_ai_analysis_sessions_updated_at
        BEFORE UPDATE ON insurance_ai.ai_analysis_sessions
        FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE trigger_name = 'update_ai_prompt_templates_updated_at') THEN
        CREATE TRIGGER update_ai_prompt_templates_updated_at
        BEFORE UPDATE ON insurance_ai.ai_prompt_templates
        FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.triggers WHERE trigger_name = 'update_system_settings_updated_at') THEN
        CREATE TRIGGER update_system_settings_updated_at
        BEFORE UPDATE ON insurance_ai.system_settings
        FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();
    END IF;
END $$;

-- =====================================================
-- 11. VIEWS FOR COMMON QUERIES
-- =====================================================

-- AI Provider Health View
CREATE OR REPLACE VIEW insurance_ai.v_ai_provider_health AS
SELECT 
    p.id,
    p.institution_id,
    p.provider_name,
    p.provider_type,
    p.model_name,
    p.is_active,
    p.is_primary,
    p.health_status,
    p.last_health_check,
    COUNT(m.id) as model_count
FROM insurance_ai.ai_providers p
LEFT JOIN insurance_ai.ai_models m ON p.id = m.provider_id AND m.is_active = true
GROUP BY p.id, p.institution_id, p.provider_name, p.provider_type, p.model_name, 
         p.is_active, p.is_primary, p.health_status, p.last_health_check;

-- Document Analysis Summary View
CREATE OR REPLACE VIEW insurance_ai.v_document_analysis_summary AS
SELECT 
    d.id as document_id,
    d.document_name,
    d.document_type,
    d.file_type,
    d.is_processed,
    COUNT(da.id) as analysis_count,
    MAX(da.created_at) as last_analysis,
    AVG(da.confidence_score) as avg_confidence,
    SUM(da.cost_usd) as total_cost,
    ARRAY_AGG(DISTINCT da.analysis_type) as analysis_types
FROM insurance_ai.documents d
LEFT JOIN insurance_ai.document_analysis da ON d.id = da.document_id
GROUP BY d.id, d.document_name, d.document_type, d.file_type, d.is_processed;

-- AI Usage Summary View
CREATE OR REPLACE VIEW insurance_ai.v_ai_usage_summary AS
SELECT 
    institution_id,
    DATE(created_at) as usage_date,
    session_type,
    COUNT(*) as session_count,
    SUM(total_cost_usd) as total_cost,
    SUM(total_tokens_used) as total_tokens,
    AVG(processing_time_ms) as avg_processing_time,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_sessions,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_sessions
FROM insurance_ai.ai_analysis_sessions
GROUP BY institution_id, DATE(created_at), session_type;

-- =====================================================
-- 12. FUNCTIONS FOR AI OPERATIONS
-- =====================================================

-- Function to get active AI provider for institution
CREATE OR REPLACE FUNCTION insurance_ai.get_active_ai_provider(
    p_institution_id UUID,
    p_provider_type VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    provider_id UUID,
    provider_name VARCHAR,
    model_name VARCHAR,
    api_endpoint VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.provider_name,
        p.model_name,
        p.api_endpoint
    FROM insurance_ai.ai_providers p
    WHERE p.institution_id = p_institution_id
      AND p.is_active = true
      AND p.health_status = 'healthy'
      AND (p_provider_type IS NULL OR p.provider_type = p_provider_type)
    ORDER BY p.is_primary DESC, p.priority_order ASC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 13. SAMPLE DATA FOR TESTING
-- =====================================================

-- Insert sample AI provider configurations
INSERT INTO insurance_ai.ai_providers (institution_id, provider_name, provider_type, model_name, is_primary, priority_order, configuration)
SELECT 
    i.id,
    'openai',
    'cloud',
    'gpt-4',
    true,
    1,
    '{"temperature": 0.7, "max_tokens": 4000}'::jsonb
FROM insurance_ai.institutions i
WHERE NOT EXISTS (
    SELECT 1 FROM insurance_ai.ai_providers p 
    WHERE p.institution_id = i.id AND p.provider_name = 'openai'
);

-- Insert sample prompt templates
INSERT INTO insurance_ai.ai_prompt_templates (institution_id, template_name, template_type, template_content, is_default)
SELECT 
    i.id,
    'underwriting_risk_assessment',
    'underwriting',
    'Analyze the following insurance application for risk assessment:\n\nApplicant: {applicant_name}\nIncome: {income}\nCredit Score: {credit_score}\n\nProvide a risk score from 1-100 and explain your reasoning.',
    true
FROM insurance_ai.institutions i
WHERE NOT EXISTS (
    SELECT 1 FROM insurance_ai.ai_prompt_templates t 
    WHERE t.institution_id = i.id AND t.template_name = 'underwriting_risk_assessment'
);

-- =====================================================
-- 14. COMMENTS AND DOCUMENTATION
-- =====================================================

-- Add comments to new tables
COMMENT ON TABLE insurance_ai.ai_providers IS 'Stores AI provider configurations (OpenAI, Anthropic, Local LLMs)';
COMMENT ON TABLE insurance_ai.ai_models IS 'Stores AI model configurations and capabilities';
COMMENT ON TABLE insurance_ai.documents IS 'Stores document metadata and content for AI analysis';
COMMENT ON TABLE insurance_ai.document_analysis IS 'Stores AI document analysis results and metrics';
COMMENT ON TABLE insurance_ai.ai_analysis_sessions IS 'Tracks AI analysis sessions across all modules';
COMMENT ON TABLE insurance_ai.ai_responses_cache IS 'Caches AI responses for performance optimization';
COMMENT ON TABLE insurance_ai.ai_prompt_templates IS 'Stores versioned AI prompt templates';
COMMENT ON TABLE insurance_ai.ai_metrics IS 'Tracks AI usage, performance, and cost metrics';
COMMENT ON TABLE insurance_ai.user_sessions IS 'Tracks user sessions for the professional UI';
COMMENT ON TABLE insurance_ai.system_settings IS 'Stores system-wide configuration settings';
COMMENT ON TABLE insurance_ai.ai_audit_trail IS 'Comprehensive audit trail for AI decisions and operations';

-- =====================================================
-- 15. COMPLETION MESSAGE
-- =====================================================

-- Success message
SELECT 'AI-Enhanced Insurance System Schema Update COMPLETED SUCCESSFULLY!' as status,
       'New tables created: 11' as new_tables,
       'Existing tables enhanced: 2' as enhanced_tables,
       'Indexes created: 25+' as indexes,
       'Views created: 3' as views,
       'Functions created: 1' as functions,
       'Triggers created: 7' as triggers,
       'The schema is now 100% compatible with the AI-enhanced system' as compatibility,
       'All AI features are fully supported' as ai_support;