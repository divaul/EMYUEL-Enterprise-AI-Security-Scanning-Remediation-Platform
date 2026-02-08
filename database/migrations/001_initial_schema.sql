-- EMYUEL Database Schema - Initial Migration
-- Version: 001
-- Description: Core tables for users, scans, vulnerabilities

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    email_verified BOOLEAN DEFAULT false,
    email_verified_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Organizations table (for multi-tenancy)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    settings JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_organizations_slug ON organizations(slug);

-- Organization members
CREATE TABLE organization_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, user_id)
);

CREATE INDEX idx_org_members_org_id ON organization_members(organization_id);
CREATE INDEX idx_org_members_user_id ON organization_members(user_id);

-- Projects/Repositories
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    repository_url VARCHAR(500),
    repository_type VARCHAR(50), -- git, github, gitlab, bitbucket
    default_branch VARCHAR(100) DEFAULT 'main',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    settings JSONB DEFAULT '{}'::jsonb,
    UNIQUE(organization_id, slug)
);

CREATE INDEX idx_projects_org_id ON projects(organization_id);
CREATE INDEX idx_projects_created_by ON projects(created_by);

-- Scans
CREATE TABLE scans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    scan_type VARCHAR(50) NOT NULL, -- quick, standard, comprehensive
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, running, completed,  failed, cancelled
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Scan configuration
    config JSONB DEFAULT '{}'::jsonb,
    
    -- Results summary
    total_files_scanned INTEGER DEFAULT 0,
    total_lines_scanned INTEGER DEFAULT 0,
    total_vulnerabilities_found INTEGER DEFAULT 0,
    critical_count INTEGER DEFAULT 0,
    high_count INTEGER DEFAULT 0,
    medium_count INTEGER DEFAULT 0,
    low_count INTEGER DEFAULT 0,
    
    -- LLM usage
    llm_provider_used VARCHAR(50),
    llm_tokens_used INTEGER DEFAULT 0,
    llm_cost_usd DECIMAL(10, 4) DEFAULT 0,
    
    -- Error tracking
    error_message TEXT,
    error_trace TEXT
);

CREATE INDEX idx_scans_project_id ON scans(project_id);
CREATE INDEX idx_scans_status ON scans(status);
CREATE INDEX idx_scans_created_by ON scans(created_by);
CREATE INDEX idx_scans_created_at ON scans(created_at);

-- Vulnerabilities
CREATE TABLE vulnerabilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_id UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    
    -- Vulnerability details
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    vulnerability_type VARCHAR(100) NOT NULL, -- sqli, xss, ssrf, rce, etc.
    severity VARCHAR(20) NOT NULL, -- critical, high, medium, low
    
    -- CVSS scoring
    cvss_score DECIMAL(3, 1),
    cvss_vector VARCHAR(255),
    
    -- Location
    file_path VARCHAR(1000) NOT NULL,
    line_start INTEGER NOT NULL,
    line_end INTEGER NOT NULL,
    code_snippet TEXT,
    
    -- Analysis details
    attack_vector TEXT,
    proof_of_concept TEXT,
    data_flow_path JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'open', -- open, in_progress, fixed, false_positive, accepted_risk
    assigned_to UUID REFERENCES users(id),
    
    -- Remediation
    has_remediation BOOLEAN DEFAULT false,
    remediation_suggestion TEXT,
    remediation_code TEXT,
    remediation_confidence DECIMAL(3, 2),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fixed_at TIMESTAMP WITH TIME ZONE,
    
    -- Provider info
    detected_by_provider VARCHAR(50),
    confidence_score DECIMAL(3, 2)
);

CREATE INDEX idx_vulnerabilities_scan_id ON vulnerabilities(scan_id);
CREATE INDEX idx_vulnerabilities_severity ON vulnerabilities(severity);
CREATE INDEX idx_vulnerabilities_status ON vulnerabilities(status);
CREATE INDEX idx_vulnerabilities_type ON vulnerabilities(vulnerability_type);
CREATE INDEX idx_vulnerabilities_cvss_score ON vulnerabilities(cvss_score);

-- Scan artifacts (reports, logs, etc.)
CREATE TABLE scan_artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_id UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    artifact_type VARCHAR(50) NOT NULL, -- report_pdf, report_html, log_file, etc.
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_artifacts_scan_id ON scan_artifacts(scan_id);
CREATE INDEX idx_artifacts_type ON scan_artifacts(artifact_type);

-- Comments on vulnerabilities
CREATE TABLE vulnerability_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vulnerability_id UUID NOT NULL REFERENCES vulnerabilities(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    comment TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vuln_comments_vuln_id ON vulnerability_comments(vulnerability_id);
CREATE INDEX idx_vuln_comments_user_id ON vulnerability_comments(user_id);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scans_updated_at BEFORE UPDATE ON scans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vulnerabilities_updated_at BEFORE UPDATE ON vulnerabilities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123 - CHANGE IN PRODUCTION!)
INSERT INTO users (email, username, password_hash, full_name, is_superuser, email_verified)
VALUES (
    'admin@emyuel.local',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzN9RgN4Ni', -- hashed 'admin123'
    'System Administrator',
    true,
    true
);
