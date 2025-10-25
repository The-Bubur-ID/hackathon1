# 🛡️ PCI DSS Compliance Automation POC

Hackathon project untuk automasi PCI DSS Requirement 6 dengan ChatBot RAG.

## 📁 Project Structure

```
hackaton1/
├── 📋 DOCUMENTATION
│   ├── Implementation-Steps-Simplified.md    # ✅ MAIN GUIDE (hackathon scope)
│   ├── SETUP_GUIDE.md                       # ✅ Complete setup instructions
│   └── review-dari-codex.md                 # Codex review (reference)
│
├── 🗄️ DATABASE
│   ├── database/001_schema.sql              # PostgreSQL schema
│   └── database/README.md                   # Database documentation
│
├── 📚 KNOWLEDGE BASE
│   ├── knowledge_base/compliance/           # PCI DSS docs
│   └── knowledge_base/policies/             # Internal policies
│
├── ⚙️ N8N WORKFLOWS (Ready to import)
│   ├── n8n-workflows/pci-automation-workflow.json    # PCI Req 6 automation
│   └── n8n-workflows/chatbot-rag-workflow.json       # ChatBot with RAG
│
└── 🧪 SCRIPTS (Local deployment tools)
    ├── scripts/ingest_knowledge_base.py      # Knowledge base setup
    ├── scripts/setup_knowledge_base.sh       # One-command setup
    ├── scripts/test_poc.py                   # Comprehensive testing
    ├── scripts/demo_quick_test.py            # Demo presentation
    └── scripts/requirements.txt              # Python dependencies
```

## 🎯 Quick Start (15 minutes)

1. **Setup Database:** Import `database/001_schema.sql` to Railway PostgreSQL
2. **Setup Knowledge Base:** Run `scripts/setup_knowledge_base.sh`
3. **Import Workflows:** Import JSON files to n8n instance
4. **Test Everything:** Run `scripts/test_poc.py`
5. **Demo Ready:** Use `scripts/demo_quick_test.py`

## 📖 Documentation Guide

- **START HERE:** `Implementation-Steps-Simplified.md` - Hackathon implementation guide
- **SETUP:** `SETUP_GUIDE.md` - Complete deployment instructions  
- **REVIEW:** `review-dari-codex.md` - Code review findings (reference)

## 🚀 Core Features

✅ **PCI Requirement 6 Automation** - Mock security scan → AI analysis → GitHub issues  
✅ **Compliance ChatBot** - RAG-powered assistant with internal docs  
✅ **Evidence Packages** - Audit-ready documentation generation  
✅ **PostgreSQL Integration** - Full-text search knowledge base  

---

**⚡ Ready for hackathon demo in under 1 hour!**