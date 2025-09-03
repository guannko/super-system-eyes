# GEO PLATFORM - ARCHITECTURE BLUEPRINT
**Created:** 2025-09-04T00:15:00Z
**Source:** GPT Architecture Research
**Status:** 🟢 READY FOR IMPLEMENTATION

## 🏗️ ARCHITECTURE DECISION: MONOLITH FIRST

### Why Monolith (not Microservices):
1. **Speed of Development** - Single codebase, faster iteration
2. **Simple Deployment** - One app on Railway
3. **Shared Database** - No distributed transactions
4. **Lower Complexity** - No service orchestration needed
5. **Easy Refactoring** - Can split later when needed

### When to Consider Microservices (LATER):
- When different parts need different scaling
- When multiple teams work on different parts
- When some modules need different tech stacks
- NOT NOW! Start simple!

## 📁 RECOMMENDED PROJECT STRUCTURE

```
brain-index-geo-platform/
├── package.json
├── .env.example
├── Dockerfile
├── docker-compose.yml
│
├── src/
│   ├── index.js                    // App entry point
│   ├── server.js                   // Express/Fastify setup
│   │
│   ├── api/
│   │   ├── v1/
│   │   │   ├── routes/
│   │   │   │   ├── auth.routes.js
│   │   │   │   ├── analysis.routes.js
│   │   │   │   ├── optimize.routes.js
│   │   │   │   ├── monitor.routes.js
│   │   │   │   └── billing.routes.js
│   │   │   ├── middlewares/
│   │   │   │   ├── auth.middleware.js
│   │   │   │   ├── rateLimit.middleware.js
│   │   │   │   └── validation.middleware.js
│   │   │   └── validators/
│   │   │       └── schemas.js
│   │   └── v2/                    // Future version
│   │
│   ├── services/                  // Business Logic
│   │   ├── analyzer/
│   │   │   ├── AnalyzerService.js
│   │   │   ├── ChatGPTConnector.js
│   │   │   ├── GoogleConnector.js
│   │   │   └── PerplexityConnector.js
│   │   ├── optimizer/
│   │   │   ├── OptimizerService.js
│   │   │   ├── SchemaGenerator.js
│   │   │   └── ContentOptimizer.js
│   │   ├── monitor/
│   │   │   ├── MonitorService.js
│   │   │   └── AlertService.js
│   │   └── billing/
│   │       └── SubscriptionService.js
│   │
│   ├── models/                    // Data Models
│   │   ├── Company.model.js
│   │   ├── Report.model.js
│   │   ├── User.model.js
│   │   └── Subscription.model.js
│   │
│   ├── database/
│   │   ├── connection.js
│   │   ├── migrations/
│   │   └── seeds/
│   │
│   ├── jobs/                      // Background Tasks
│   │   ├── queue.js
│   │   ├── workers/
│   │   │   ├── analyze.worker.js
│   │   │   └── monitor.worker.js
│   │   └── schedulers/
│   │       └── daily-check.js
│   │
│   ├── utils/
│   │   ├── logger.js
│   │   ├── cache.js
│   │   └── helpers.js
│   │
│   └── config/
│       ├── index.js
│       ├── database.config.js
│       └── services.config.js
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/
│   ├── api/
│   │   └── openapi.yaml
│   └── architecture/
│
└── scripts/
    ├── deploy.sh
    └── seed-data.js
```

## 🔌 API DESIGN PRINCIPLES

### 1. RESTful Structure
```javascript
// Examples of clean API endpoints
GET    /api/v1/companies/:id/visibility
POST   /api/v1/companies/:id/analyze
GET    /api/v1/reports/:id
POST   /api/v1/optimize
GET    /api/v1/monitor/alerts

// Versioning from day 1
/api/v1/...  // Current
/api/v2/...  // Future
```

### 2. Authentication Strategy
```javascript
// Multiple auth methods for different users
const AUTH_STRATEGY = {
  internal_dashboard: "JWT with refresh tokens",
  external_api: "API keys with rate limiting",
  agency_clients: "OAuth2 for white-label",
  webhooks: "HMAC signatures"
};
```

### 3. Error Handling
```javascript
// Standardized error responses
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "details": {
      "limit": 100,
      "reset": "2025-09-04T01:00:00Z"
    }
  }
}
```

## 🚀 DEPLOYMENT STRATEGY

### Phase 1: Railway (NOW)
```yaml
# railway.toml
[build]
  builder = "DOCKERFILE"

[deploy]
  numReplicas = 1
  healthcheckPath = "/health"
  restartPolicyType = "ON_FAILURE"

# Environment Variables
DATABASE_URL = postgresql://...
REDIS_URL = redis://...
OPENAI_API_KEY = sk-...
```

### Phase 2: Docker + VPS (LATER)
```dockerfile
# Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["node", "src/index.js"]
```

### Phase 3: Kubernetes (MUCH LATER)
- Only when really needed
- Start with Docker Swarm first
- K8s is overkill for < 100K users

## 📊 DATABASE DESIGN

### Single PostgreSQL Database (for now)
```sql
-- Main tables
companies
users
subscriptions
reports
ai_visibility_scores
optimizations
monitoring_alerts

-- Indexes for performance
CREATE INDEX idx_companies_domain ON companies(domain);
CREATE INDEX idx_reports_company_created ON reports(company_id, created_at);
CREATE INDEX idx_visibility_ai_system ON ai_visibility_scores(ai_system);
```

### Caching Strategy
```javascript
// Redis for hot data
const CACHE_KEYS = {
  visibility_score: "visibility:{companyId}:{aiSystem}",
  report: "report:{reportId}",
  user_session: "session:{userId}",
  rate_limit: "ratelimit:{apiKey}"
};

// TTL based on data type
const TTL = {
  visibility_score: 3600,    // 1 hour
  report: 86400,             // 24 hours
  user_session: 7200,        // 2 hours
  rate_limit: 60             // 1 minute
};
```

## 🔧 IMPLEMENTATION ROADMAP

### Week 1-2: Foundation
- [ ] Setup monolith structure
- [ ] Basic API endpoints
- [ ] Database schema
- [ ] Authentication system

### Week 3-4: Core Features
- [ ] Analyzer service (ChatGPT + Google)
- [ ] Basic optimizer
- [ ] Simple monitoring
- [ ] Dashboard API

### Month 2: Polish
- [ ] Add more AI connectors
- [ ] Background jobs
- [ ] Caching layer
- [ ] API documentation

### Month 3: Scale
- [ ] Performance optimization
- [ ] Advanced features
- [ ] White-label support
- [ ] Analytics

## 🎯 KEY DECISIONS SUMMARY

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | Monolith | Faster to build, easier to maintain initially |
| Framework | Fastify | Faster than Express, good plugin system |
| Database | PostgreSQL | Reliable, good for relational data |
| Cache | Redis | Standard, fast, supports many patterns |
| Queue | BullMQ | Robust, Redis-based, good for Node.js |
| Hosting | Railway → VPS | Start simple, migrate when needed |
| Frontend | Separate on Vercel | Better scalability, CDN benefits |

## ⚠️ AVOID THESE MISTAKES

1. **Don't start with microservices** - Premature optimization
2. **Don't skip API versioning** - Add it from day 1
3. **Don't hardcode secrets** - Use environment variables
4. **Don't forget monitoring** - At least basic logging
5. **Don't over-engineer** - YAGNI (You Aren't Gonna Need It)

## 📈 SCALING TRIGGERS

When to consider changes:
- **Split frontend/backend:** When dashboard needs CDN (immediately)
- **Add caching:** When same queries repeat (Month 1)
- **Background jobs:** When requests take > 5 seconds (Month 1)
- **Multiple instances:** When > 100 req/sec (Month 3-6)
- **Microservices:** When teams > 10 people (Year 2+)

---
*"Start simple, scale when needed, not before!"*