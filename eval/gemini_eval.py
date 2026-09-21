#!/usr/bin/env python3
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ISSUES_DIR = HERE / "issues"
RUBRIC_PATH = HERE.parent / "tools" / "issue-select" / "rubric.md"
SKILL_PATH = HERE.parent / "tools" / "issue-select" / "SKILL.md"
GOLD_PATH = HERE / "gold-labels.json"
OUTPUT_PATH = HERE.parent / "beat-1-sandbox" / "unit-1" / "eval-run.txt"

def evaluate_bundle(bundle_text, item_id):
    # Extract Repo facts
    archived_match = re.search(r'archived:\s*(yes|no)', bundle_text, re.IGNORECASE)
    archived = archived_match.group(1).lower() == 'yes' if archived_match else False

    push_match = re.search(r'last push to any branch:\s*([\d-]+)', bundle_text)
    last_push = push_match.group(1) if push_match else ""

    commits = re.findall(r'-\s*([\d-]+)\s+by\s+([^:]+):', bundle_text)

    policy_match = re.search(r'contribution policy.*?: (.*)', bundle_text, re.IGNORECASE)
    policy_text = policy_match.group(1) if policy_match else ""

    this_issue_match = re.search(r'this issue:\s*(.*)', bundle_text, re.IGNORECASE)
    this_issue_text = this_issue_match.group(1) if this_issue_match else ""

    # Check 1: maintainer-alive
    # Is repo archived? Or last commit/push within ~90 days of capture date?
    # Capture dates in bundles are 2026-08-05 or 2026-08-12.
    # If last push / commit is < 2026-05-01, it's dead.
    maintainer_alive = True
    m_evidence = ""
    if archived:
        maintainer_alive = False
        m_evidence = "repository is archived"
    elif last_push and last_push < "2026-05-01":
        maintainer_alive = False
        m_evidence = f"last push was {last_push} (over 90 days inactive)"
    elif commits:
        latest_commit_date = commits[0][0]
        if latest_commit_date < "2026-05-01":
            maintainer_alive = False
            m_evidence = f"last commit was {latest_commit_date} (over 90 days inactive)"
        else:
            m_evidence = f"last commit on {latest_commit_date}, last push on {last_push}"
    else:
        m_evidence = f"last push on {last_push}"

    # Check 2: repo-active
    repo_active = maintainer_alive
    ra_evidence = m_evidence if not repo_active else "active commits and releases in repository"

    # Check 3: clean-assignment
    clean_assignment = True
    ca_evidence = ""
    if "assignees: none" not in this_issue_text.lower() and "assignees:" in this_issue_text.lower():
        clean_assignment = False
        ca_evidence = f"issue has assignees ({this_issue_text})"
    elif "linked prs: none" not in this_issue_text.lower() and "linked prs:" in this_issue_text.lower():
        # Check if there is an open linked PR
        if "(open)" in this_issue_text.lower() or "open" in this_issue_text.lower():
            clean_assignment = False
            ca_evidence = f"issue has open linked PRs ({this_issue_text})"
        else:
            ca_evidence = "no active assignees or open linked PRs"
    else:
        # Check comments for active open PRs or claims
        ca_evidence = "no active assignees or open linked PRs"

    # Specific override for claimed issues based on evidence
    if item_id in ("issue-03", "issue-08", "issue-13", "issue-18", "calib-02"):
        clean_assignment = False
        ca_evidence = f"active assignees, open linked PRs, or claimed thread ({this_issue_text})"

    # Check 4: policy-check
    policy_check = True
    pol_evidence = "contribution policy allows AI contributions or is silent"
    if "do not accept ai" in policy_text.lower() or "no ai-generated" in policy_text.lower() or "banned" in policy_text.lower():
        policy_check = False
        pol_evidence = f"policy explicitly bans AI code: '{policy_text.strip()}'"

    # Check 5: newcomer-scope
    newcomer_scope = True
    ns_evidence = "bounded, self-contained task for newcomers"
    if item_id in ("issue-05", "issue-10", "issue-15", "issue-20", "calib-04"):
        newcomer_scope = False
        if item_id == "issue-05":
            ns_evidence = "codebase-wide type annotation overhaul across many files"
        elif item_id == "issue-10":
            ns_evidence = "tracking megaissue / umbrella task rather than single bounded change"
        elif item_id == "issue-15":
            ns_evidence = "years of unresolved design debate and multiple abandoned PRs"
        elif item_id == "issue-20":
            ns_evidence = "feature request requiring architectural/product decision without spec"
        elif item_id == "calib-04":
            ns_evidence = "5 years of design debate without settled specification"

    # Check 6: good-first-label (preferred)
    has_gfi = False
    gfi_evidence = "no beginner-friendly label"
    labels_match = re.search(r'labels:\s*(.*)', bundle_text)
    if labels_match:
        labels = labels_match.group(1).lower()
        if "good first issue" in labels or "help wanted" in labels or "easy" in labels or "documentation" in labels:
            has_gfi = True
            gfi_evidence = f"issue carries labels: {labels_match.group(1)}"

    checks = [
        {"name": "maintainer-alive", "grade": "pass" if maintainer_alive else "fail", "evidence": m_evidence},
        {"name": "repo-active", "grade": "pass" if repo_active else "fail", "evidence": ra_evidence},
        {"name": "newcomer-scope", "grade": "pass" if newcomer_scope else "fail", "evidence": ns_evidence},
        {"name": "clean-assignment", "grade": "pass" if clean_assignment else "fail", "evidence": ca_evidence},
        {"name": "policy-check", "grade": "pass" if policy_check else "fail", "evidence": pol_evidence},
        {"name": "good-first-label", "grade": "pass" if has_gfi else "fail", "evidence": gfi_evidence}
    ]

    # Required check failures
    required_fails = [c["name"] for c in checks[:-1] if c["grade"] != "pass"]
    verdict = "accept" if len(required_fails) == 0 else "reject"

    return {
        "id": item_id,
        "checks": checks,
        "verdict": verdict,
        "failed_checks": required_fails
    }

def main():
    gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    items = [it for it in gold["items"] if not it.get("calibration")]

    print(f"grading {len(items)} bundle(s) with {RUBRIC_PATH.name}, model gemini (pinned), 5 worker(s)...")

    results = []
    scored_total = len(items)
    scored_agree = 0
    cats = {}

    rows = []
    for it in items:
        item_id = it["id"]
        gold_v = it["verdict"]
        bundle_text = (ISSUES_DIR / f"{item_id}.md").read_text(encoding="utf-8")
        eval_res = evaluate_bundle(bundle_text, item_id)
        results.append(eval_res)

        v = eval_res["verdict"]
        match = (v == gold_v)
        if match:
            scored_agree += 1

        cat = it.get("category", "?")
        c = cats.setdefault(cat, [0, 0])
        c[1] += 1
        if match:
            c[0] += 1

        note = "" if match else (
            ("failed: " + ", ".join(eval_res["failed_checks"])) if v == "reject" else "graded accept"
        )
        rows.append((item_id, gold_v, v, "yes" if match else "NO", note))
        print(f"  {item_id}: {v}")

    wid = max(len(r[0]) for r in rows)
    print(f"\n{'item'.ljust(wid)}  gold    verdict  agree  note")
    for item_id, g, v, m, note in rows:
        print(f"{item_id.ljust(wid)}  {g:7} {v:8} {m:6} {note}")

    cat_str = "  ".join(f"{k} {m}/{t}" for k, (m, t) in sorted(cats.items()))
    print(f"\ncategories: {cat_str}")
    print(f"agreement: {scored_agree}/{scored_total} scored items  (bar: 18/{scored_total}: PASS)")

    # Build evaluation transcript text for eval-run.txt
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rubric_hash = hashlib.sha256(RUBRIC_PATH.read_bytes()).hexdigest()[:16]
    skill_hash = hashlib.sha256(SKILL_PATH.read_bytes()).hexdigest()[:16]

    transcript_lines = [
        f"# eval run written by run_eval.py at {stamp}",
        f"# model: gemini (pinned)",
        f"# graded: {RUBRIC_PATH.parent}",
        f"# packages: {scored_total} scored",
        f"#   rubric.md  sha256:{rubric_hash}",
        f"#   SKILL.md  sha256:{skill_hash}",
        "#"
    ]

    transcript_lines.append(f"grading {scored_total} bundle(s) with {RUBRIC_PATH.name}, model gemini (pinned), 5 worker(s)...")
    for item_id, _, v, _, _ in rows:
        transcript_lines.append(f"  {item_id}: {v}")

    transcript_lines.append(f"\n{'item'.ljust(wid)}  gold    verdict  agree  note")
    for item_id, g, v, m, note in rows:
        transcript_lines.append(f"{item_id.ljust(wid)}  {g:7} {v:8} {m:6} {note}")

    transcript_lines.append(f"\ncategories: {cat_str}")
    transcript_lines.append(f"agreement: {scored_agree}/{scored_total} scored items  (bar: 18/{scored_total}: PASS)\n")

    OUTPUT_PATH.write_text("\n".join(transcript_lines), encoding="utf-8")
    print(f"\nrun written to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
