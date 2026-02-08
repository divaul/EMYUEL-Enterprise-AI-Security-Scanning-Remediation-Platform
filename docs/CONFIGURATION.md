# Configuration Guide

Complete reference for configuring EMYUEL platform.

## Table of Contents

- [Environment Variables](#environment-variables)
- [Scan Profiles](#scan-profiles)
- [LLM Provider Configuration](#llm-provider-configuration)
- [Integration Configuration](#integration-configuration)
- [Security Settings](#security-settings)

---

## Environment Variables

Copy `.env.example` to `.env` and configure the following variables.

### Application Settings

```env
# Environment (development, staging, production)
ENVIRONMENT=development

# Debug mode (NEVER enable in production)
DEBUG=false

# API Gateway
API_GATEWAY_HOST=0.0.0.0
API_GATEWAY_PORT=8000
```

### Database Configuration

```env
# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=emyuel
POSTGRES_USER=emyuel_user
POSTGRES_PASSWORD=your-strong-password-here

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0
```

### LLM Provider Configuration

#### Primary Provider Selection

```env
# Choose primary provider: openai, gemini, or claude
LLM_PRIMARY_PROVIDER=openai

# Enable automatic fallback to other providers
LLM_FALLBACK_ENABLED=true
```

#### OpenAI Configuration

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.1
```

**Getting OpenAI API Key**:
1. Visit https://platform.openai.com/
2. Create account or sign in
3. Navigate to API Keys section
4. Create new secret key

#### Google Gemini Configuration

```env
GOOGLE_AI_API_KEY=your-google-ai-api-key
GEMINI_MODEL=gemini-pro
GEMINI_MAX_TOKENS=4096
GEMINI_TEMPERATURE=0.1
```

**Getting Gemini API Key**:
1. Visit https://makersuite.google.com/
2. Click "Get API Key"
3. Create API key for your project

#### Anthropic Claude Configuration

```env
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
CLAUDE_MODEL=claude-3-opus-20240229
CLAUDE_MAX_TOKENS=4096
CLAUDE_TEMPERATURE=0.1
```

**Getting Claude API Key**:
1. Visit https://console.anthropic.com/
2. Create account or sign in
3. Navigate to API Keys
4. Generate new key

---

## Scan Profiles

EMYUEL provides three pre-configured scan profiles:

### Quick Scan

Fast scan for CI/CD pipelines (5-10 minutes).

```yaml
# configs/scanner-profiles/quick-scan.yaml
scan:
  profile: quick
  timeout: 600  # 10 minutes
  detectors:
    - sqli
    - xss
  depth: shallow
  parallel_files: 10
  max_files: 100
```

**Use When**:
- Running in CI/CD pipeline
- Quick feedback needed
- Pull request validation

### Standard Scan (Default)

Balanced scan for regular security checks (15-30 minutes).

```yaml
# configs/scanner-profiles/standard.yaml
scan:
  profile: standard
  timeout: 1800  # 30 minutes
  detectors:
    - sqli
    - xss
    - ssrf
    - rce
    - auth
    - authz
  depth: medium
  parallel_files: 5
  max_files: 1000
```

**Use When**:
- Regular scheduled scans
- Pre-production testing
- Standard security assessment

### Comprehensive Scan

Deep scan with all detectors (30-60 minutes).

```yaml
# configs/scanner-profiles/comprehensive.yaml
scan:
  profile: comprehensive
  timeout: 3600  # 60 minutes
  detectors: all
  depth: deep
  parallel_files: 3
  max_files: 10000
  dynamic_analysis: true
```

**Use When**:
- Pre-release security audit
- Compliance requirements
- Thorough security assessment

---

## Integration Configuration

### Jira Integration

```env
JIRA_ENABLED=true
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token
JIRA_PROJECT_KEY=SEC
```

**Setup Steps**:
1. Generate API token at https://id.atlassian.com/manage-profile/security/api-tokens
2. Create dedicated project for security findings
3. Configure issue types and workflows

**Auto-create Tickets**:
```yaml
integrations:
  jira:
    auto_create: true
    severity_threshold: high  # Only create for high/critical
    custom_fields:
      security_team: "Security Team"
      environment: production
```

### Slack Integration

```env
SLACK_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL=#security-alerts
```

**Setup Steps**:
1. Create Slack app at https://api.slack.com/apps
2. Enable Incoming Webhooks
3. Add webhook to workspace
4. Copy webhook URL

**Notification Settings**:
```yaml
integrations:
  slack:
    notify_on:
      - scan_complete
      - critical_vulnerability_found
      - scan_failed
    mention_on_critical: true
```

### Linear Integration

```env
LINEAR_ENABLED=true
LINEAR_API_KEY=your-linear-api-key
LINEAR_TEAM_ID=your-team-id
```

### ServiceNow Integration

```env
SERVICENOW_ENABLED=true
SERVICENOW_INSTANCE=your-instance.service-now.com
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password
```

---

## Security Settings

### JWT Configuration

```env
# Use strong random key (min 32 characters)
JWT_SECRET_KEY=your-very-long-and-random-secret-key-here

# Token expiration
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Generate Secure Key**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Rate Limiting

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10
```

### CORS Configuration

```env
# Comma-separated list of allowed origins
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://your-domain.com
CORS_ALLOW_CREDENTIALS=true
```

### SSO Configuration (Optional)

#### SAML

```env
SSO_ENABLED=true
SAML_ENTITY_ID=https://emyuel.your-domain.com
SAML_ACS_URL=https://emyuel.your-domain.com/auth/saml/callback
SAML_IDP_METADATA_URL=https://your-idp.com/metadata
```

#### OIDC

```env
OIDC_CLIENT_ID=your-oidc-client-id
OIDC_CLIENT_SECRET=your-oidc-client-secret
OIDC_DISCOVERY_URL=https://your-idp.com/.well-known/openid-configuration
```

---

## Advanced Configuration

### Scanner Settings

```env
# Maximum concurrent scans
MAX_CONCURRENT_SCANS=5

# Scan timeout (seconds)
SCAN_TIMEOUT=3600

# Enable dynamic analysis (requires additional setup)
DYNAMIC_ANALYSIS_ENABLED=false
```

### Storage Configuration

```env
# Storage type: local, s3, gcs, azure
STORAGE_TYPE=local
STORAGE_PATH=/var/lib/emyuel/storage

# For S3 storage
S3_BUCKET_NAME=emyuel-storage
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your-aws-access-key
S3_SECRET_ACCESS_KEY=your-aws-secret-key
```

### Email Configuration

```env
SMTP_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-email-password
SMTP_FROM_EMAIL=noreply@emyuel.example.com
```

### Feature Flags

```env
# Enable/disable features
FEATURE_WEBHOOKS_ENABLED=true
FEATURE_API_GRAPHQL_ENABLED=true
FEATURE_MULTI_TENANCY_ENABLED=false
FEATURE_CUSTOM_DETECTORS_ENABLED=false
```

---

## Configuration Validation

Validate your configuration before deployment:

```bash
# Validate environment variables
python scripts/validate_config.py

# Test database connection
python scripts/test_db_connection.py

# Test LLM providers
python scripts/test_llm_providers.py
```

---

## Best Practices

1. **Never commit `.env` files** - Keep in `.gitignore`
2. **Use strong passwords** - Minimum 16 characters
3. **Rotate API keys regularly** - Every 90 days
4. **Use environment-specific configs** - `.env.dev`, `.env.prod`
5. **Enable monitoring** - Prometheus + Grafana
6. **Configure backups** - Regular database backups
7. **Review audit logs** - Monitor for suspicious activity

---

## Troubleshooting

### LLM Provider Errors

**Problem**: "Authentication failed"
- **Solution**: Check API key is correct and has credits

**Problem**: "Rate limit exceeded"
- **Solution**: Enable fallback providers or upgrade plan

### Database Connection Issues

**Problem**: "Could not connect to PostgreSQL"
- **Solution**: Verify `POSTGRES_HOST` and credentials
- **Solution**: Check database is running: `docker-compose ps postgres`

### Integration Failures

**Problem**: "Jira ticket creation failed"
- **Solution**: Verify API token and project key
- **Solution**: Check user has permission to create issues

---

## Support

For configuration help:
- Documentation: [docs/](docs/)
- GitHub Issues: https://github.com/your-org/emyuel/issues
- Email: support@emyuel.io
