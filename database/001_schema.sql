-- PCI DSS Compliance Automation - Database Schema
-- Version: Hackathon MVP
-- Date: 2025-10-25

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Core findings table from Snyk + AI analysis
CREATE TABLE findings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    finding_id VARCHAR(255) UNIQUE NOT NULL,
    repo_name VARCHAR(255) NOT NULL,
    severity VARCHAR(50) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    title VARCHAR(500),
    description TEXT,
    fix_suggestion TEXT,  -- AI generated fix
    affected_file VARCHAR(500),
    line_number INTEGER,
    cwe_id VARCHAR(50),
    pci_requirement VARCHAR(50),  -- AI mapped requirement
    risk_score INTEGER CHECK (risk_score BETWEEN 1 AND 10),
    status VARCHAR(50) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'verified')),
    github_issue_url TEXT,
    clickup_task_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Evidence packages for compliance audit
CREATE TABLE evidence_packages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    finding_id VARCHAR(255) REFERENCES findings(finding_id) ON DELETE CASCADE,
    evidence_document TEXT,  -- Markdown format
    compliance_metadata JSONB,
    verification_status VARCHAR(50) DEFAULT 'pending' CHECK (verification_status IN ('pending', 'reviewed', 'approved')),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Knowledge base for ChatBot (simple keyword approach)
CREATE TABLE knowledge_simple (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500),
    content TEXT,
    doc_type VARCHAR(100),  -- 'policy', 'compliance_doc', 'evidence'
    keywords TEXT[],
    source_type VARCHAR(100) DEFAULT 'manual',  -- 'manual', 'evidence_package', 'document'
    created_at TIMESTAMP DEFAULT NOW()
);

-- ChatBot query audit trail
CREATE TABLE chatbot_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_query TEXT,
    bot_response TEXT,
    sources_used JSONB,
    confidence_score DECIMAL(3,2),
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Workflow execution logs
CREATE TABLE workflow_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_name VARCHAR(255),
    execution_id VARCHAR(255),
    status VARCHAR(50) CHECK (status IN ('success', 'failed', 'partial')),
    error_message TEXT,
    duration_ms INTEGER,
    findings_processed INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_findings_severity ON findings(severity);
CREATE INDEX idx_findings_repo ON findings(repo_name);
CREATE INDEX idx_findings_status ON findings(status);
CREATE INDEX idx_findings_created ON findings(created_at DESC);

CREATE INDEX idx_evidence_finding ON evidence_packages(finding_id);
CREATE INDEX idx_evidence_status ON evidence_packages(verification_status);

CREATE INDEX idx_knowledge_keywords ON knowledge_simple USING GIN(keywords);
CREATE INDEX idx_knowledge_content ON knowledge_simple USING gin(to_tsvector('english', content));
CREATE INDEX idx_knowledge_type ON knowledge_simple(doc_type);

CREATE INDEX idx_chatbot_created ON chatbot_queries(created_at DESC);

CREATE INDEX idx_workflow_name ON workflow_logs(workflow_name);
CREATE INDEX idx_workflow_status ON workflow_logs(status);

-- Auto-update timestamps trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_findings_updated_at 
    BEFORE UPDATE ON findings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View for compliance summary
CREATE VIEW compliance_summary AS
SELECT 
    f.pci_requirement,
    COUNT(*) as total_findings,
    COUNT(CASE WHEN f.severity = 'critical' THEN 1 END) as critical_count,
    COUNT(CASE WHEN f.severity = 'high' THEN 1 END) as high_count,
    COUNT(CASE WHEN f.severity = 'medium' THEN 1 END) as medium_count,
    COUNT(CASE WHEN f.severity = 'low' THEN 1 END) as low_count,
    COUNT(CASE WHEN f.status = 'verified' THEN 1 END) as resolved_count,
    ROUND(COUNT(CASE WHEN f.status = 'verified' THEN 1 END)::NUMERIC / COUNT(*)::NUMERIC * 100, 2) as resolution_rate,
    COUNT(CASE WHEN ep.verification_status = 'approved' THEN 1 END) as approved_evidence_count
FROM findings f
LEFT JOIN evidence_packages ep ON f.finding_id = ep.finding_id
WHERE f.created_at >= NOW() - INTERVAL '30 days'  -- Last 30 days
GROUP BY f.pci_requirement
ORDER BY total_findings DESC;

-- Insert initial knowledge base data
INSERT INTO knowledge_simple (title, content, doc_type, keywords, source_type) VALUES
('PCI DSS Requirement 6.5.1 - SQL Injection Protection', 
 'All web-facing applications must be protected against SQL injection attacks. This includes using parameterized queries, stored procedures with type-safe parameters, or proper escaping of all user-supplied input. SQL injection vulnerabilities can allow attackers to access, modify, or delete data from the database.',
 'compliance_doc',
 ARRAY['sql injection', 'pci dss', '6.5.1', 'parameterized queries', 'web application', 'database security', 'input validation'],
 'manual'),

('PCI DSS Requirement 6.5.7 - Cross-Site Scripting Prevention',
 'All web applications must be protected against cross-site scripting (XSS) attacks. This requires proper validation of all input parameters and encoding of output. XSS vulnerabilities allow attackers to execute malicious scripts in users browsers.',
 'compliance_doc', 
 ARRAY['xss', 'cross-site scripting', '6.5.7', 'input validation', 'output encoding', 'web security'],
 'manual'),

('PCI DSS Requirement 6.3.2 - Secure Code Review Process',
 'All custom application code must be reviewed by individuals other than the code author prior to release to production or customers. Code reviews must specifically address common coding vulnerabilities and ensure adherence to secure coding guidelines.',
 'compliance_doc',
 ARRAY['code review', 'security', 'application', 'vulnerabilities', 'production', 'secure coding'],
 'manual'),

('SQL Injection Prevention Best Practices',
 'Use prepared statements with parameterized queries. Example: SELECT * FROM users WHERE id = ? instead of SELECT * FROM users WHERE id = + userId. Always validate and sanitize user input. Use stored procedures with type-safe parameters where possible.',
 'policy',
 ARRAY['sql injection', 'prepared statements', 'parameterized queries', 'input validation', 'best practices'],
 'manual'),

('XSS Prevention Techniques',
 'Implement proper output encoding using libraries like DOMPurify for JavaScript or similar for other languages. Validate all input on both client and server side. Use Content Security Policy (CSP) headers to prevent script execution.',
 'policy',
 ARRAY['xss prevention', 'output encoding', 'input validation', 'csp', 'dompurify', 'security headers'],
 'manual');

-- Test data for demo
INSERT INTO findings (finding_id, repo_name, severity, title, description, fix_suggestion, affected_file, line_number, cwe_id, pci_requirement, risk_score, status) VALUES
('DEMO-001', 'payment-gateway', 'critical', 'SQL Injection in Payment Controller', 'User input directly concatenated into SQL query without sanitization', 'Use parameterized queries: SELECT * FROM payments WHERE id = ?', 'src/controllers/payment.controller.js', 145, 'CWE-89', '6.5.1', 9, 'open'),
('DEMO-002', 'merchant-api', 'high', 'Cross-Site Scripting in Error Handler', 'User input reflected in error messages without proper HTML encoding', 'Implement output encoding: const cleanHtml = DOMPurify.sanitize(userInput);', 'src/middleware/error.handler.js', 67, 'CWE-79', '6.5.7', 7, 'open');

-- Test evidence packages
INSERT INTO evidence_packages (finding_id, evidence_document, compliance_metadata) VALUES
('DEMO-001', '# Security Finding Evidence Package

**Finding ID:** DEMO-001
**Severity:** Critical
**PCI Requirement:** 6.5.1

## Vulnerability Details
- **Repository:** payment-gateway
- **File:** src/controllers/payment.controller.js:145
- **CWE:** CWE-89

## Description
User input directly concatenated into SQL query without sanitization

## Recommended Fix
Use parameterized queries: SELECT * FROM payments WHERE id = ?

## Timeline
- **Discovered:** 2025-10-25T10:00:00Z
- **Status:** Open
- **Priority:** Critical

---
Generated by DOKU Compliance Automation', 
'{"repo": "payment-gateway", "severity": "critical", "pci_requirement": "6.5.1", "scan_tool": "mock", "created_by": "demo"}');

-- Add evidence to knowledge base
INSERT INTO knowledge_simple (title, content, doc_type, keywords, source_type) VALUES
('Critical Finding: SQL Injection in Payment Gateway',
 'SQL injection vulnerability found in payment-gateway repository at src/controllers/payment.controller.js line 145. User input directly concatenated into SQL query without sanitization. Fix: Use parameterized queries: SELECT * FROM payments WHERE id = ?',
 'evidence',
 ARRAY['sql injection', 'payment gateway', 'critical', 'cwe-89', 'parameterized queries'],
 'evidence_package');