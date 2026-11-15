# VeresiEB AI Cockpit: build-vs-adapt security decision (2026-11-15)

Status: **RESEARCH / PUBLIC SYNTHETIC LAB ONLY**. Not approved for VeresiEB private code, prod, agent credentials, or merge.

## Architecture decision

**Recommend adapting Cezar as an operator UI / job intake** rather than merging its internals directly with Orkestra. Place a fail-closed, independently tested **Policy Gateway** between cockpit and execution. Evaluate whether Orkestra's policy kernel can serve as an isolated executor behind a narrow adapter. Keep the existing #111 SQLite Relay contract as the record and compatibility reference, *not* a deployed global durable queue.

### Why
- Cezar MIT license; Orkestra Apache-2.0 license (preserve notices).
- Confirmed failure: Cezar graph allows same `runner: claude` for author and reviewer, and returns success. See negative run https://github.com/atis16/veresieb-ai-orchestrator-lab/actions/runs/43765784584
- Static external coiguard PASS only checks declared provider; cannot attest actual identity/session/account. https://github.com/atis16/veresieb-ai-orchestrator-lab/actions/runs/43765884854
- Cezar graph simulated reject -> repair -> re-review PASS. https://github.com/atis16/veresieb-ai-orchestrator-lab/actions/runs/43765511196
- Orkestra fake-agent demo PASS for independent agents, test gate and bounded repair. https://github.com/atis16/veresieb-ai-orchestrator-lab/actions/runs/43763376367
- Orkestra security threat model: https://github.com/andyyaro/orkestra/blob/main/docs/security/THREAT_MODEL.md ; note Docker sandbox is not available for all vendor CLI backends, so default execution still requires an OS-level trust boundary.

## Non-bypassable policy contract (proposed, NOT implemented)
Input immutable: task_id, repo/worktree identity, plan digest, author_agent_id and attested provider/profile, review_agent_id and attested provider/profile, code commit SHA, test config digest, affected areas, approval set, capability grants, expiration. No user/agent-provided free text may override the policy.

1. Account/session binding: different provider alone is insufficient; block self-review on same durable agent identity, originating session, or delegated descendant.
2. Reviewer assigned by Policy Gateway, never by author agent; candidate cannot alter reviewer identity or approvals.
3. CI tests run by trusted evaluator against exact commit/tree SHA. A reviewer verdict is only advisory until bound to that SHA.
4. Each affected area reviewer must independently approve its own scope. Repairman authors fixes, cannot approve them. PM can coordinate but cannot override safety/reviewer gate.
5. Any new commit invalidates prior test and review verdicts. Re-verify all affected aspects before closure.
6. Read-only provider subprocesses must not receive tokens needed for writes; no main/production/DNS changes, secrets, external personal data, paid API without owner GO.
7. Timeouts, cancel, retry limits, re-entrancy, exact evidence links and audit ledger. UNKNOWN means BLOCK.
8. Untrusted PR/workflow/third-party package cannot run with host credentials. Do not put long-lived credentials into self-hosted runner trust boundary.

## Cybersecurity threat model and test plan

- **Prompt injection / repo instruction hijack**: malicious README, task payload, Markdown skill or tool output tells agent to bypass checks. Test hostile but synthetic files; expected policy remains immutable.
- **Tool/mcp abuse**: write tool exposed to review-only agent; shell execution, cross-worktree read, curl exfiltration. Deny by OS/container permissions, not prompt alone.
- **Agent impersonation / fake approval**: author forges review text or uses `runner: claude` twice. Enforce signed / immutable provenance and separate principals.
- **Replay / TOCTOU**: old pass reused for new SHA, changed artifact after approval. Gate binds to tree SHA and reruns after changes.
- **Supply chain / skills**: verify source/commit and publisher; use NVIDIA SkillSpector static scanner on every SKILL.md directory; pin source; inspect dependencies and SBOM with OSV/Trivy/pip-audit/npm audit and CodeQL/Semgrep where suitable.
- **Identity/provider Terms**: no assumption that subscription credentials are permitted for background third-party automated agents; verify vendor terms individually.
- **Secrets and logs**: no token in workflows/PRs/reports, redact tests; read-only tokens scoped to repo, TTL, rotation.
- **Crash recovery/queue**: SQLite ephemeral runner not cross-run durable. Test crash, duplicate execution, reconciliation, idempotent completion.

## NVIDIA verification boundaries

NVIDIA [SkillSpector](https://github.com/NVIDIA/SkillSpector) scans SKILL.md and dependencies for suspicious patterns (static; optional model evaluation). It is **not** a general source-code vulnerability scanner and does not prove an agent safe. NVIDIA [garak](https://github.com/NVIDIA/garak) evaluates LLM-backed systems at runtime for prompt injection/data leak etc; requires a controlled target and can incur model calls, so **not launched**.

NVIDIA [skills catalog](https://github.com/NVIDIA/skills) publishes signed skills; verify signature/provenance and scan prior to install. A successful signature validates origin/integrity, not absence of bugs.

## Integration stages & acceptance

Gate A: public lab SkillSpector dry-run on benign synthetic skill, no API key, archive raw/JSON results. Gate B: threat-model tests for forbidden same identity and replay; FAIL-CLOSED. Gate C: small adapter proof Cezar UI -> policy -> Orkestra fake-agent executor using synthetic data; do not import entire dependency trees. Gate D: source/dependency audit and ToS check. Gate E: read-only, explicitly authorized real provider pilot on isolated worktree. Gate F: owners' separate approval for private project integration / protected merge. No Oracle required until platform selection.

## Priorities

P0 guard, provenance, secrets, untrusted inputs and mutable worktrees. P1 repair lifecycle/all-owner sign-off, crash recovery. P2 mobile cockpit, notifications, observability. P3 optional deployment choice. Maintain 0 new required subscription cost.
