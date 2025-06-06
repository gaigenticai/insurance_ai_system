-- PostgreSQL Schema for Insurance AI System
-- Designed for Railway.com deployment
-- Production-grade implementation

-- Enable UUID extension for unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE SCHEMA IF NOT EXISTS insurance_ai;

-- Set search path to use the schema
SET search_path TO insurance_ai, public;
-- Create schema for insurance AI system
-- Institutions table - stores institution configurations
CREATE TABLE insurance_ai.institutions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    settings JSONB NOT NULL DEFAULT '{}'::jsonb,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Applications table - stores insurance application data
CREATE TABLE insurance_ai.applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id VARCHAR(50) NOT NULL UNIQUE,
    institution_id UUID NOT NULL REFERENCES insurance_ai.institutions(id) ON DELETE CASCADE,
    applicant_full_name VARCHAR(255) NOT NULL,
    applicant_address TEXT,
    applicant_date_of_birth DATE,
    application_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_status CHECK (status IN ('pending', 'approved', 'rejected', 'under_review', 'incomplete'))
);

-- Create index on application status for faster queries
CREATE INDEX idx_applications_status ON insurance_ai.applications(status);
CREATE INDEX idx_applications_institution ON insurance_ai.applications(institution_id);

-- Agent configurations table - stores configuration for different agent types
CREATE TABLE insurance_ai.agent_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES insurance_ai.institutions(id) ON DELETE CASCADE,
    agent_type VARCHAR(100) NOT NULL,
    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (institution_id, agent_type)
);

-- Agent state table - stores the current state of agents
CREATE TABLE insurance_ai.agent_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_configuration_id UUID NOT NULL REFERENCES insurance_ai.agent_configurations(id) ON DELETE CASCADE,
    application_id UUID REFERENCES insurance_ai.applications(id) ON DELETE SET NULL,
    state_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on agent states for faster lookups
CREATE INDEX idx_agent_states_application ON insurance_ai.agent_states(application_id);

-- Module configurations table - stores configuration for different modules
CREATE TABLE insurance_ai.module_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES insurance_ai.institutions(id) ON DELETE CASCADE,
    module_type VARCHAR(100) NOT NULL,
    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (institution_id, module_type)
);

-- Underwriting decisions table - stores underwriting flow results
CREATE TABLE insurance_ai.underwriting_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES insurance_ai.applications(id) ON DELETE CASCADE,
    decision VARCHAR(50) NOT NULL,
    decision_factors JSONB NOT NULL DEFAULT '{}'::jsonb,
    risk_score DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    CONSTRAINT valid_decision CHECK (decision IN ('approved', 'rejected', 'referred', 'pending_information'))
);

-- Claims table - stores claim information
CREATE TABLE insurance_ai.claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id VARCHAR(50) NOT NULL UNIQUE,
    institution_id UUID NOT NULL REFERENCES insurance_ai.institutions(id) ON DELETE CASCADE,
    application_id UUID REFERENCES insurance_ai.applications(id) ON DELETE SET NULL,
    claimant_name VARCHAR(255) NOT NULL,
    claim_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(50) NOT NULL DEFAULT 'filed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_claim_status CHECK (status IN ('filed', 'under_review', 'approved', 'rejected', 'appealed', 'closed'))
);

-- Create index on claim status for faster queries
CREATE INDEX idx_claims_status ON insurance_ai.claims(status);
CREATE INDEX idx_claims_institution ON insurance_ai.claims(institution_id);

-- Claim decisions table - stores claim processing results
CREATE TABLE insurance_ai.claim_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID NOT NULL REFERENCES insurance_ai.claims(id) ON DELETE CASCADE,
    decision VARCHAR(50) NOT NULL,
    decision_factors JSONB NOT NULL DEFAULT '{}'::jsonb,
    payout_amount DECIMAL(12,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    CONSTRAINT valid_claim_decision CHECK (decision IN ('approved', 'partially_approved', 'rejected', 'pending_information', 'fraud_suspected'))
);

-- Actuarial data table - stores actuarial calculations and models
CREATE TABLE insurance_ai.actuarial_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES insurance_ai.institutions(id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (institution_id, model_name, model_version)
);

-- Audit logs table - for tracking system activities
CREATE TABLE insurance_ai.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    actor VARCHAR(100) NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_action CHECK (action IN ('create', 'read', 'update', 'delete', 'process', 'decision'))
);

-- Create index on audit logs for faster queries
CREATE INDEX idx_audit_logs_entity ON insurance_ai.audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON insurance_ai.audit_logs(created_at);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION insurance_ai.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for all tables with updated_at column
CREATE TRIGGER update_institutions_updated_at
BEFORE UPDATE ON insurance_ai.institutions
FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();

CREATE TRIGGER update_applications_updated_at
BEFORE UPDATE ON insurance_ai.applications
FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();

CREATE TRIGGER update_agent_configurations_updated_at
BEFORE UPDATE ON insurance_ai.agent_configurations
FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();

CREATE TRIGGER update_agent_states_updated_at
BEFORE UPDATE ON insurance_ai.agent_states
FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();

CREATE TRIGGER update_module_configurations_updated_at
BEFORE UPDATE ON insurance_ai.module_configurations
FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();

CREATE TRIGGER update_underwriting_decisions_updated_at
BEFORE UPDATE ON insurance_ai.underwriting_decisions
FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();

CREATE TRIGGER update_claims_updated_at
BEFORE UPDATE ON insurance_ai.claims
FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();

CREATE TRIGGER update_claim_decisions_updated_at
BEFORE UPDATE ON insurance_ai.claim_decisions
FOR EACH ROW EXECUTE FUNCTION insurance_ai.update_updated_at_column();

-- Comments for documentation
COMMENT ON SCHEMA insurance_ai IS 'Schema for the Insurance AI System';
COMMENT ON TABLE insurance_ai.institutions IS 'Stores institution configurations and settings';
COMMENT ON TABLE insurance_ai.applications IS 'Stores insurance application data';
COMMENT ON TABLE insurance_ai.agent_configurations IS 'Stores configuration for different agent types';
COMMENT ON TABLE insurance_ai.agent_states IS 'Stores the current state of agents';
COMMENT ON TABLE insurance_ai.module_configurations IS 'Stores configuration for different modules';
COMMENT ON TABLE insurance_ai.underwriting_decisions IS 'Stores underwriting flow results';
COMMENT ON TABLE insurance_ai.claims IS 'Stores claim information';
COMMENT ON TABLE insurance_ai.claim_decisions IS 'Stores claim processing results';
COMMENT ON TABLE insurance_ai.actuarial_data IS 'Stores actuarial calculations and models';
COMMENT ON TABLE insurance_ai.audit_logs IS 'Tracks system activities for auditing purposes';


-- Add index for document_id if it exists in a table, based on ai_enhanced_schema_update_fixed.sql
-- Assuming a 'documents' table exists or will be created with a 'document_id' column
-- CREATE INDEX idx_document_analysis_document ON insurance_ai.document_analysis(document_id);




-- Sessions table - for tracking user sessions
CREATE TABLE insurance_ai.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    session_data JSONB NOT NULL DEFAULT \'{}\'::jsonb
);

CREATE INDEX idx_sessions_session_id ON insurance_ai.sessions(session_id);
CREATE INDEX idx_sessions_user_id ON insurance_ai.sessions(user_id);




CREATE INDEX idx_sessions_user_id ON insurance_ai.sessions(user_id);




-- Documents table - stores information about uploaded documents
CREATE TABLE insurance_ai.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES insurance_ai.institutions(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size INT,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    document_content TEXT, -- Storing text content extracted from documents
    metadata JSONB NOT NULL DEFAULT \'{}\':jsonb
);

CREATE INDEX idx_documents_institution ON insurance_ai.documents(institution_id);

-- Document analysis table - stores results of AI analysis on documents
CREATE TABLE insurance_ai.document_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES insurance_ai.documents(id) ON DELETE CASCADE,
    analysis_type VARCHAR(100) NOT NULL,
    analysis_result JSONB NOT NULL DEFAULT \'{}\':jsonb,
    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    analyzed_by VARCHAR(100)
);

CREATE INDEX idx_document_analysis_document ON insurance_ai.document_analysis(document_id);




-- Users table - for managing user accounts and roles
CREATE TABLE insurance_ai.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'customer',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT valid_role CHECK (role IN ('admin', 'underwriter', 'claims_adjuster', 'actuary', 'customer', 'reviewer', 'compliance'))
);

CREATE INDEX idx_users_email ON insurance_ai.users(email);
CREATE INDEX idx_users_role ON insurance_ai.users(role);


