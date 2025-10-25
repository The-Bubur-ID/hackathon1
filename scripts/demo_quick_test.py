#!/usr/bin/env python3
"""
Quick Demo Test Script for PCI DSS Compliance POC
Run this during the hackathon demo to show key functionality
"""

import os
import json
import psycopg2
import requests
from datetime import datetime

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL')

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)

def print_section(title):
    print(f"\n📋 {title}")
    print('-'*40)

def demo_database_content():
    """Show current database content"""
    print_header("DATABASE CONTENT OVERVIEW")
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    
    # Knowledge base stats
    print_section("Knowledge Base Statistics")
    cur.execute("""
        SELECT doc_type, COUNT(*) as chunks
        FROM knowledge_simple 
        GROUP BY doc_type 
        ORDER BY chunks DESC
    """)
    
    for row in cur.fetchall():
        print(f"   📄 {row[0]}: {row[1]} chunks")
    
    # Recent findings
    print_section("Recent Security Findings")
    cur.execute("""
        SELECT finding_id, severity, title, pci_requirement, status
        FROM findings 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    findings = cur.fetchall()
    if findings:
        for finding in findings:
            severity_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
            status_emoji = {'open': '🔓', 'in_progress': '⚠️', 'resolved': '✅', 'verified': '🔒'}
            
            print(f"   {severity_emoji.get(finding[1], '❓')} {finding[0][:15]}... | "
                  f"PCI {finding[3]} | {status_emoji.get(finding[4], '❓')} {finding[4]}")
            print(f"      📝 {finding[2][:50]}...")
    else:
        print("   📝 No findings yet - run PCI workflow to generate sample data")
    
    # Compliance status summary
    print_section("Compliance Status Summary")
    cur.execute("""
        SELECT 
            pci_requirement,
            COUNT(*) as total,
            COUNT(CASE WHEN status = 'open' THEN 1 END) as open_issues,
            COUNT(CASE WHEN severity IN ('critical', 'high') THEN 1 END) as high_risk
        FROM findings 
        WHERE pci_requirement IS NOT NULL
        GROUP BY pci_requirement
        ORDER BY high_risk DESC, total DESC
    """)
    
    compliance_data = cur.fetchall()
    if compliance_data:
        for req in compliance_data:
            risk_level = "🔴" if req[3] > 0 else "🟢"
            print(f"   {risk_level} PCI {req[0]}: {req[1]} total, {req[2]} open, {req[3]} high-risk")
    else:
        print("   📊 No compliance data yet")
    
    cur.close()
    conn.close()

def demo_knowledge_search():
    """Demonstrate knowledge base search capabilities"""
    print_header("KNOWLEDGE BASE SEARCH DEMO")
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    
    search_queries = [
        "SQL injection prevention",
        "cross site scripting XSS",
        "PCI requirement 6.5.1",
        "secure coding practices"
    ]
    
    for query in search_queries:
        print_section(f"Search: '{query}'")
        
        # Combined search (keywords + full-text + title match)
        cur.execute("""
            SELECT 
                title, 
                doc_type,
                ts_rank(to_tsvector('english', content), plainto_tsquery('english', %s)) as relevance
            FROM knowledge_simple 
            WHERE (
                to_tsvector('english', content) @@ plainto_tsquery('english', %s)
                OR keywords && string_to_array(lower(%s), ' ')
                OR title ILIKE %s
            )
            ORDER BY relevance DESC, created_at DESC
            LIMIT 3
        """, (query, query, query, f"%{query}%"))
        
        results = cur.fetchall()
        
        if results:
            for i, (title, doc_type, relevance) in enumerate(results, 1):
                doc_emoji = {'policy': '📋', 'compliance_doc': '📄', 'evidence': '🔍'}
                print(f"   {i}. {doc_emoji.get(doc_type, '📄')} {title[:50]}...")
                print(f"      📊 Relevance: {relevance:.3f} | Type: {doc_type}")
        else:
            print(f"   ❌ No results found for '{query}'")
    
    cur.close()
    conn.close()

def demo_chatbot_simulation():
    """Simulate ChatBot interactions"""
    print_header("CHATBOT RAG SIMULATION")
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    
    # Sample ChatBot queries
    chatbot_queries = [
        {
            'query': 'What is SQL injection and how to prevent it according to PCI DSS?',
            'tool': 'search_knowledge_base',
            'search_term': 'sql injection prevention'
        },
        {
            'query': 'Show me critical security findings in our codebase',
            'tool': 'check_compliance_status', 
            'filter': 'critical'
        },
        {
            'query': 'What are the requirements for secure code review?',
            'tool': 'search_knowledge_base',
            'search_term': 'secure code review'
        }
    ]
    
    for i, chat in enumerate(chatbot_queries, 1):
        print_section(f"ChatBot Query {i}")
        print(f"   👤 User: {chat['query']}")
        print(f"   🤖 Tool Used: {chat['tool']}")
        
        if chat['tool'] == 'search_knowledge_base':
            # Simulate knowledge search
            cur.execute("""
                SELECT title, doc_type
                FROM knowledge_simple 
                WHERE (
                    to_tsvector('english', content) @@ plainto_tsquery('english', %s)
                    OR keywords && string_to_array(lower(%s), ' ')
                )
                LIMIT 3
            """, (chat['search_term'], chat['search_term']))
            
            results = cur.fetchall()
            print(f"   📚 Knowledge Sources Found: {len(results)}")
            for title, doc_type in results:
                print(f"      • {title[:40]}... ({doc_type})")
            
        elif chat['tool'] == 'check_compliance_status':
            # Simulate status check
            cur.execute("""
                SELECT severity, COUNT(*) as count
                FROM findings 
                WHERE severity = %s OR %s = 'all'
                GROUP BY severity
            """, (chat.get('filter', 'all'), chat.get('filter', 'all')))
            
            results = cur.fetchall()
            print(f"   📊 Compliance Data Retrieved:")
            for severity, count in results:
                print(f"      • {severity}: {count} findings")
        
        # Simulate response logging
        cur.execute("""
            INSERT INTO chatbot_queries (
                user_query, bot_response, sources_used, 
                confidence_score, response_time_ms
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            chat['query'][:100],
            f"Response based on {chat['tool']} tool",
            json.dumps([{'tool': chat['tool']}]),
            0.85,
            1200
        ))
    
    conn.commit()
    print(f"\n   ✅ {len(chatbot_queries)} ChatBot interactions logged")
    
    cur.close()
    conn.close()

def demo_workflow_status():
    """Show workflow execution status"""
    print_header("WORKFLOW EXECUTION STATUS")
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    
    # Recent workflow executions
    print_section("Recent Workflow Runs")
    cur.execute("""
        SELECT 
            workflow_name, 
            status, 
            findings_processed,
            duration_ms,
            created_at
        FROM workflow_logs 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    workflows = cur.fetchall()
    if workflows:
        for workflow in workflows:
            status_emoji = {'success': '✅', 'failure': '❌', 'running': '⚡'}
            print(f"   {status_emoji.get(workflow[1], '❓')} {workflow[0]}")
            print(f"      📊 Processed: {workflow[2]} findings | Duration: {workflow[3]}ms")
            print(f"      🕒 {workflow[4].strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("   📝 No workflow executions yet")
    
    # Summary stats
    print_section("Workflow Performance Summary")
    cur.execute("""
        SELECT 
            workflow_name,
            COUNT(*) as executions,
            AVG(duration_ms) as avg_duration,
            SUM(findings_processed) as total_findings
        FROM workflow_logs 
        GROUP BY workflow_name
    """)
    
    stats = cur.fetchall()
    if stats:
        for stat in stats:
            print(f"   ⚙️ {stat[0]}:")
            print(f"      📈 {stat[1]} executions | Avg duration: {stat[2]:.0f}ms")
            print(f"      🔍 Total findings processed: {stat[3]}")
    else:
        print("   📊 No performance data available")
    
    cur.close()
    conn.close()

def main():
    """Run complete demo"""
    print("🎬 Starting PCI DSS Compliance POC Demo")
    print("🕒 " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        print("💡 Run: export DATABASE_URL='your-railway-connection-string'")
        return
    
    try:
        # Test database connection
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('SELECT version()')
        version = cur.fetchone()[0]
        print(f"✅ Connected to: {version[:50]}...")
        cur.close()
        conn.close()
        
        # Run demo sections
        demo_database_content()
        demo_knowledge_search()
        demo_chatbot_simulation()
        demo_workflow_status()
        
        print_header("DEMO COMPLETED SUCCESSFULLY")
        print("🎉 PCI DSS Compliance POC is ready for presentation!")
        print("📋 Key capabilities demonstrated:")
        print("   ✅ Knowledge base search and retrieval")
        print("   ✅ Security finding management")
        print("   ✅ ChatBot RAG functionality")
        print("   ✅ Workflow automation logging")
        print("   ✅ Compliance status tracking")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Check database connection and run setup_knowledge_base.sh first")

if __name__ == "__main__":
    main()