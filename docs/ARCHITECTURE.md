# EMYUEL Architecture Documentation

## System Architecture Overview

EMYUEL follows a **microservices architecture** designed for scalability, maintainability, and independent deployment. Each service has a well-defined responsibility and communicates through APIs.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        External Clients                          │
│              (Web Dashboard, CLI, CI/CD Systems)                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS
                         ▼
          ┌──────────────────────────────┐
          │      Load Balancer /         │
          │       API Gateway            │
          │  ┌────────────────────────┐  │
          │  │ Rate Limiting          │  │
          │  │ Authentication (JWT)   │  │
          │  │ Request Routing        │  │
          │  │ Response Aggregation   │  │
          │  └────────────────────────┘  │
          └──────────────┬───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────────┐ ┌────────────┐ ┌─────────────┐
│   Scanner      │ │Integration │ │    Auth     │
│     Core       │ │    Hub     │ │  Service    │
└───────┬────────┘ └─────┬──────┘ └──────┬──────┘
        │                │               │
        │                │               │
        ▼                ▼               ▼
┌────────────────┐ ┌────────────┐ ┌─────────────┐
│ LLM            │ │ Webhooks   │ │  RBAC       │
│ Orchestrator   │ │ & Actions  │ │  Engine     │
└───────┬────────┘ └────────────┘ └─────────────┘
        │
        │
  ┌─────┴──────┬──────────┐
  │            │          │
  ▼            ▼          ▼
┌──────┐  ┌────────┐  ┌───────┐
│OpenAI│  │ Gemini │  │Claude │
└──────┘  └────────┘  └───────┘

        ┌───────────────────┐
        │  Data Layer       │
        ├───────────────────┤
        │ PostgreSQL        │
        │ Redis Cache       │
        │ Message Queue     │
        └───────────────────┘
```

## Services

### 1. API Gateway

**Responsibility**: Central entry point for all client requests

**Key Features**:
- Request routing to appropriate microservices
- JWT authentication and validation
- Rate limiting and throttling
- API versioning
- Request/response transformation
- CORS handling

**Technology**: FastAPI (Python 3.11)

**Port**: 8000

---

### 2. LLM Orchestrator

**Responsibility**: Manage multiple LLM providers with intelligent fallback

**Key Features**:
- Provider abstraction layer (OpenAI, Gemini, Claude)
- Automatic failover between providers
- Provider health monitoring
- Usage tracking and cost optimization
- Token estimation
- Unified interface for security analysis

**Technology**: Python with async/await

**Providers Supported**:
- OpenAI GPT-4 Turbo
- Google Gemini Pro
- Anthropic Claude 3 Opus

---

### 3. Scanner Core

**Responsibility**: Execute security scans and coordinate vulnerability detection

**Key Features**:
- Multiple vulnerability detectors (SQL Injection, XSS, SSRF, etc.)
- LLM-powered data flow analysis
- CVSS scoring
- Code-level remediation suggestions
- Static analysis integration
- Parallel scanning for performance

**Detectors**:
- SQL Injection Detector
- XSS Detector (Reflected, Stored, DOM-based)
- SSRF Detector
- RCE Detector (planned)
- Auth/AuthZ Detector (planned)
- Deserialization Detector (planned)

**Technology**: Python with asyncio

---

### 4. Integration Hub

**Responsibility**: Manage third-party integrations

**Supported Integrations**:
- **Jira**: Automatic ticket creation for vulnerabilities
- **Slack**: Real-time notifications
- **Linear**: Issue tracking
- **ServiceNow**: Incident management
- **GitHub/GitLab**: PR comments, status checks

**Features**:
- Webhook management
- Action triggers (event-based automation)
- Webhook delivery tracking
- Retry logic for failed deliveries

---

### 5. Authentication & Authorization Service

**Responsibility**: User authentication and RBAC

**Key Features**:
- JWT token generation and validation
- Password hashing (bcrypt)
- SSO integration (SAML, OIDC)
- Role-Based Access Control
- Permission management

**Roles**:
- Admin: Full system access
- Team Lead: Manage team and projects
- Developer: Run scans and view results
- Scanner: Execute scans only
- Viewer: Read-only access

---

### 6. Audit & Compliance Service

**Responsibility**: Immutable audit logging and compliance reporting

**Key Features**:
- Append-only audit logs (cannot be modified/deleted)
- Comprehensive activity tracking
- Compliance report generation (OWASP Top 10, PCI-DSS, SOC 2)
- Export functionality (CSV, JSON)
- Configurable retention policies

---

### 7. Reporting Service

**Responsibility**: Generate security reports in various formats

**Supported Formats**:
- PDF (executive summaries)
- HTML (detailed technical reports)
- Markdown (developer-friendly)
- JSON (machine-readable)
- CSV (data export)

**Report Types**:
- Vulnerability reports
- Compliance reports
- Trend analysis
- Executive dashboards

---

### 8. Job Queue Service

**Responsibility**: Asynchronous task processing

**Technology**: Celery with Redis backend

**Job Types**:
- Scan execution (long-running)
- Report generation
- Integration webhooks
- Scheduled tasks

---

## Data Flow

### Scan Execution Flow

```
1. Client → API Gateway: Create scan request
2. API Gateway → Auth Service: Validate token
3. API Gateway → Scanner Core: Initiate scan
4. Scanner Core → Job Queue: Enqueue scan job
5. Job Queue → Scanner Core: Process scan
6. Scanner Core → LLM Orchestrator: Analyze code
7. LLM Orchestrator → OpenAI/Gemini/Claude: LLM analysis
8. Scanner Core → Database: Store results
9. Scanner Core → Integration Hub: Trigger webhooks
10. Integration Hub → Jira/Slack: Create tickets/notify
11. Scanner Core → API Gateway: Return results
12. API Gateway → Client: Scan results
```

### Authentication Flow

```
1. Client → API Gateway: POST /auth/login
2. API Gateway → Auth Service: Validate credentials
3. Auth Service → Database: Check user/password
4. Auth Service → Audit Service: Log login attempt
5. Auth Service → API Gateway: JWT tokens
6. API Gateway → Client: Access + Refresh tokens
```

---

## Database Schema

### Core Tables

- **users**: User accounts
- **organizations**: Multi-tenancy support
- **projects**: Repositories to scan
- **scans**: Scan execution records
- **vulnerabilities**: Detected security issues

### RBAC Tables

- **roles**: Role definitions
- **permissions**: Granular permissions
- **role_permissions**: Role-permission mapping
- **user_roles**: User-role assignments

### Audit Tables

- **audit_logs**: Immutable activity logs (append-only)

### Integration Tables

- **integrations**: Third-party service configs
- **webhooks**: Webhook configurations
- **webhook_deliveries**: Delivery tracking
- **action_triggers**: Automated actions

---

## Technology Stack

### Backend

- **Language**: Python 3.11+
- **Framework**: FastAPI (async)
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Message Queue**: Celery + Redis

### LLM Integration

- **OpenAI**: `openai` Python SDK
- **Gemini**: `google-generativeai` SDK
- **Claude**: `anthropic` SDK

### Monitoring

- **Metrics**: Prometheus
- **Dashboards**: Grafana  
- **Tracing**: OpenTelemetry (optional)

### Deployment

- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **IaC**: Terraform
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins

---

## Security Considerations

### Authentication & Authorization

- JWT with short expiration (60 minutes)
- Refresh tokens with longer expiration (7 days)
- RBAC for fine-grained access control
- SSO support for enterprise

### Data Protection

- Passwords hashed with bcrypt
- Sensitive data encrypted at rest
- TLS for data in transit
- API keys stored securely (environment variables)

### Audit & Compliance

- Immutable audit logs
- Compliance reporting
- Data retention policies
- GDPR considerations

---

## Scalability

### Horizontal Scaling

- Stateless services (can scale independently)
- Load balancing across instances
- Database connection pooling
- Redis for session storage

### Performance Optimization

- Async/await throughout
- Parallel scan execution
- Database query optimization
- Caching frequently accessed data

### Resource Management

- LLM provider fallback for availability
- Rate limiting to prevent abuse
- Job queue for long-running tasks
- Configurable concurrency limits

---

## Monitoring & Observability

### Metrics

- HTTP request metrics (rate, latency, errors)
- LLM usage (tokens, costs, latency)
- Database connection pool status
- Queue length and job processing time

### Alerts

- Service down alerts
- High error rates
- LLM quota exceeded
- Database connection pool exhausted
- High memory/disk usage

### Logging

- Structured logging (JSON)
- Centralized log aggregation
- Different log levels per service
- Request tracing with correlation IDs

---

## Deployment Options

### Option 1: Docker Compose (Development/Small Teams)

- Single-machine deployment
- Easy setup with `docker-compose up`
- Suitable for development and small teams

### Option 2: Kubernetes (Production/Enterprise)

- Multi-node cluster
- Auto-scaling
- High availability
- Load balancing
- Health checks and self-healing

### Option 3: Managed Cloud (SaaS)

- Fully managed service
- No infrastructure management
- Automatic updates
- Enterprise support

---

## API Design

### REST API

- RESTful endpoints (`/api/v1/scans`, `/api/v1/projects`, etc.)
- JSON request/response
- Standard HTTP methods (GET, POST, PUT, DELETE)
- Pagination for list endpoints
- Filtering and sorting

### GraphQL API (Planned)

- Single endpoint
- Client-specified queries
- Reduced over-fetching
- Real-time subscriptions

---

## Future Enhancements

1. **Real-time Scanning**: WebSocket-based live updates
2. **Custom Detectors**: User-defined vulnerability patterns
3. **ML-based Detection**: Machine learning for pattern recognition
4. **Multi-language Support**: Support for more programming languages
5. **IDE Plugins**: VSCode, IntelliJ IDEA integrations
6. **Mobile App**: iOS/Android apps for on-the-go monitoring
