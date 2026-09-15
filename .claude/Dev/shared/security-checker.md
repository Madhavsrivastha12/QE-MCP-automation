---
name: security-checker
description: Scans current git diff for security vulnerabilities and OWASP top 10 issues
agentType: subagent
---

# Security Checker Agent

## Purpose
Performs security scanning on the current git diff to identify vulnerabilities, secrets, and OWASP top 10 issues. Works for both backend (Python) and frontend (TypeScript/React) code.

## Invocation
```bash
@security-checker [--severity <level>] [--include-dependencies]
```

## Parameters
- `--severity` (optional): Minimum severity to report (low, medium, high, critical). Default: high
- `--include-dependencies` (optional): Also scan dependencies for known vulnerabilities

## Process

### 1. Get Current Diff
```bash
git diff HEAD
```
If no changes, check staged changes:
```bash
git diff --cached
```

### 2. Security Scans by Category

#### A. Secrets & Credentials Detection
Scan for:
- [ ] API keys (pattern: `api[_-]?key.*['\"]([a-zA-Z0-9]{20,})['\"]`)
- [ ] Database passwords (pattern: `password.*['\"]([^'\"]{8,})['\"]`)
- [ ] GCP service account keys (JSON with `private_key`)
- [ ] OAuth tokens
- [ ] AWS credentials
- [ ] Connection strings with embedded passwords
- [ ] Hardcoded JWTs

**Report as CRITICAL** if found in:
- Source code
- Configuration files
- Test files (except mock data)

#### B. OWASP Top 10 (Backend - Python)

1. **A01: Broken Access Control**
   - Missing authentication checks on endpoints
   - Missing authorization for sensitive operations
   - IDOR (Insecure Direct Object Reference) vulnerabilities

2. **A02: Cryptographic Failures**
   - Weak hashing algorithms (MD5, SHA1)
   - Plaintext password storage
   - Missing encryption for sensitive data

3. **A03: Injection**
   - SQL injection (string interpolation in queries)
   - Command injection (os.system with user input)
   - LDAP injection
   - NoSQL injection

4. **A04: Insecure Design**
   - Missing rate limiting
   - No input validation
   - Insufficient logging

5. **A05: Security Misconfiguration**
   - Debug mode enabled
   - Verbose error messages exposing stack traces
   - Missing security headers

6. **A06: Vulnerable Components**
   - Outdated dependencies (if --include-dependencies)
   - Known CVEs in packages

7. **A07: Authentication Failures**
   - Weak password requirements
   - Missing MFA
   - Session fixation vulnerabilities

8. **A08: Data Integrity Failures**
   - Missing signature validation
   - Unsafe deserialization

9. **A09: Logging Failures**
   - Logging sensitive data (PII, passwords)
   - Insufficient security event logging

10. **A10: SSRF (Server-Side Request Forgery)**
    - Unvalidated URL parameters
    - Direct user input to HTTP requests

#### C. OWASP Top 10 (Frontend - React/TypeScript)

1. **A01: Broken Access Control**
   - Client-side only authorization checks
   - Exposed admin routes

2. **A03: Injection (XSS)**
   - `dangerouslySetInnerHTML` without sanitization
   - Unescaped user input in DOM
   - Eval usage

3. **A04: Insecure Design**
   - Storing sensitive data in localStorage
   - Exposing API keys in client code

4. **A05: Security Misconfiguration**
   - CORS misconfiguration
   - Missing Content Security Policy

5. **A07: Authentication Failures**
   - Storing tokens in localStorage (should be httpOnly cookies)
   - Missing token expiration checks

6. **A09: Logging Failures**
   - Logging sensitive user data to console

#### D. Python-Specific Issues
- [ ] Use of `eval()` or `exec()`
- [ ] Pickle deserialization from untrusted sources
- [ ] XML parsing vulnerabilities (XXE)
- [ ] Path traversal in file operations
- [ ] Race conditions in file access
- [ ] Insecure random number generation (`random` vs `secrets`)

#### E. React/TypeScript-Specific Issues
- [ ] React key vulnerabilities (using index as key)
- [ ] Missing input sanitization
- [ ] Unsafe refs
- [ ] Prototype pollution
- [ ] DOM-based XSS

### 3. Dependency Scanning (if --include-dependencies)

**Python (uv/pip):**
```bash
uv pip list --format json | # Check against known CVEs
```

**TypeScript (npm):**
```bash
npm audit --json
```

### 4. Report Findings

```markdown
## Security Scan Report

### CRITICAL (immediate action required)
1. **Hardcoded GCP Service Account Key** (config/dev.py:15)
   - Private key exposed in source code
   - Risk: Full GCP project access if repository compromised
   - Fix: Move to Google Secret Manager
   - OWASP: A02 - Cryptographic Failures

2. **SQL Injection** (src/api/endpoints/forecast.py:42)
   - User input directly in SQL query
   - Risk: Database compromise, data exfiltration
   - Fix: Use parameterized queries
   - OWASP: A03 - Injection
   ```python
   # Bad
   sql = f"SELECT * FROM forecasts WHERE pod_id = '{pod_id}'"
   # Good  
   sql = "SELECT * FROM forecasts WHERE pod_id = $1"
   result = await conn.fetch(sql, pod_id)
   ```

### HIGH (fix before merge)
3. **XSS Vulnerability** (src/components/Dashboard.tsx:67)
   - Using dangerouslySetInnerHTML with user content
   - Risk: Arbitrary JavaScript execution
   - Fix: Sanitize HTML or use safe rendering
   - OWASP: A03 - Injection (XSS)

4. **Missing Authentication Check** (src/api/endpoints/admin.py:23)
   - Admin endpoint accessible without auth
   - Risk: Unauthorized admin access
   - Fix: Add @requires_auth decorator
   - OWASP: A01 - Broken Access Control

### MEDIUM (should fix)
5. **Weak Random Number** (src/shared/utils.py:45)
   - Using `random.randint()` for security token
   - Risk: Predictable tokens
   - Fix: Use `secrets.randbelow()`
   - OWASP: A02 - Cryptographic Failures

### LOW (nice to have)
6. **Missing Security Header** (src/main.py:30)
   - No X-Content-Type-Options header
   - Risk: MIME type sniffing attacks
   - Fix: Add header in middleware

### DEPENDENCY VULNERABILITIES
7. **Vulnerable Package: requests 2.25.0** (pyproject.toml)
   - CVE-2023-32681: Proxy-Authorization header leak
   - Risk: Credential exposure
   - Fix: Upgrade to requests >= 2.31.0
```

### 5. Summary & Risk Score

```
Security Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical:     2  🔴
High:         2  🟠
Medium:       1  🟡
Low:          1  ⚪
Dependencies: 1  🟣
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total:        7

Risk Score: 85/100 (High Risk)

Recommendation: ❌ DO NOT MERGE
- Must fix all CRITICAL findings before merge
- Should fix all HIGH findings before merge

Estimated Fix Time: 2-3 hours
```

## Severity Levels

| Severity | Criteria | Action Required |
|----------|----------|-----------------|
| **CRITICAL** | Exposed secrets, SQL injection, remote code execution | Immediate fix, do not merge |
| **HIGH** | XSS, broken auth, privilege escalation | Fix before merge |
| **MEDIUM** | Weak crypto, missing validation, insecure configs | Fix in sprint |
| **LOW** | Missing headers, weak random (non-security) | Nice to have |

## False Positive Handling

If a finding is a false positive, user can:
1. Add comment in code explaining why it's safe
2. Add to `.security-exceptions.yml`:
   ```yaml
   exceptions:
     - file: src/test/mock_data.py
       line: 42
       reason: "Mock API key for testing only"
       approved_by: "security-team"
       date: "2026-07-14"
   ```

## Output Format

**Default**: Markdown report with color-coded severity

**Exit codes**:
- `0`: No findings or only LOW
- `1`: MEDIUM findings present
- `2`: HIGH findings present  
- `3`: CRITICAL findings present

## MCP Tools Used
None (uses standard Claude Code tools: Read, Grep, Bash)

## Example Usage

```bash
# Standard scan (HIGH and CRITICAL only)
@security-checker

# Include all severities
@security-checker --severity low

# Include dependency scan
@security-checker --include-dependencies

# Full scan
@security-checker --severity low --include-dependencies
```

## Integration with Workflow

This agent is called as part of:
- `@backend-workflow` (before PR creation)
- `@frontend-workflow` (before PR creation)

Can also be run standalone at any time.

## Success Criteria
- [ ] All files in diff scanned
- [ ] Secrets detection completed
- [ ] OWASP top 10 checks performed
- [ ] Findings categorized by severity
- [ ] Each finding has:
  - File path and line number
  - Risk description
  - Fix recommendation
  - OWASP mapping
- [ ] Risk score calculated
- [ ] Merge recommendation provided
- [ ] If dependencies scanned: CVE report included
