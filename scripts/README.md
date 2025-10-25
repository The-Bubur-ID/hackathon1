# 🧪 Scripts Documentation

Scripts untuk setup, testing, dan demo PCI DSS Compliance POC.

## 📋 Script Overview

| Script | Purpose | Run Where | Duration |
|--------|---------|-----------|----------|
| `setup_knowledge_base.sh` | Setup knowledge base | **Local machine** | 2 min |
| `ingest_knowledge_base.py` | Ingest docs to database | **Local machine** | 1 min |
| `test_poc.py` | Comprehensive testing | **Local machine** | 30 sec |
| `demo_quick_test.py` | Demo presentation | **Local machine** | 10 sec |

## 🖥️ **Run Location: LOCAL MACHINE**

**Semua scripts dijalankan di laptop/komputer tim hackathon**, bukan di server/cloud.

### Prerequisites (Install Once)
```bash
# Install Python dependencies
pip install -r scripts/requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@host:port/db"  # Railway connection
export OPENAI_API_KEY="sk-..."  # Optional for vector mode
```

## 📚 1. **setup_knowledge_base.sh** 
**Purpose:** One-command setup knowledge base

```bash
# Run from project root
chmod +x scripts/setup_knowledge_base.sh
./scripts/setup_knowledge_base.sh
```

**What it does:**
- ✅ Tests database connection
- ✅ Installs Python dependencies  
- ✅ Runs knowledge base ingestion
- ✅ Verifies data was loaded correctly

**Expected output:**
```
🚀 Setting up Knowledge Base for PCI DSS Compliance POC
✅ Connected to: PostgreSQL 14.x
📚 Running knowledge base ingestion...
✅ Successfully ingested: 12 chunks from PCI DSS
📊 Total: 12 knowledge chunks
🚀 Ready for n8n workflow setup!
```

## 🐍 2. **ingest_knowledge_base.py**
**Purpose:** Load compliance docs into PostgreSQL

```bash
python3 scripts/ingest_knowledge_base.py
```

**What it does:**
- 📄 Reads markdown files from `knowledge_base/`
- ✂️ Chunks documents into searchable pieces
- 🔤 Extracts keywords for search
- 💾 Stores in `knowledge_simple` table
- 🔍 Enables full-text search

**Database changes:**
- Populates `knowledge_simple` table
- Creates searchable chunks from compliance docs

## 🧪 3. **test_poc.py**
**Purpose:** Comprehensive system testing

```bash
python3 scripts/test_poc.py
```

**What it does:**
- 🔌 Tests database connection
- 📊 Validates schema exists
- 🔍 Tests knowledge base search
- ⚙️ Simulates workflow execution
- 🤖 Tests ChatBot functionality

**Expected output:**
```
🧪 TEST RESULTS SUMMARY
✅ DATABASE: PASS (3/3 tests)
✅ KNOWLEDGE BASE: PASS (3/3 tests) 
✅ PCI WORKFLOW: PASS (3/3 tests)
✅ CHATBOT WORKFLOW: PASS (3/3 tests)
📈 OVERALL: 12/12 tests passed
🎉 POC is ready for demo!
```

## 🎬 4. **demo_quick_test.py**
**Purpose:** Live demo presentation

```bash
python3 scripts/demo_quick_test.py
```

**What it shows:**
- 📊 Current database content
- 🔍 Knowledge search examples
- 🤖 ChatBot interaction simulation
- ⚙️ Workflow execution status

**Perfect for hackathon presentation!**

## ⚠️ Important Notes

### **Network Requirements**
- 🌐 Internet connection (for Railway database)
- 🔗 Railway PostgreSQL accessible
- 🔑 Valid DATABASE_URL

### **NOT Required**
- ❌ Server deployment
- ❌ Cloud hosting  
- ❌ Container orchestration
- ❌ CI/CD pipelines

### **Troubleshooting**

**Connection Failed:**
```bash
# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql://user:pass@host:port/db

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

**Knowledge Base Empty:**
```bash
# Check files exist
ls -la knowledge_base/compliance/
# Re-run ingestion
python3 scripts/ingest_knowledge_base.py
```

**Tests Failing:**
```bash
# Check database schema
psql $DATABASE_URL -c "\dt"
# Should show: findings, evidence_packages, knowledge_simple, etc.
```

## 🎯 Deployment Flow

```mermaid
graph LR
    A[Local Laptop] --> B[Railway PostgreSQL]
    A --> C[n8n Cloud/Self-hosted]
    B --> D[Knowledge Base]
    C --> E[Workflows]
    A --> F[Testing & Demo]
```

**Tim hackathon hanya perlu:**
1. Laptop dengan Python
2. Railway database credentials  
3. n8n instance access
4. Run scripts locally untuk setup & testing

**Semua scripts adalah tools untuk tim, bukan untuk production deployment.**