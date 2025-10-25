# PCI DSS Compliance Automation - Simplified Implementation (Hackathon-Ready)

Based on Codex review feedback, this is a **realistic 2-3 day hackathon scope** addressing critical issues in the original plan.

## 🎯 **Simplified Goals (Achievable in 2-3 days)**

1. **Core Workflow:** 1 repo → Mock scan → Store findings → Create GitHub Issue
2. **Simple ChatBot:** Answer questions from static knowledge base
3. **Evidence Package:** Generate audit-ready documentation

**Removed from scope:**
- ❌ Multiple repo scanning
- ❌ Live Snyk API integration  
- ❌ ClickUp/Slack integrations
- ❌ Complex vector search
- ❌ Automated PR creation with code fixes

---

## Phase 1: Minimal Database Setup (Day 1 - 2 hours)

### Step 1: Railway PostgreSQL (No pgvector needed)

```sql
-- File: database/001_simple_schema.sql
-- Simple schema without vector complexity

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Core findings table
CREATE TABLE findings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    finding_id VARCHAR(255) UNIQUE NOT NULL,
    repo_name VARCHAR(255) NOT NULL,
    severity VARCHAR(50) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    title VARCHAR(500),
    description TEXT,
    fix_suggestion TEXT,
    affected_file VARCHAR(500),
    line_number INTEGER,
    cwe_id VARCHAR(50),
    pci_requirement VARCHAR(50),
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Simple knowledge base (no vectors)
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500),
    content TEXT,
    doc_type VARCHAR(100), -- 'policy', 'compliance', 'faq'
    keywords TEXT[], -- Simple keyword search
    created_at TIMESTAMP DEFAULT NOW()
);

-- Evidence packages
CREATE TABLE evidence_packages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    finding_id VARCHAR(255) REFERENCES findings(finding_id),
    github_issue_url TEXT,
    evidence_document TEXT, -- Markdown content
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_findings_severity ON findings(severity);
CREATE INDEX idx_findings_repo ON findings(repo_name);
CREATE INDEX idx_knowledge_keywords ON knowledge_base USING GIN (keywords);
```

### Step 2: Deploy to Railway

```bash
# Simple deployment
railway login
railway link
psql [CONNECTION_STRING] < database/001_simple_schema.sql
```

---

## Phase 2: Mock Data and Static Knowledge Base (Day 1 - 2 hours)

### Step 1: Create Mock Scan Results

```json
// File: mock-data/sample-findings.json
[
  {
    "finding_id": "DEMO-001",
    "repo_name": "payment-gateway",
    "severity": "critical",
    "title": "SQL Injection in Payment Query",
    "description": "User input directly concatenated into SQL query without sanitization in payment processing endpoint",
    "fix_suggestion": "Use parameterized queries or prepared statements. Replace: `SELECT * FROM payments WHERE id = ${userId}` with `SELECT * FROM payments WHERE id = ?`",
    "affected_file": "src/controllers/payment.controller.js",
    "line_number": 145,
    "cwe_id": "CWE-89",
    "pci_requirement": "6.5.1"
  },
  {
    "finding_id": "DEMO-002", 
    "repo_name": "merchant-api",
    "severity": "high",
    "title": "Cross-Site Scripting (XSS) in Error Handler",
    "description": "User input reflected in error messages without proper HTML encoding",
    "fix_suggestion": "Implement output encoding using DOMPurify: `const cleanHtml = DOMPurify.sanitize(userInput);`",
    "affected_file": "src/middleware/error.handler.js",
    "line_number": 67,
    "cwe_id": "CWE-79",
    "pci_requirement": "6.5.7"
  }
]
```

### Step 2: Create Static Knowledge Base

```sql
-- Insert static compliance knowledge
INSERT INTO knowledge_base (title, content, doc_type, keywords) VALUES
('PCI DSS Requirement 6.5.1', 
 'All web applications must be protected against SQL injection attacks. Use parameterized queries, stored procedures, or properly validated input.',
 'compliance',
 ARRAY['sql injection', 'pci dss', '6.5.1', 'parameterized queries']),

('PCI DSS Requirement 6.5.7',
 'All web applications must be protected against cross-site scripting (XSS). Implement proper output encoding and input validation.',
 'compliance', 
 ARRAY['xss', 'cross-site scripting', '6.5.7', 'output encoding']),

('Secure Code Review Process',
 'All custom code must be reviewed by someone other than the code author before deployment. Review should check for common vulnerabilities.',
 'policy',
 ARRAY['code review', 'security', 'deployment', 'process']);
```

---

## Phase 3: Simple n8n Workflows (Day 2)

### Workflow 1: Mock Security Scan

**Simple 6-node workflow:**

1. **Manual Trigger**
   - Type: Manual Trigger
   - Purpose: Start workflow manually

2. **Load Mock Data**
   - Type: Function (JavaScript)
   - Code:
   ```javascript
   // Return mock findings
   const mockFindings = [
     {
       finding_id: "DEMO-001",
       repo_name: "payment-gateway", 
       severity: "critical",
       title: "SQL Injection in Payment Query",
       description: "User input directly concatenated into SQL query...",
       fix_suggestion: "Use parameterized queries...",
       affected_file: "src/controllers/payment.controller.js",
       line_number: 145,
       cwe_id: "CWE-89",
       pci_requirement: "6.5.1"
     }
   ];
   
   return mockFindings.map(finding => ({ json: finding }));
   ```

3. **Store Finding to Database**
   - Type: Postgres
   - Operation: Insert
   - Table: findings
   - Simple insert without complex JSON handling

4. **Generate Evidence Package**
   - Type: Function (JavaScript)
   - Code:
   ```javascript
   const finding = $json;
   
   const evidenceMarkdown = `
   # Security Finding Evidence Package
   
   **Finding ID:** ${finding.finding_id}
   **Severity:** ${finding.severity}
   **PCI Requirement:** ${finding.pci_requirement}
   
   ## Vulnerability Details
   - **Repository:** ${finding.repo_name}
   - **File:** ${finding.affected_file}:${finding.line_number}
   - **CWE:** ${finding.cwe_id}
   
   ## Description
   ${finding.description}
   
   ## Recommended Fix
   ${finding.fix_suggestion}
   
   ## Timeline
   - **Discovered:** ${new Date().toISOString()}
   - **Status:** Open
   - **Priority:** ${finding.severity}
   
   ---
   Generated by DOKU Compliance Automation
   `;
   
   return { json: { ...finding, evidence_document: evidenceMarkdown } };
   ```

5. **Create GitHub Issue (NOT PR)**
   - Type: HTTP Request
   - Method: POST
   - URL: `https://api.github.com/repos/the-bubur/hackathon-pci-compliance/issues`
   - Headers: `Authorization: Bearer {{$credentials.github_token}}`
   - Body:
   ```json
   {
     "title": "[{{$json.severity}}] {{$json.title}}",
     "body": "**Finding ID:** {{$json.finding_id}}\n**File:** {{$json.affected_file}}:{{$json.line_number}}\n\n{{$json.description}}\n\n**Recommended Fix:**\n```\n{{$json.fix_suggestion}}\n```\n\n**PCI Requirement:** {{$json.pci_requirement}}\n**CWE:** {{$json.cwe_id}}",
     "labels": ["security", "{{$json.severity}}", "pci-compliance"]
   }
   ```

6. **Store Evidence Package**
   - Type: Postgres
   - Operation: Insert  
   - Table: evidence_packages
   - Store complete evidence with GitHub issue link

### Workflow 2: Simple Knowledge ChatBot

**Simple 4-node workflow:**

1. **Webhook Trigger**
   - Type: Webhook
   - Method: POST
   - Path: `/chat`
   - Body: `{"query": "What is PCI DSS requirement 6.5.1?"}`

2. **Search Knowledge Base**
   - Type: Postgres
   - Operation: Select
   - Query:
   ```sql
   SELECT title, content, doc_type
   FROM knowledge_base
   WHERE keywords && string_to_array($1, ' ')
   OR content ILIKE '%' || $1 || '%'
   ORDER BY 
     CASE WHEN title ILIKE '%' || $1 || '%' THEN 1 ELSE 2 END,
     created_at DESC
   LIMIT 3
   ```

3. **Format Response with AI (Optional)**
   - Type: OpenAI (Simple completion, not agent)
   - Model: gpt-4o-mini (cheaper)
   - Prompt:
   ```
   Based on these compliance documents, answer the user's question: "{{$json.query}}"
   
   Available information:
   {{$json.search_results}}
   
   Provide a clear, accurate answer with source references.
   ```

4. **Return Response**
   - Type: Respond to Webhook
   - Body:
   ```json
   {
     "answer": "{{$json.ai_response}}",
     "sources": "{{$json.search_results}}",
     "timestamp": "{{$now}}"
   }
   ```

---

## Phase 4: Testing and Demo (Day 3)

### Simple Testing Checklist

- [ ] Database tables created successfully
- [ ] Mock data loads correctly  
- [ ] n8n workflows execute without errors
- [ ] GitHub issue gets created
- [ ] Evidence package generates
- [ ] ChatBot responds to basic queries
- [ ] All credentials properly configured

### Demo Script (5 minutes)

**Setup:**
- Pre-load mock findings in database
- Clear GitHub issues
- Open n8n workflow

**Demo Flow:**
1. **Trigger workflow manually** (30 sec)
   - Show workflow execution in n8n
   - Watch green checkmarks

2. **Show results** (2 min)
   - Database: `SELECT * FROM findings ORDER BY created_at DESC LIMIT 1;`
   - GitHub: Show created issue with security label
   - Evidence: Show generated markdown

3. **Test ChatBot** (2 min)
   - Query: "What is SQL injection in PCI DSS?"
   - Show response with relevant compliance info
   - Query: "Show me critical findings"
   - Show database results

4. **Value proposition** (30 sec)
   - Manual process: Hours
   - Automated: 30 seconds
   - Complete audit trail ready

---

## Credential Configuration (Secure)

### n8n Credentials (No hardcoded values)

```bash
# Environment variables (not in code)
OPENAI_API_KEY=[your-key]
GITHUB_TOKEN=[your-token]
DATABASE_URL=[railway-connection]
```

### n8n Credential Setup

1. **OpenAI Account**
   - Type: OpenAI
   - API Key: `[YOUR_OPENAI_KEY]`

2. **GitHub**
   - Type: Header Auth
   - Name: Authorization
   - Value: `Bearer [YOUR_GITHUB_TOKEN]`

3. **PostgreSQL**
   - Type: Postgres
   - Connection details from Railway (not hardcoded)

---

## Risk Mitigation

### What Could Go Wrong:

1. **GitHub API rate limit**
   - **Mitigation:** Use personal token (5000/hour)
   - **Fallback:** Create local file instead of issue

2. **Database connection fails**
   - **Mitigation:** Test connection first
   - **Fallback:** Store to JSON files

3. **OpenAI API quota**
   - **Mitigation:** Use minimal tokens, gpt-4o-mini
   - **Fallback:** Simple template responses

4. **n8n workflow fails**
   - **Mitigation:** Test each node individually
   - **Fallback:** Manual execution of steps

---

## Success Metrics (Realistic)

### Technical:
- [ ] Workflow completes in <1 minute
- [ ] ChatBot responds in <3 seconds  
- [ ] Zero manual intervention needed
- [ ] All evidence properly stored

### Business:
- [ ] Complete audit trail generated
- [ ] GitHub integration working
- [ ] Demonstrates PCI compliance automation
- [ ] Scalable to multiple repos

---

## Future Enhancements (Post-Hackathon)

1. **Real security scanner integration**
2. **Advanced vector search with pgvector**
3. **Automated PR creation with fixes**
4. **Multiple repository support**
5. **ClickUp/Slack integrations**
6. **Dashboard and reporting**

---

## Time Allocation

**Day 1 (4 hours):**
- Database setup: 1 hour
- Mock data creation: 1 hour
- n8n credential setup: 2 hours

**Day 2 (6 hours):**
- Workflow 1 (scan): 3 hours
- Workflow 2 (chatbot): 2 hours
- Testing: 1 hour

**Day 3 (2 hours):**
- Bug fixes: 1 hour
- Demo preparation: 1 hour

**Total: 12 hours** (realistic for hackathon)

---

This simplified approach addresses all Codex feedback:
- ✅ Manageable scope for 2-3 days
- ✅ Mock data instead of unreliable APIs
- ✅ GitHub Issues instead of complex PR creation
- ✅ Simple keyword search instead of vector complexity
- ✅ No pgvector dependency issues
- ✅ Secure credential handling
- ✅ Clear, achievable deliverables