
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
