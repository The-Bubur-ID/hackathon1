#!/bin/bash
# Knowledge Base Setup Script
# Run this after database setup

set -e

echo "🚀 Setting up Knowledge Base for PCI DSS Compliance POC"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "scripts/ingest_knowledge_base.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check for environment variables
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL environment variable not set"
    echo "💡 Please set it first: export DATABASE_URL='your-railway-connection-string'"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r scripts/requirements.txt

# Check database connection
echo "🔌 Testing database connection..."
python3 -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
    cur = conn.cursor()
    cur.execute('SELECT version()')
    version = cur.fetchone()[0]
    print(f'✅ Connected to: {version}')
    cur.close()
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Run knowledge base ingestion
echo "📚 Running knowledge base ingestion..."
python3 scripts/ingest_knowledge_base.py

# Verify ingestion
echo "🔍 Verifying knowledge base content..."
python3 -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
    cur = conn.cursor()
    
    # Check knowledge_simple table
    cur.execute('SELECT doc_type, COUNT(*) FROM knowledge_simple GROUP BY doc_type ORDER BY doc_type')
    results = cur.fetchall()
    
    print('📊 Knowledge Base Contents:')
    total = 0
    for doc_type, count in results:
        print(f'   • {doc_type}: {count} chunks')
        total += count
    
    print(f'   📈 Total: {total} knowledge chunks')
    
    # Test search functionality
    cur.execute(\"\"\"
        SELECT title FROM knowledge_simple 
        WHERE content ILIKE '%sql injection%' 
        LIMIT 3
    \"\"\")
    search_results = cur.fetchall()
    
    print(f'🔍 Test search \"sql injection\": {len(search_results)} results')
    for result in search_results:
        print(f'   - {result[0][:60]}...')
    
    cur.close()
    conn.close()
    
    if total > 0:
        print('✅ Knowledge base setup completed successfully!')
    else:
        print('⚠️  Knowledge base is empty - check for errors above')
        
except Exception as e:
    print(f'❌ Verification failed: {e}')
"

echo ""
echo "🎯 Next steps:"
echo "   1. Verify knowledge base content in Railway dashboard"
echo "   2. Test knowledge search queries"
echo "   3. Build n8n workflows"
echo ""
echo "📋 Quick test queries:"
echo "   SELECT doc_type, count(*) FROM knowledge_simple GROUP BY doc_type;"
echo "   SELECT title FROM knowledge_simple WHERE content ILIKE '%pci%' LIMIT 5;"
echo ""
echo "🚀 Ready for n8n workflow setup!"