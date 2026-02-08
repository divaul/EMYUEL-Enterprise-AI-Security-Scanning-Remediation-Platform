-- Integration Configuration Tables
-- Version: 004
-- Description: Third-party integration configurations and webhooks

-- Integration configurations
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    integration_type VARCHAR(50) NOT NULL, -- jira, slack, linear, servicenow, github, gitlab
    name VARCHAR(255) NOT NULL,
    is_enabled BOOLEAN DEFAULT true,
    
    -- Configuration (encrypted sensitive data)
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Credentials (should be encrypted at application level)
    credentials JSONB DEFAULT '{}'::jsonb,
    
    -- Status
    last_sync_at TIMESTAMP WITH TIME ZONE,
    last_error TEXT,
    sync_status VARCHAR(50) DEFAULT 'active', -- active, error, disabled
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    UNIQUE(organization_id, integration_type, name)
);

CREATE INDEX idx_integrations_org_id ON integrations(organization_id);
CREATE INDEX idx_integrations_type ON integrations(integration_type);
CREATE INDEX idx_integrations_enabled ON integrations(is_enabled);

-- Webhooks
CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(1000) NOT NULL,
    is_enabled BOOLEAN DEFAULT true,
    
    -- Events to trigger on
    events VARCHAR(100)[] NOT NULL, -- array of event types
    
    -- Configuration
    method VARCHAR(10) DEFAULT 'POST',
    headers JSONB DEFAULT '{}'::jsonb,
    secret VARCHAR(255), -- For signature verification
    
    -- Retry configuration
    retry_attempts INTEGER DEFAULT 3,
    retry_backoff_seconds INTEGER DEFAULT 60,
    
    -- Status
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    last_success_at TIMESTAMP WITH TIME ZONE,
    last_failure_at TIMESTAMP WITH TIME ZONE,
    failure_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_webhooks_org_id ON webhooks(organization_id);
CREATE INDEX idx_webhooks_enabled ON webhooks(is_enabled);
CREATE INDEX idx_webhooks_events ON webhooks USING GIN(events);

-- Webhook delivery logs
CREATE TABLE webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    webhook_id UUID NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    
    -- Request
    request_url VARCHAR(1000) NOT NULL,
    request_method VARCHAR(10) NOT NULL,
    request_headers JSONB,
    request_payload JSONB,
    
    -- Response
    response_status_code INTEGER,
    response_headers JSONB,
    response_body TEXT,
    
    -- Timing
    delivered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    duration_ms INTEGER,
    
    -- Status
    success BOOLEAN NOT NULL,
    error_message TEXT,
    attempt_number INTEGER DEFAULT 1
);

CREATE INDEX idx_webhook_deliveries_webhook_id ON webhook_deliveries(webhook_id);
CREATE INDEX idx_webhook_deliveries_delivered_at ON webhook_deliveries(delivered_at DESC);
CREATE INDEX idx_webhook_deliveries_success ON webhook_deliveries(success);

-- Action triggers (automated actions on events)
CREATE TABLE action_triggers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_enabled BOOLEAN DEFAULT true,
    
    -- Trigger condition
    trigger_event VARCHAR(100) NOT NULL,
    trigger_conditions JSONB DEFAULT '{}'::jsonb, -- e.g., {"severity": "critical"}
    
    -- Action to perform
    action_type VARCHAR(50) NOT NULL, -- create_jira_ticket, send_slack, create_linear_issue
    action_config JSONB NOT NULL,
    
    -- Integration reference
    integration_id UUID REFERENCES integrations(id) ON DELETE CASCADE,
    
    -- Statistics
    trigger_count INTEGER DEFAULT 0,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_action_triggers_org_id ON action_triggers(organization_id);
CREATE INDEX idx_action_triggers_enabled ON action_triggers(is_enabled);
CREATE INDEX idx_action_triggers_event ON action_triggers(trigger_event);

-- Add triggers
CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_webhooks_updated_at BEFORE UPDATE ON webhooks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_action_triggers_updated_at BEFORE UPDATE ON action_triggers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
