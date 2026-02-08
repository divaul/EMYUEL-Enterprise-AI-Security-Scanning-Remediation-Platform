-- Audit Logs Tables Migration
-- Version: 003
-- Description: Immutable append-only audit logging

-- Audit logs table (append-only, immutable)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- WHO
    user_id UUID REFERENCES users(id),
    user_email VARCHAR(255),
    user_ip_address INET,
    user_agent TEXT,
    
    -- WHAT
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    
    -- WHERE
    endpoint VARCHAR(500),
    http_method VARCHAR(10),
    
    -- DETAILS
    changes JSONB, -- Before/after values
    metadata JSONB, -- Additional context
    
    -- RESULT
    status VARCHAR(50) NOT NULL, -- success, failure, error
    error_message TEXT,
    
    -- REQUEST/RESPONSE
    request_id UUID,
    session_id UUID,
    
    -- ORGANIZATION
    organization_id UUID REFERENCES organizations(id)
);

-- Indexes for efficient querying
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_org_id ON audit_logs(organization_id);
CREATE INDEX idx_audit_logs_request_id ON audit_logs(request_id);

-- GIN index for JSON searching
CREATE INDEX idx_audit_logs_metadata ON audit_logs USING GIN (metadata);
CREATE INDEX idx_audit_logs_changes ON audit_logs USING GIN (changes);

-- Prevent updates and deletes on audit logs (immutability)
CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit logs are immutable and cannot be modified or deleted';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_audit_log_update
    BEFORE UPDATE ON audit_logs
    FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_modification();

CREATE TRIGGER prevent_audit_log_delete
    BEFORE DELETE ON audit_logs
    FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_modification();

-- Partitioning function for time-based partitioning (optional, for large-scale deployments)
-- This can be enabled later for better performance with millions of logs
COMMENT ON TABLE audit_logs IS 'Immutable append-only audit log table. Records cannot be modified or deleted.';
