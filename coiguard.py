#!/usr/bin/env python3
"""Fail-closed static gate for synthetic Cezar workflow YAML.

This protects against explicitly identical runner providers or unspecified
runners. It is NOT cryptographic proof of distinct actual model accounts.
Requires PyYAML; never touches a real provider or GitHub credential.
"""
import sys
from pathlib import Path
import yaml

def check(path: Path) -> tuple[bool, str]:
    try:
        obj = yaml.safe_load(path.read_text(encoding="utf-8"))
        nodes = obj.get("nodes", [])
        names = {x.get("id"): x for x in nodes if isinstance(x, dict)}
        implement = names.get("implement")
        reviewer = names.get("reviewer") or names.get("review")
        if not implement or not reviewer:
            return False, "BLOCK: missing implement/reviewer nodes"
        if implement.get("type") != "agent" or reviewer.get("type") != "agent":
            return False, "BLOCK: both nodes must be agents"
        i, r = implement.get("runner"), reviewer.get("runner")
        if not isinstance(i, str) or not isinstance(r, str) or not i or not r:
            return False, "BLOCK: runner identity not explicitly configured"
        if i == r:
            return False, f"BLOCK: identical provider runner {i!r}"
        return True, f"STATIC_ALLOW: different providers {i!r} / {r!r}; live account identity STILL UNVERIFIED"
    except Exception as exc:
        return False, f"BLOCK: invalid workflow: {exc}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: coiguard.py PATH_TO_CEZAR_WORKFLOW.yaml")
    ok, msg = check(Path(sys.argv[1]))
    print(msg)
    raise SystemExit(0 if ok else 2)
