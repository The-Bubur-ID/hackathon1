# Secure Coding Guidelines

## Overview
This document outlines secure coding practices that must be followed by all development teams to ensure compliance with PCI DSS requirements and maintain application security.

## SQL Injection Prevention

### Requirements
- **NEVER** concatenate user input directly into SQL queries
- **ALWAYS** use parameterized queries or prepared statements
- **VALIDATE** all input on both client and server side
- **SANITIZE** input using appropriate libraries

### Examples

#### ❌ Vulnerable Code
```javascript
const query = `SELECT * FROM users WHERE id = ${userId}`;
const result = await db.query(query);
```

#### ✅ Secure Code
```javascript
const query = 'SELECT * FROM users WHERE id = ?';
const result = await db.query(query, [userId]);
```

### Frameworks and Libraries
- **Node.js**: Use parameterized queries with mysql2, pg, or similar
- **Python**: Use SQLAlchemy or parameterized queries with psycopg2
- **Java**: Use PreparedStatement, never Statement with concatenation
- **C#**: Use SqlParameter with SqlCommand

## Cross-Site Scripting (XSS) Prevention

### Requirements
- **ENCODE** all output that includes user data
- **VALIDATE** input on both client and server side
- **SANITIZE** HTML content using trusted libraries
- **IMPLEMENT** Content Security Policy (CSP) headers

### Examples

#### ❌ Vulnerable Code
```javascript
document.getElementById('welcome').innerHTML = 'Hello ' + userName;
```

#### ✅ Secure Code
```javascript
document.getElementById('welcome').textContent = 'Hello ' + userName;
// OR use DOMPurify for HTML content
const clean = DOMPurify.sanitize(htmlContent);
document.getElementById('content').innerHTML = clean;
```

### Libraries for XSS Prevention
- **JavaScript**: DOMPurify, js-xss
- **Python**: bleach, MarkupSafe
- **Java**: OWASP Java Encoder
- **C#**: Microsoft.Security.Application

## Input Validation

### General Principles
1. **Whitelist validation** (preferred) - only allow known good input
2. **Blacklist validation** - block known bad input (less secure)
3. **Length validation** - enforce maximum input lengths
4. **Type validation** - ensure input matches expected data type
5. **Format validation** - use regex for structured data (email, phone, etc.)

### Examples
```javascript
// Email validation
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(email)) {
    throw new Error('Invalid email format');
}

// Numeric validation
const id = parseInt(userInput, 10);
if (isNaN(id) || id < 1 || id > 999999) {
    throw new Error('Invalid ID');
}

// String length validation
if (username.length < 3 || username.length > 50) {
    throw new Error('Username must be 3-50 characters');
}
```

## Authentication and Session Management

### Requirements
- **USE** strong session tokens (cryptographically random)
- **IMPLEMENT** proper session timeout
- **REGENERATE** session ID after login
- **SECURE** session cookies (HttpOnly, Secure, SameSite)
- **HASH** passwords using bcrypt or similar with salt

### Examples
```javascript
// Secure session configuration
app.use(session({
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: true,      // HTTPS only
        httpOnly: true,    // No client-side access
        maxAge: 1800000,   // 30 minutes
        sameSite: 'strict' // CSRF protection
    }
}));

// Password hashing
const bcrypt = require('bcrypt');
const saltRounds = 12;
const hashedPassword = await bcrypt.hash(password, saltRounds);
```

## Error Handling

### Requirements
- **NEVER** expose system information in error messages
- **LOG** security events for monitoring
- **RETURN** generic error messages to users
- **IMPLEMENT** proper logging with correlation IDs

### Examples
#### ❌ Vulnerable Error Handling
```javascript
catch (error) {
    res.status(500).json({ error: error.message }); // Exposes internal details
}
```

#### ✅ Secure Error Handling
```javascript
catch (error) {
    logger.error('Database query failed', { 
        correlationId: req.correlationId,
        error: error.message,
        stack: error.stack 
    });
    res.status(500).json({ 
        error: 'Internal server error',
        correlationId: req.correlationId 
    });
}
```

## Code Review Requirements

### Mandatory Checks
1. **Security vulnerabilities** (OWASP Top 10)
2. **Input validation** implementation
3. **Authentication and authorization** logic
4. **Sensitive data handling**
5. **Error handling** patterns
6. **Dependency security** (known vulnerabilities)

### Review Process
- **TWO-PERSON** rule: all code reviewed by someone other than author
- **SECURITY-FOCUSED** reviewer for security-critical code
- **AUTOMATED SCANNING** with SAST tools (Snyk, SonarQube)
- **DOCUMENTATION** of review decisions

## Compliance References
- PCI DSS Requirement 6.5.1 (SQL Injection)
- PCI DSS Requirement 6.5.7 (Cross-site scripting)
- PCI DSS Requirement 6.3.2 (Code review)
- OWASP Top 10 2021
- NIST Secure Software Development Framework (SSDF)