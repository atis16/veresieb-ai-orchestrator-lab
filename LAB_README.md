# VeresiEB AI Orchestrator Lab — PUBLIC SYNTHETIC SANDBOX

This repository is intentionally **public** and separate from private VeresiEB. It contains no private project code, assets, credentials, or personal data.

## Scope
- Cezar: `CEZ_DRY_RUN=1` mock agent without AI provider login.
- Orkestra: `orkestra demo` with scripted fake agents.

## Safety
- Manual workflow_dispatch only. No PR/push/scheduled trigger.
- Public GitHub-hosted disposable runners, read-only permissions, no inherited credentials.
- Per-job and per-process timeouts; no provider model calls, no deployment.
- Upstream packages execute as untrusted third-party code on disposable runners only.
- Upstream PASS != VeresiEB private E2E PASS.

No Oracle provisioning. No private GitHub integration.
