# Security Baseline Checklist

> Copy this section into any new project's CLAUDE.md to enforce security standards from day one.

**Project:** _______________
**Date:** _______________
**Audited by:** _______________

---

## Security Requirements

The following 11 items MUST be addressed before any deployment. When implementing features, reference this checklist and note which items are satisfied by the implementation.

### 1. Authentication
- Use bcrypt (cost factor >= 12) or argon2 for password hashing — never store plain-text passwords
- Use signed JWTs with expiration for session tokens
- Implement account lockout after 5 failed login attempts

### 2. Authorization
- Enforce role-based access control (RBAC) on every protected route
- Check permissions server-side — never rely on client-side role checks
- Validate resource ownership (user can only access their own data)

### 3. Input Validation
- Validate all user input against a schema (Zod, Pydantic, Joi, etc.)
- Use parameterized queries for ALL database operations — zero string concatenation
- Sanitize file uploads: check MIME type, limit file size, rename on storage

### 4. CSRF Protection
- Use CSRF tokens on all state-changing requests, OR
- Use SameSite=Strict cookies with proper domain settings

### 5. XSS Prevention
- Never use `dangerouslySetInnerHTML` (React) or `v-html` (Vue) with user content
- Set Content-Security-Policy headers (at minimum: `default-src 'self'`)
- Escape all dynamic content in templates

### 6. SQL Injection
- Parameterized queries only — enforce via ORM or query builder
- No raw SQL with string interpolation anywhere in the codebase
- Use least-privilege database users (app user cannot DROP tables)

### 7. Rate Limiting
- Apply per-IP rate limiting on all public endpoints (e.g., 100 req/min)
- Apply stricter per-user rate limiting on auth endpoints (e.g., 5 req/min)
- Return 429 with Retry-After header

### 8. Secrets Management
- All secrets in environment variables — never committed to git
- Maintain `.env.example` with placeholder values (no real secrets)
- `.env` files are in `.gitignore` — verify before every commit

### 9. CORS Configuration
- Explicit allowlist of permitted origins — never use `*` in production
- Only allow necessary HTTP methods and headers
- Do not expose sensitive headers in CORS responses

### 10. Dependency Audit
- Run `npm audit` / `pip-audit` in CI pipeline
- Review and update dependencies monthly
- Pin major versions to prevent surprise breaking changes

### 11. Deploy Priorities (the first three things on any deployment)
- Email verification: no account is active until its email address is confirmed
- MFA (multi-factor authentication): offered at minimum, required for admin and privileged roles
- Invite codes or rate-limited registration: open sign-up is never left unthrottled

---

## How to Use This Checklist

1. Copy everything from `## Security Requirements` down into your project's CLAUDE.md
2. As you implement each item, add a note below it: `> Implemented in <file>:<function> on <date>`
3. During `/security-audit`, reference this checklist to verify coverage
4. Items not applicable to your project should be marked `> N/A — <reason>` rather than deleted
