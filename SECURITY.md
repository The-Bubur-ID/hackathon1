# 🔒 Security Guidelines

## ⚠️ IMPORTANT: Credential Security

### 🚨 Before Pushing to Git

**NEVER commit these files:**
- `.env` (actual environment variables)
- `.claude/settings.local.json` (contains real DB credentials)
- Any file containing real API keys, passwords, or connection strings

### 🔧 Setup Process

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

2. **Use placeholders in documentation:**
   - `DATABASE_URL="postgresql://username:password@host:port/database"`
   - `OPENAI_API_KEY="sk-your-openai-api-key-here"`
   - `GITHUB_TOKEN="ghp_your-github-token-here"`

3. **Verify before commit:**
   ```bash
   # Check for exposed credentials
   grep -r "postgresql://.*@" --exclude-dir=.git --exclude=.env
   grep -r "sk-proj-" --exclude-dir=.git --exclude=.env
   ```

## 🛡️ Security Best Practices

### 🗄️ Database Security
- Use Railway's connection string rotation feature
- Never hardcode credentials in source code
- Use environment variables for all sensitive data

### 🔑 API Key Management
- Store API keys in `.env` file (not committed)
- Use minimal permissions for GitHub tokens
- Rotate keys regularly

### 📝 Documentation Security
- Use placeholder values in all documentation
- Include security warnings in setup guides
- Provide .env.example with safe defaults

### 🧪 Testing Security
- Use mock data for testing when possible
- Avoid using production credentials in test scripts
- Clean up test data containing sensitive information

## 🚨 Incident Response

### If Credentials Are Exposed

1. **Immediate Action:**
   ```bash
   # Remove from git history if needed
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch path/to/sensitive/file' --prune-empty --tag-name-filter cat -- --all
   ```

2. **Rotate Credentials:**
   - Railway: Generate new database password
   - OpenAI: Rotate API key
   - GitHub: Generate new personal access token

3. **Update Documentation:**
   - Replace exposed values with placeholders
   - Add to .gitignore
   - Update security guidelines

## ✅ Security Checklist

Before pushing code:

- [ ] `.env` file is not committed
- [ ] `.claude/settings.local.json` is in .gitignore
- [ ] No real credentials in documentation
- [ ] All examples use placeholder values
- [ ] .gitignore includes sensitive file patterns
- [ ] Security guidelines are documented

## 🔍 Credential Patterns to Avoid

```bash
# ❌ NEVER commit these patterns:
postgresql://.*:.*@.*\.railway\.app
sk-proj-[A-Za-z0-9]{48}
ghp_[A-Za-z0-9]{36}
```

## 📞 Contact

For security concerns, contact the development team immediately.

---

**Remember: Security is everyone's responsibility!** 🛡️