# Database Setup Instructions

## 🚀 Quick Setup (5 minutes)

### 1. Railway PostgreSQL Setup

1. **Sign up to Railway:** https://railway.app/ (use GitHub login)
2. **Create new project:** "DOKU Compliance POC"
3. **Add PostgreSQL service:**
   - Click "New" → "Database" → "PostgreSQL"
   - Wait for deployment (1-2 minutes)
4. **Get connection string:**
   - Go to PostgreSQL service → "Connect"
   - Copy the "Postgres Connection URL"

### 2. Deploy Schema

**Option A: Using Railway Dashboard**
1. Go to PostgreSQL service → "Data" tab
2. Click "Query" 
3. Copy content from `001_schema.sql`
4. Paste and execute

**Option B: Using Command Line**
```bash
# Install psql if not available
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql-client

# Connect and run schema
psql "your-railway-connection-string" < database/001_schema.sql
```

### 3. Verify Setup

```sql
-- Check tables created
\dt

-- Expected tables:
-- findings, evidence_packages, knowledge_simple, 
-- chatbot_queries, workflow_logs

-- Check sample data
SELECT count(*) FROM knowledge_simple;
-- Should return: 6

SELECT count(*) FROM findings;  
-- Should return: 2

-- Test compliance view
SELECT * FROM compliance_summary;
```

## 🔧 Configuration Options

### Simple Keyword Search (Default/Recommended)
- Uses `knowledge_simple` table
- Fast setup, no additional extensions
- Perfect for hackathon scope

### Advanced Vector Search (Optional)
- Requires pgvector extension
- Better semantic search
- More complex setup

To enable pgvector:
1. Check if available: `SELECT * FROM pg_available_extensions WHERE name = 'vector';`
2. If available: `CREATE EXTENSION vector;`
3. Set `USE_PGVECTOR=true` in environment

## 📊 Sample Queries for Testing

```sql
-- Test knowledge search
SELECT title, doc_type 
FROM knowledge_simple 
WHERE content ILIKE '%sql injection%';

-- Test findings
SELECT finding_id, severity, title 
FROM findings 
ORDER BY created_at DESC;

-- Test compliance summary
SELECT pci_requirement, total_findings, critical_count 
FROM compliance_summary;

-- Test ChatBot query logging
INSERT INTO chatbot_queries (user_query, bot_response, confidence_score) 
VALUES ('Test question', 'Test response', 0.95);

SELECT * FROM chatbot_queries ORDER BY created_at DESC LIMIT 5;
```

## 🚨 Troubleshooting

### Connection Issues
- Verify Railway database is running
- Check connection string format
- Ensure SSL mode if required: `?sslmode=require`

### Permission Issues  
- Some managed PostgreSQL instances restrict extensions
- Use simple keyword search if pgvector unavailable
- Contact Railway support for extension requests

### Performance Issues
- Ensure indexes are created (included in schema)
- Monitor query performance with `EXPLAIN ANALYZE`
- Consider connection pooling for production

## 📈 Monitoring

### Health Check
```sql
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes
FROM pg_stat_user_tables 
WHERE schemaname = 'public';
```

### Storage Usage
```sql
SELECT 
    relname as table_name,
    pg_size_pretty(pg_total_relation_size(relid)) as size
FROM pg_catalog.pg_statio_user_tables 
ORDER BY pg_total_relation_size(relid) DESC;
```

Ready for next phase: Knowledge Base Setup! 🎯