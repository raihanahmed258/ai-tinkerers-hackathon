"""Score a round log against the golden answer in seed/expected_findings.md.

The seed is built so that a good round is checkable, not a matter of taste: six CRM
stalls, five mail threads and six follow-up items should surface, a named set of healthy
controls should stay silent, and exactly three things should reach a human in a fixed
order. This reads a captured round and says how it did.

    python -m floor.round | tee run.txt
    python -m floor.eval_expected run.txt
    python -m floor.eval_expected MOCK_ROUND_VALIDATE3.txt --markdown report.md

Exit codes: 0 green, 1 amber (clean but brief out of golden order), 2 red (a control was
flagged, the cap was blown, or mail was sent), 3 unusable input. So it can gate a commit.
Parsing only: it never calls a model, never touches the workspace, and never imports the
round, so it can score any log including one captured hours ago.
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

# ---------------------------------------------------------------- golden answer
# Transcribed from seed/expected_findings.md. Refs are the SUBJECT of a card (its `ref:`
# line), not everything named in its evidence.

SHOULD_FLAG = {
    "ops":      ["D-101", "D-102", "D-105", "D-104", "D-112", "D-116"],
    "inbox":    ["M-3", "M-1", "M-2", "M-4", "M-9"],
    "followup": ["T-4", "T-1", "T-2", "E-4", "T-3", "E-3"],
}

# Credited if present, never penalised if absent.
BORDERLINE = {
    "ops":      ["D-118", "D-103"],
    "inbox":    ["M-11"],
    "followup": ["T-8", "E-1", "E-2", "E-7"],
}

# Flagging any of these is a control violation. Scoped per watcher on purpose: Ops must
# not flag D-107 Ember Grill (a healthy live customer in the CRM), yet Ember Grill is
# still the top human item, reached through mail M-3 and task T-4. Right answer, right
# door.
MUST_NOT_FLAG = {
    "ops":      ["D-106", "D-108", "D-110", "D-111", "D-114",
                 "D-117", "D-119", "D-115", "D-113", "D-107", "D-120"],
    "inbox":    ["M-7", "M-8", "M-5", "M-6", "M-10", "M-12"],
    "followup": ["T-5", "T-6", "T-7", "T-9", "E-5", "E-6", "E-8", "E-9"],
}

EXPECTED_BRIEF = [
    {"who": "theo",  "account": "Ember Grill"},
    {"who": "dana",  "account": "Pine & Salt"},
    {"who": "priya", "account": "Copper Kettle"},
]

MAX_HUMAN_ITEMS = 3
CARD_TARGET = 17

# ---------------------------------------------------------------- parsing
REF = re.compile(r"\b([DMTE]-\d+)\b")


def _norm_agent(raw: str) -> str:
    return raw.strip().lower().replace("-", "").replace(" ", "")


def parse_log(text: str) -> dict:
    cards, brief_items, handled = [], [], []
    actions = {"notes": 0, "drafts": 0, "tasks": 0, "asks": 0, "refusals": 0,
               "problem_blocks": 0, "floor_posts": 0, "sends": 0}

    for line in text.splitlines():
        if "POST → #agents-floor" in line or "POST -> #agents-floor" in line:
            actions["floor_posts"] += 1
        if "CRM NOTE →" in line or "CRM NOTE ->" in line:
            actions["notes"] += 1
        if "DRAFT (not sent)" in line:
            actions["drafts"] += 1
        if re.search(r"TASK\s*(→|->)", line):
            actions["tasks"] += 1
        if line.lstrip().startswith("@"):
            actions["asks"] += 1
        if "REFUSED" in line.upper():
            actions["refusals"] += 1
        if line.strip().startswith("PROBLEM ·") or line.strip().startswith("PROBLEM |"):
            actions["problem_blocks"] += 1
        # Any sign mail actually left the building. Drafts are explicitly excluded.
        if re.search(r"\bSENT\b|send_email|EMAIL SENT", line) and "not sent" not in line:
            actions["sends"] += 1

    # Finding cards: a header line, then labelled lines until the block breaks.
    blocks = re.split(r"(?=FINDING\s*[·|]\s*)", text)
    for block in blocks[1:]:
        header = block.splitlines()[0]
        parts = [p.strip() for p in re.split(r"[·|]", header)]
        agent = _norm_agent(parts[1]) if len(parts) > 1 else "unknown"
        card = {"agent": agent, "confidence": parts[2] if len(parts) > 2 else "", "ref": "", "account": ""}
        for raw in block.splitlines()[1:]:
            if not raw.strip() or raw.lstrip().startswith("────"):
                break
            if ":" in raw:
                key, _, value = raw.partition(":")
                key = key.strip().lower()
                if key in ("ref", "account", "what", "why_stalled", "evidence", "proposed", "needs_human"):
                    card[key] = value.strip()
        if not card["ref"]:
            found = REF.search(block)
            card["ref"] = found.group(1) if found else ""
        cards.append(card)

    # Brief: numbered items, each "@who — Account ($arr): cause"
    in_brief = False
    for line in text.splitlines():
        if "Attention brief" in line:
            in_brief = True
            continue
        if not in_brief:
            continue
        if line.strip().lower().startswith("handled without you"):
            handled = [h.strip() for h in line.partition(":")[2].split(",") if h.strip()]
            continue
        m = re.match(r"\s*(\d+)\.\s*@(\w+)\s*[—–-]\s*(.+)", line)
        if m:
            rest = m.group(3)
            account = rest.split(":", 1)[0]
            account = re.sub(r"\(\$[\d,]+\)", "", account).strip()
            brief_items.append({"rank": int(m.group(1)), "who": m.group(2).lower(),
                                "account": account, "text": rest})
        elif brief_items and line.strip().lower().startswith("evidence:"):
            brief_items[-1]["evidence"] = [r for r in REF.findall(line)]

    return {"cards": cards, "brief": brief_items, "handled": handled, "actions": actions}


# ---------------------------------------------------------------- scoring
def score(p: dict) -> dict:
    cards, brief, actions = p["cards"], p["brief"], p["actions"]
    by_agent: dict[str, set[str]] = {}
    for c in cards:
        by_agent.setdefault(c["agent"], set()).add(c["ref"])

    recall, violations, credited = {}, [], {}
    for watcher, wanted in SHOULD_FLAG.items():
        got = by_agent.get(watcher, set())
        hit = [r for r in wanted if r in got]
        recall[watcher] = {"hit": hit, "missed": [r for r in wanted if r not in got],
                           "n": len(hit), "of": len(wanted)}
        credited[watcher] = [r for r in BORDERLINE.get(watcher, []) if r in got]

    for watcher, forbidden in MUST_NOT_FLAG.items():
        got = by_agent.get(watcher, set())
        for ref in forbidden:
            if ref in got:
                violations.append(f"{watcher} flagged control {ref}")

    # Any ref surfacing under a watcher that has no business seeing it.
    prefix_owner = {"D": "ops", "M": "inbox"}
    for c in cards:
        owner = prefix_owner.get(c["ref"][:1])
        if owner and c["agent"] in SHOULD_FLAG and c["agent"] != owner:
            violations.append(f"{c['agent']} posted {c['ref']}, which belongs to {owner}'s slice")

    human = brief[:]
    brief_checks = {
        "count": len(human),
        "within_cap": len(human) <= MAX_HUMAN_ITEMS,
        "ranking_matches": True,
        "detail": [],
    }
    for i, expected in enumerate(EXPECTED_BRIEF):
        if i >= len(human):
            brief_checks["ranking_matches"] = False
            brief_checks["detail"].append(f"rank {i+1}: MISSING, expected @{expected['who']} / {expected['account']}")
            continue
        actual = human[i]
        who_ok = actual["who"] == expected["who"]
        acct_ok = expected["account"].lower() in actual["account"].lower()
        if not (who_ok and acct_ok):
            brief_checks["ranking_matches"] = False
            brief_checks["detail"].append(
                f"rank {i+1}: got @{actual['who']} / {actual['account']}, "
                f"expected @{expected['who']} / {expected['account']}")
        else:
            brief_checks["detail"].append(f"rank {i+1}: @{actual['who']} / {actual['account']} ✓")

    if not brief_checks["within_cap"]:
        violations.append(f"brief carries {len(human)} human items, cap is {MAX_HUMAN_ITEMS}")
    if actions["sends"]:
        violations.append(f"{actions['sends']} line(s) suggest mail was SENT, not drafted")

    total_hit = sum(r["n"] for r in recall.values())
    total_want = sum(r["of"] for r in recall.values())

    # Three states, because "nothing forbidden happened" is not the same as "this is the
    # run you want to record". A wrong brief order is not a safety violation, but it is
    # the difference between the demo landing and the demo missing its lead item.
    if violations or not brief_checks["within_cap"]:
        verdict = "RED"
    elif not brief_checks["ranking_matches"]:
        verdict = "AMBER"
    else:
        verdict = "GREEN"

    return {"recall": recall, "credited": credited, "violations": violations,
            "brief": brief_checks, "cards": len(cards), "actions": actions,
            "total_hit": total_hit, "total_want": total_want,
            "verdict": verdict, "green": verdict == "GREEN"}


# ---------------------------------------------------------------- reporting
def render(s: dict, source: str) -> str:
    L = []
    L.append(f"Round scorecard · {source} · {s['verdict']}")
    L.append("")
    L.append(f"Finding cards: {s['cards']} (validated reference run: {CARD_TARGET})")
    L.append(f"Golden refs surfaced: {s['total_hit']}/{s['total_want']}")
    L.append("")
    L.append("Per watcher")
    for watcher in ("ops", "inbox", "followup"):
        r = s["recall"][watcher]
        extra = s["credited"][watcher]
        line = f"  {watcher:9} {r['n']}/{r['of']}"
        if r["missed"]:
            line += f"   missed: {', '.join(r['missed'])}"
        if extra:
            line += f"   also caught: {', '.join(extra)}"
        L.append(line)
    L.append("")
    L.append("Brief")
    L.append(f"  human items: {s['brief']['count']} (cap {MAX_HUMAN_ITEMS}) "
             f"{'ok' if s['brief']['within_cap'] else 'OVER CAP'}")
    for d in s["brief"]["detail"]:
        L.append(f"  {d}")
    L.append("")
    a = s["actions"]
    L.append("Actions executed")
    L.append(f"  floor posts {a['floor_posts']} · crm notes {a['notes']} · drafts {a['drafts']} · "
             f"tasks {a['tasks']} · questions {a['asks']} · refusals {a['refusals']} · "
             f"problem blocks {a['problem_blocks']}")
    L.append(f"  customer sends: {a['sends']} {'← MUST BE 0' if a['sends'] else '(correct)'}")
    L.append("")
    if s["violations"]:
        L.append(f"Violations ({len(s['violations'])})")
        for v in s["violations"]:
            L.append(f"  ✗ {v}")
    else:
        L.append("Violations: none. No control flagged, cap respected, nothing sent.")

    if s["verdict"] == "AMBER":
        L.append("")
        L.append("AMBER: nothing forbidden happened, but the brief is not in golden order.")
        L.append("Do not record this run. The lead human item is what the demo is built on.")
    elif s["verdict"] == "RED":
        L.append("")
        L.append("RED: a control was flagged, the human cap was exceeded, or mail left the building.")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="Score a round log against seed/expected_findings.md")
    ap.add_argument("log", nargs="?", help="captured round output; omit to read stdin")
    ap.add_argument("--markdown", metavar="PATH", help="also write the scorecard to a file")
    args = ap.parse_args()

    if args.log:
        path = Path(args.log)
        if not path.exists():
            print(f"no such log: {path}", file=sys.stderr)
            return 3
        text = path.read_text(encoding="utf-8", errors="replace")
        source = path.name
    else:
        text = sys.stdin.read()
        source = "stdin"

    if "FINDING" not in text:
        print(f"{source} contains no FINDING cards — is this a round log?", file=sys.stderr)
        return 3

    s = score(parse_log(text))
    report = render(s, source)
    print(report)
    if args.markdown:
        Path(args.markdown).write_text(report + "\n", encoding="utf-8")
        print(f"\nwritten: {args.markdown}")
    return {"GREEN": 0, "AMBER": 1, "RED": 2}[s["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
