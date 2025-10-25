#!/usr/bin/env python3
"""
PCI DSS Compliance POC Testing Script
Tests both n8n workflows and database integration
"""

import os
import json
import psycopg2
import requests
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL')
N8N_WEBHOOK_BASE = os.getenv('N8N_WEBHOOK_BASE', 'https://your-n8n-instance.com/webhook')

class POCTester:
    def __init__(self):
        self.db_conn = None
        self.test_results = {
            'database': {'status': 'pending', 'tests': []},
            'knowledge_base': {'status': 'pending', 'tests': []},
            'pci_workflow': {'status': 'pending', 'tests': []},
            'chatbot_workflow': {'status': 'pending', 'tests': []}
        }
    
    def connect_database(self) -> bool:
        """Test database connection"""
        try:
            if not DATABASE_URL:
                raise Exception("DATABASE_URL environment variable not set")
            
            self.db_conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            
            # Test basic connection
            cur = self.db_conn.cursor()
            cur.execute('SELECT version()')
            version = cur.fetchone()[0]
            
            self.test_results['database']['tests'].append({
                'name': 'Database Connection',
                'status': 'pass',
                'details': f'Connected to: {version[:50]}...'
            })
            
            cur.close()
            return True
            
        except Exception as e:
            self.test_results['database']['tests'].append({
                'name': 'Database Connection',
                'status': 'fail',
                'details': str(e)
            })
            return False
    
    def test_database_schema(self) -> bool:
        """Test database schema and tables"""
        try:
            cur = self.db_conn.cursor()
            
            # Check required tables exist
            required_tables = [
                'findings', 'evidence_packages', 'knowledge_simple', 
                'chatbot_queries', 'workflow_logs'
            ]
            
            for table in required_tables:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    )
                """, (table,))
                
                exists = cur.fetchone()[0]
                if not exists:
                    raise Exception(f"Table {table} does not exist")
            
            self.test_results['database']['tests'].append({
                'name': 'Schema Validation',
                'status': 'pass',
                'details': f'All {len(required_tables)} required tables exist'
            })
            
            # Test sample data
            cur.execute('SELECT COUNT(*) FROM knowledge_simple')
            knowledge_count = cur.fetchone()[0]
            
            self.test_results['database']['tests'].append({
                'name': 'Sample Data Check',
                'status': 'pass' if knowledge_count > 0 else 'warning',
                'details': f'Knowledge base has {knowledge_count} chunks'
            })
            
            cur.close()
            self.test_results['database']['status'] = 'pass'
            return True
            
        except Exception as e:
            self.test_results['database']['tests'].append({
                'name': 'Schema Validation',
                'status': 'fail',
                'details': str(e)
            })
            self.test_results['database']['status'] = 'fail'
            return False
    
    def test_knowledge_base(self) -> bool:
        """Test knowledge base search functionality"""
        try:
            cur = self.db_conn.cursor()
            
            # Test keyword search
            cur.execute("""
                SELECT title, doc_type 
                FROM knowledge_simple 
                WHERE keywords && ARRAY['sql', 'injection']
                LIMIT 3
            """)
            
            keyword_results = cur.fetchall()
            
            self.test_results['knowledge_base']['tests'].append({
                'name': 'Keyword Search',
                'status': 'pass' if len(keyword_results) > 0 else 'warning',
                'details': f'Found {len(keyword_results)} results for SQL injection keywords'
            })
            
            # Test full-text search
            cur.execute("""
                SELECT title, ts_rank(to_tsvector('english', content), 
                                     plainto_tsquery('english', 'cross site scripting')) as rank
                FROM knowledge_simple 
                WHERE to_tsvector('english', content) @@ plainto_tsquery('english', 'cross site scripting')
                ORDER BY rank DESC
                LIMIT 3
            """)
            
            fts_results = cur.fetchall()
            
            self.test_results['knowledge_base']['tests'].append({
                'name': 'Full-Text Search',
                'status': 'pass' if len(fts_results) > 0 else 'warning',
                'details': f'Found {len(fts_results)} results for XSS search'
            })
            
            # Test document types
            cur.execute('SELECT doc_type, COUNT(*) FROM knowledge_simple GROUP BY doc_type')
            doc_types = cur.fetchall()
            
            self.test_results['knowledge_base']['tests'].append({
                'name': 'Document Types',
                'status': 'pass',
                'details': f'Document types: {dict(doc_types)}'
            })
            
            cur.close()
            self.test_results['knowledge_base']['status'] = 'pass'
            return True
            
        except Exception as e:
            self.test_results['knowledge_base']['tests'].append({
                'name': 'Knowledge Base Search',
                'status': 'fail',
                'details': str(e)
            })
            self.test_results['knowledge_base']['status'] = 'fail'
            return False
    
    def test_pci_workflow(self) -> bool:
        """Test PCI automation workflow (mock mode)"""
        try:
            # For testing, we simulate workflow execution by testing database operations
            cur = self.db_conn.cursor()
            
            # Insert test finding
            test_finding = {
                'finding_id': f'TEST-{int(datetime.now().timestamp())}',
                'repo_name': 'test-repo',
                'severity': 'high',
                'title': 'Test SQL Injection Finding',
                'description': 'Test vulnerability for POC validation',
                'fix_suggestion': 'Use parameterized queries',
                'affected_file': 'test/controller.js',
                'line_number': 42,
                'cwe_id': 'CWE-89',
                'pci_requirement': '6.5.1',
                'risk_score': 7,
                'status': 'open'
            }
            
            cur.execute("""
                INSERT INTO findings (
                    finding_id, repo_name, severity, title, description, 
                    fix_suggestion, affected_file, line_number, cwe_id, 
                    pci_requirement, risk_score, status
                ) VALUES (
                    %(finding_id)s, %(repo_name)s, %(severity)s, %(title)s, 
                    %(description)s, %(fix_suggestion)s, %(affected_file)s, 
                    %(line_number)s, %(cwe_id)s, %(pci_requirement)s, 
                    %(risk_score)s, %(status)s
                )
            """, test_finding)
            
            # Insert test evidence package
            evidence_doc = f"# Test Evidence Package\n\n**Finding:** {test_finding['finding_id']}\n**Generated:** {datetime.now().isoformat()}"
            
            cur.execute("""
                INSERT INTO evidence_packages (finding_id, evidence_document, compliance_metadata)
                VALUES (%s, %s, %s)
            """, (
                test_finding['finding_id'], 
                evidence_doc,
                json.dumps({'test': True, 'automated': True})
            ))
            
            self.db_conn.commit()
            
            self.test_results['pci_workflow']['tests'].append({
                'name': 'Finding Storage',
                'status': 'pass',
                'details': f'Successfully stored test finding {test_finding["finding_id"]}'
            })
            
            self.test_results['pci_workflow']['tests'].append({
                'name': 'Evidence Package',
                'status': 'pass',
                'details': 'Evidence document created and stored'
            })
            
            # Test workflow logging
            cur.execute("""
                INSERT INTO workflow_logs (
                    workflow_name, execution_id, status, duration_ms, 
                    findings_processed, metadata
                ) VALUES (
                    'PCI Automation Test', 'test-exec-001', 'success', 
                    2500, 1, %s
                )
            """, (json.dumps({'test_mode': True}),))
            
            self.db_conn.commit()
            
            self.test_results['pci_workflow']['tests'].append({
                'name': 'Workflow Logging',
                'status': 'pass',
                'details': 'Workflow execution logged successfully'
            })
            
            cur.close()
            self.test_results['pci_workflow']['status'] = 'pass'
            return True
            
        except Exception as e:
            if cur:
                cur.close()
            self.test_results['pci_workflow']['tests'].append({
                'name': 'PCI Workflow Test',
                'status': 'fail',
                'details': str(e)
            })
            self.test_results['pci_workflow']['status'] = 'fail'
            return False
    
    def test_chatbot_workflow(self) -> bool:
        """Test ChatBot RAG workflow functionality"""
        try:
            cur = self.db_conn.cursor()
            
            # Test knowledge search (simulating ChatBot tool calls)
            test_queries = [
                {'query': 'sql injection prevention', 'expected_results': 1},
                {'query': 'cross site scripting', 'expected_results': 1},
                {'query': 'pci requirement 6', 'expected_results': 1}
            ]
            
            for test in test_queries:
                cur.execute("""
                    SELECT title, content, doc_type 
                    FROM knowledge_simple 
                    WHERE (
                        to_tsvector('english', content) @@ plainto_tsquery('english', %s)
                        OR keywords && string_to_array(lower(%s), ' ')
                        OR title ILIKE %s
                    )
                    ORDER BY ts_rank(to_tsvector('english', content), plainto_tsquery('english', %s)) DESC
                    LIMIT 5
                """, (test['query'], test['query'], f"%{test['query']}%", test['query']))
                
                results = cur.fetchall()
                
                self.test_results['chatbot_workflow']['tests'].append({
                    'name': f'Knowledge Search: {test["query"]}',
                    'status': 'pass' if len(results) >= test['expected_results'] else 'warning',
                    'details': f'Found {len(results)} results'
                })
            
            # Test compliance status query
            cur.execute("""
                SELECT pci_requirement, COUNT(*) as total_findings,
                       COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_count,
                       COUNT(CASE WHEN status = 'open' THEN 1 END) as open_count
                FROM findings 
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY pci_requirement
                ORDER BY total_findings DESC
            """)
            
            status_results = cur.fetchall()
            
            self.test_results['chatbot_workflow']['tests'].append({
                'name': 'Compliance Status Query',
                'status': 'pass',
                'details': f'Retrieved status for {len(status_results)} PCI requirements'
            })
            
            # Test ChatBot query logging
            cur.execute("""
                INSERT INTO chatbot_queries (
                    user_query, bot_response, sources_used, 
                    confidence_score, response_time_ms
                ) VALUES (
                    'Test query: What is SQL injection?',
                    'SQL injection is a code injection technique...',
                    %s,
                    0.85,
                    1200
                )
            """, (json.dumps([{'title': 'PCI DSS Requirement 6.5.1', 'type': 'compliance_doc'}]),))
            
            self.db_conn.commit()
            
            self.test_results['chatbot_workflow']['tests'].append({
                'name': 'Query Logging',
                'status': 'pass',
                'details': 'ChatBot interaction logged successfully'
            })
            
            cur.close()
            self.test_results['chatbot_workflow']['status'] = 'pass'
            return True
            
        except Exception as e:
            if cur:
                cur.close()
            self.test_results['chatbot_workflow']['tests'].append({
                'name': 'ChatBot Workflow Test',
                'status': 'fail',
                'details': str(e)
            })
            self.test_results['chatbot_workflow']['status'] = 'fail'
            return False
    
    def run_all_tests(self) -> Dict:
        """Run complete test suite"""
        print("🧪 Starting PCI DSS Compliance POC Tests")
        print("=" * 50)
        
        # Database tests
        print("\n📊 Testing Database...")
        if self.connect_database():
            self.test_database_schema()
        
        # Knowledge base tests
        if self.db_conn:
            print("\n📚 Testing Knowledge Base...")
            self.test_knowledge_base()
            
            print("\n⚙️ Testing PCI Workflow...")
            self.test_pci_workflow()
            
            print("\n🤖 Testing ChatBot Workflow...")
            self.test_chatbot_workflow()
        
        return self.test_results
    
    def print_results(self):
        """Print formatted test results"""
        print("\n" + "=" * 60)
        print("🧪 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        overall_status = 'pass'
        total_tests = 0
        passed_tests = 0
        
        for category, data in self.test_results.items():
            status_emoji = {'pass': '✅', 'fail': '❌', 'warning': '⚠️', 'pending': '⏳'}
            
            print(f"\n{status_emoji.get(data['status'], '❓')} {category.upper().replace('_', ' ')}: {data['status'].upper()}")
            
            for test in data['tests']:
                test_emoji = status_emoji.get(test['status'], '❓')
                print(f"   {test_emoji} {test['name']}: {test['details']}")
                
                total_tests += 1
                if test['status'] == 'pass':
                    passed_tests += 1
                elif test['status'] == 'fail':
                    overall_status = 'fail'
        
        print("\n" + "=" * 60)
        print(f"📈 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
        
        if overall_status == 'pass':
            print("🎉 POC is ready for demo!")
        else:
            print("⚠️ Some issues found - please review failed tests")
        
        print("=" * 60)
    
    def cleanup(self):
        """Clean up test data and connections"""
        if self.db_conn:
            try:
                cur = self.db_conn.cursor()
                # Remove test data
                cur.execute("DELETE FROM findings WHERE finding_id LIKE 'TEST-%'")
                cur.execute("DELETE FROM evidence_packages WHERE finding_id LIKE 'TEST-%'")
                cur.execute("DELETE FROM workflow_logs WHERE workflow_name = 'PCI Automation Test'")
                self.db_conn.commit()
                cur.close()
            except Exception as e:
                print(f"⚠️ Cleanup warning: {e}")
            finally:
                self.db_conn.close()


def main():
    """Main test runner"""
    tester = POCTester()
    
    try:
        results = tester.run_all_tests()
        tester.print_results()
        
        # Export results for CI/CD
        with open('test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Detailed results saved to: test_results.json")
        
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test runner failed: {e}")
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()