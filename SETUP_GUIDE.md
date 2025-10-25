# 🚀 PCI DSS Compliance Automation POC - Setup Guide

Complete setup instructions for the hackathon demo.

## 📋 Prerequisites

- **Railway Account** (for PostgreSQL database)
- **n8n Instance** (self-hosted or cloud)
- **OpenAI API Key** (for GPT-4o)
- **GitHub Personal Access Token** (for issue creation)
- **Python 3.8+** (for knowledge base setup)

## 🗄️ Phase 1: Database Setup (5 minutes)

### 1.1 Create Railway PostgreSQL Database

1. Go to [Railway.app](https://railway.app)
2. Create new project → Add PostgreSQL
3. Go to Database → Connect → Copy connection URL
4. Note down your `DATABASE_URL`

### 1.2 Initialize Database Schema

```bash
# Set environment variable (replace with your Railway connection string)
export DATABASE_URL="postgresql://username:password@host:port/database"

# Run schema setup
psql $DATABASE_URL -f database/001_schema.sql
```

**Verify Setup:**
```sql
-- Check tables were created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' ORDER BY table_name;

-- Should show: chatbot_queries, evidence_packages, findings, knowledge_simple, workflow_logs
```

## 📚 Phase 2: Knowledge Base Setup (10 minutes)

### 2.1 Install Python Dependencies

```bash
cd scripts/
pip install -r requirements.txt
```

**Requirements.txt contents:**
```
psycopg2-binary>=2.9.0
PyPDF2>=3.0.0
python-dotenv>=1.0.0
openai>=1.0.0
```

### 2.2 Ingest Compliance Documents

```bash
# Set up environment (replace with your actual credentials)
export DATABASE_URL="postgresql://username:password@host:port/database"
export OPENAI_API_KEY="sk-your-openai-api-key-here"  # Optional for vector mode

# Run knowledge base ingestion
python3 scripts/ingest_knowledge_base.py

# Alternative: Use setup script
chmod +x scripts/setup_knowledge_base.sh
./scripts/setup_knowledge_base.sh
```

**Expected Output:**
```
📚 Processing: compliance/pci-dss-requirement-6-summary.md
✅ Successfully ingested: 12 chunks from PCI DSS Requirement 6 Summary
📊 Total ingested: 12 knowledge chunks
```

### 2.3 Verify Knowledge Base

```sql
-- Check knowledge base content
SELECT doc_type, COUNT(*) FROM knowledge_simple GROUP BY doc_type;

-- Test search functionality
SELECT title FROM knowledge_simple 
WHERE content ILIKE '%sql injection%' 
LIMIT 3;
```

## ⚙️ Phase 3: n8n Workflow Setup (15 minutes)

### 3.1 Configure n8n Credentials

In your n8n instance, create these credentials:

**PostgreSQL Credential (id: `railway-postgres`):**
- Host: `[your-railway-host]`
- Database: `[your-database-name]`
- User: `[your-username]`
- Password: `[your-password]`
- Port: `[usually-5432]`
- SSL Mode: `require`

**OpenAI Credential (id: `openai-credentials`):**
- API Key: `[your-openai-api-key]`

**GitHub Credential (id: `github-auth`):**
- Header Auth
- Name: `Authorization`
- Value: `token [your-github-token]`

### 3.2 Import Workflows

1. **Import PCI Automation Workflow:**
   - Copy content from `n8n-workflows/pci-automation-workflow.json`
   - n8n → Import from URL/File → Paste JSON
   - Save workflow

2. **Import ChatBot RAG Workflow:**
   - Copy content from `n8n-workflows/chatbot-rag-workflow.json`
   - n8n → Import from URL/File → Paste JSON
   - Save workflow

### 3.3 Configure Workflow Settings

**PCI Automation Workflow:**
- Set schedule trigger to desired frequency (default: Monday 9 AM)
- Update GitHub repository URL in "Create GitHub Issue" node
- Test workflow with manual execution

**ChatBot RAG Workflow:**
- Enable webhook: `/webhook/chat`
- Note webhook URL for testing
- Configure CORS headers if needed

## 🧪 Phase 4: Testing & Validation (10 minutes)

### 4.1 Run Test Suite

```bash
# Set environment variables
export DATABASE_URL="your-railway-connection-string"

# Run comprehensive tests
python3 scripts/test_poc.py
```

**Expected Results:**
```
🧪 TEST RESULTS SUMMARY
==============================
✅ DATABASE: PASS
   ✅ Database Connection: Connected to: PostgreSQL 14.x
   ✅ Schema Validation: All 5 required tables exist
   ✅ Sample Data Check: Knowledge base has 12 chunks

✅ KNOWLEDGE BASE: PASS
   ✅ Keyword Search: Found 2 results for SQL injection keywords
   ✅ Full-Text Search: Found 1 results for XSS search

✅ PCI WORKFLOW: PASS
   ✅ Finding Storage: Successfully stored test finding
   ✅ Evidence Package: Evidence document created

✅ CHATBOT WORKFLOW: PASS
   ✅ Knowledge Search: Found 3 results
   ✅ Query Logging: ChatBot interaction logged

📈 OVERALL RESULTS: 8/8 tests passed
🎉 POC is ready for demo!
```

### 4.2 Manual Workflow Tests

**Test PCI Automation:**
```bash
# Trigger workflow manually in n8n
# Check for:
# - Mock findings generated
# - AI analysis completed
# - GitHub issue created
# - Evidence packages stored
```

**Test ChatBot Workflow:**
```bash
# Send test request to webhook
curl -X POST http://your-n8n-instance/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is SQL injection and how to prevent it?",
    "user_id": "test-user",
    "session_id": "test-session"
  }'
```

**Expected ChatBot Response:**
```json
{
  "status": "success",
  "answer": "SQL injection is a code injection technique...",
  "sources": [
    {
      "title": "PCI DSS Requirement 6.5.1",
      "type": "compliance_doc",
      "relevance": 0.95
    }
  ],
  "confidence": 0.92,
  "result_count": 3
}
```

## 🎯 Phase 5: Demo Preparation (5 minutes)

### 5.1 Demo Flow

1. **Show Database Content:**
   ```sql
   SELECT finding_id, severity, title, pci_requirement 
   FROM findings ORDER BY created_at DESC LIMIT 5;
   ```

2. **Trigger PCI Workflow:**
   - Manual execution in n8n
   - Show workflow progress
   - Check GitHub issues created

3. **Demo ChatBot:**
   - Ask: "What are the PCI DSS requirements for secure coding?"
   - Ask: "Show me critical security findings"
   - Ask: "What is the compliance status for requirement 6.5.1?"

4. **Show Evidence Packages:**
   ```sql
   SELECT finding_id, LEFT(evidence_document, 100) as preview
   FROM evidence_packages ORDER BY created_at DESC LIMIT 3;
   ```

### 5.2 Demo Script

```bash
# 1. Show system status
python3 scripts/test_poc.py

# 2. Show knowledge base
psql $DATABASE_URL -c "SELECT doc_type, COUNT(*) FROM knowledge_simple GROUP BY doc_type;"

# 3. Trigger workflows via n8n interface

# 4. Show results
psql $DATABASE_URL -c "SELECT finding_id, severity, title FROM findings ORDER BY created_at DESC LIMIT 5;"
```

## 🔧 Troubleshooting

### Common Issues

**Database Connection Failed:**
```bash
# Check connection string format
echo $DATABASE_URL
# Should be: postgresql://user:pass@host:port/db

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

**Knowledge Base Empty:**
```bash
# Check file permissions
ls -la knowledge_base/
# Re-run ingestion
python3 scripts/ingest_knowledge_base.py
```

**n8n Workflow Errors:**
- Check credentials are properly configured
- Verify webhook URLs are accessible
- Test database queries in Railway console

**GitHub Issues Not Created:**
- Verify GitHub token has repo permissions
- Check repository name in workflow configuration
- Test token: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user`

### Performance Optimization

**Database Queries:**
```sql
-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_findings_pci_requirement ON findings(pci_requirement);
CREATE INDEX IF NOT EXISTS idx_knowledge_keywords ON knowledge_simple USING gin(keywords);
```

**n8n Settings:**
- Set execution timeout to 60 seconds
- Enable error retry (3 attempts)
- Configure webhook response timeout

## 📊 Monitoring & Logs

### Key Metrics to Track

```sql
-- Workflow execution stats
SELECT 
    workflow_name, 
    COUNT(*) as executions,
    AVG(duration_ms) as avg_duration_ms,
    SUM(findings_processed) as total_findings
FROM workflow_logs 
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY workflow_name;

-- ChatBot usage
SELECT 
    DATE(created_at) as date,
    COUNT(*) as queries,
    AVG(confidence_score) as avg_confidence
FROM chatbot_queries 
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date;

-- Finding status distribution
SELECT 
    severity, 
    status, 
    COUNT(*) as count
FROM findings 
GROUP BY severity, status
ORDER BY severity, status;
```

## 🎉 Next Steps

After successful POC demo:

1. **Production Deployment:**
   - Set up real Snyk API integration
   - Configure ClickUp task automation
   - Add Slack notifications
   - Implement user authentication

2. **Enhanced Features:**
   - Vector database with pgvector
   - Advanced RAG with embeddings
   - Multi-repository support
   - Custom compliance frameworks

3. **Security Hardening:**
   - Environment variable management
   - API rate limiting
   - Audit logging
   - Data encryption at rest

---

**🚀 You're all set! The POC is ready for the hackathon demo.**

For questions or issues, check the troubleshooting section or test with `python3 scripts/test_poc.py`.