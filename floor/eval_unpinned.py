"""Ablation: how much of the brief does the Desk actually decide?

`floor/round.py` contains stabilisers that push a round toward the golden answer:
`_ops_backfill` and `_followup_backfill` add expected findings the model skipped,
`_ensure_golden_problems` synthesises the Ember / Pine / Copper problems if the Desk
omitted them, and `_stabilize_brief` forces those three into ranks 1-3 with fixed owners
while holding a denylist of healthy accounts off the brief.

Those are defensible as demo stability guards, but they make "the brief matched the
golden order" close to tautological, so it is worth knowing the unpinned number before
anyone quotes the pinned one to a judge. This runs the same round twice against the same
seed, once as shipped and once with the stabilisers replaced by identity functions, and
diffs them. It monkeypatches at runtime and never modifies round.py.

    python -m floor.eval_unpinned            # pinned vs unpinned, side by side
    python -m floor.eval_unpinned --trace    # which stabiliser actually changed anything

Needs ANTHROPIC_API_KEY to say anything about the model path; without it both runs use
the heuristic fallback and the comparison only covers the stabilisers themselves.
"""
from __future__ import annotations
import io, os, sys
from contextlib import redirect_stdout

from . import round as R
from .client import MockClient
from .eval_expected import parse_log, score

PINS = ("_ops_backfill", "_followup_backfill", "_ensure_golden_problems", "_stabilize_brief")


def _capture_round() -> str:
    buf = io.StringIO()
    ws = MockClient(verbose=True)
    with redirect_stdout(buf):
        R.run_round(ws)
    return buf.getvalue()


def _disable_pins():
    """Replace each stabiliser with a pass-through that returns its first argument."""
    saved = {}
    for name in PINS:
        saved[name] = getattr(R, name)
        setattr(R, name, lambda first, *a, **k: first)
    return saved


def _restore(saved: dict):
    for name, fn in saved.items():
        setattr(R, name, fn)


def _trace_pins():
    """Wrap each stabiliser so we learn which ones actually changed their input.

    More useful than the binary: it separates "the Desk produced the right items and a pin
    only reordered them" from "a pin invented the items outright".
    """
    calls = {name: {"n": 0, "changed": 0, "added": 0, "notes": []} for name in PINS}
    saved = {}

    def wrap(name, fn):
        def inner(first, *a, **k):
            rec = calls[name]
            rec["n"] += 1
            before_len = len(first) if isinstance(first, list) else None
            before = repr(first)
            out = fn(first, *a, **k)
            after_len = len(out) if isinstance(out, list) else None
            if repr(out) != before:
                rec["changed"] += 1
            if before_len is not None and after_len is not None and after_len != before_len:
                rec["added"] += after_len - before_len
            # Did a synthesised problem carry the canned cause text?
            if name == "_ensure_golden_problems" and isinstance(out, list):
                for item in out:
                    cause = str((item or {}).get("cause", ""))
                    for canned in ("Q3 state withholding unconfirmed",
                                   "Champion bounced; no other contact known",
                                   "Revised quote promised twice and already late"):
                        if canned in cause and canned not in rec["notes"]:
                            rec["notes"].append(canned)
            return out
        return inner

    for name in PINS:
        saved[name] = getattr(R, name)
        setattr(R, name, wrap(name, saved[name]))
    return saved, calls


def _summary(label: str, log: str) -> dict:
    s = score(parse_log(log))
    return {
        "label": label,
        "verdict": s["verdict"],
        "cards": s["cards"],
        "recall": f"{s['total_hit']}/{s['total_want']}",
        "per_watcher": {w: f"{s['recall'][w]['n']}/{s['recall'][w]['of']}" for w in ("ops", "inbox", "followup")},
        "brief": [f"@{i['who']} / {i['account']}" for i in parse_log(log)["brief"]],
        "cap_ok": s["brief"]["within_cap"],
        "ranking_matches": s["brief"]["ranking_matches"],
        "violations": s["violations"],
    }


def run_trace() -> int:
    have_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    print("The Floor · stabiliser trace")
    print(f"model path: {'Claude (ANTHROPIC_API_KEY present)' if have_key else 'heuristic fallback (no key)'}")
    print()
    saved, calls = _trace_pins()
    try:
        log = _capture_round()
    finally:
        _restore(saved)

    s = _summary("traced run", log)
    print(f"verdict {s['verdict']} · cards {s['cards']} · golden recall {s['recall']} · golden order {s['ranking_matches']}")
    print()
    print("Stabiliser activity")
    fabricated = False
    for name in PINS:
        rec = calls[name]
        bits = f"  {name:28} calls {rec['n']}  changed {rec['changed']}"
        if rec["added"]:
            bits += f"  items added {rec['added']:+d}"
        print(bits)
        for note in rec["notes"]:
            fabricated = True
            print(f"      ↳ synthesised a brief item with canned text: \"{note}\"")
    print()
    print("Reading")
    if fabricated:
        print("  A brief item was INVENTED by _ensure_golden_problems using pre-written cause text.")
        print("  That item is not a model finding. Do not present it as one.")
    elif any(calls[n]["changed"] for n in ("_ensure_golden_problems", "_stabilize_brief")):
        print("  No brief item was invented. The Desk produced the items; a stabiliser then")
        print("  reordered them and/or forced the owner, and held denylisted accounts off the brief.")
        print("  Defensible framing: the findings and the merge are derived, the priority order")
        print("  encodes a hand-written playbook prior. Say that before a judge greps for it.")
    else:
        print("  No stabiliser changed anything on this run. The brief is entirely Desk output.")
    if any(calls[n]["changed"] for n in ("_ops_backfill", "_followup_backfill")):
        print("  Backfill added findings the watcher missed, so per-watcher recall is assisted,")
        print("  not purely model recall. Quote it that way.")
    return 0


def main() -> int:
    if "--trace" in sys.argv:
        return run_trace()
    have_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    print("The Floor · pinned vs unpinned ablation")
    print(f"model path: {'Claude (ANTHROPIC_API_KEY present)' if have_key else 'heuristic fallback (no key)'}")
    print(f"stabilisers under test: {', '.join(PINS)}")
    print()

    shipped = _summary("as shipped (pinned)", _capture_round())

    saved = _disable_pins()
    try:
        ablated = _summary("stabilisers disabled", _capture_round())
    finally:
        _restore(saved)

    for s in (shipped, ablated):
        print(f"── {s['label']}")
        print(f"   verdict         {s['verdict']}")
        print(f"   cards           {s['cards']}")
        print(f"   golden recall   {s['recall']}   " +
              "  ".join(f"{w}:{v}" for w, v in s["per_watcher"].items()))
        print(f"   brief cap ok    {s['cap_ok']}")
        print(f"   golden order    {s['ranking_matches']}")
        print("   brief items")
        for i, item in enumerate(s["brief"], 1):
            print(f"     {i}. {item}")
        if s["violations"]:
            for v in s["violations"]:
                print(f"   ✗ {v}")
        print()

    same_order = shipped["brief"] == ablated["brief"]
    print("── verdict on the pinning")
    if same_order:
        print("   The brief is IDENTICAL with the stabilisers disabled.")
        print("   The Desk reaches that ranking on its own. The pins are a safety net, not the cause.")
        print("   You can say the merge and the ranking are derived, and mean it.")
    else:
        print("   The brief CHANGES when the stabilisers are disabled.")
        print("   The shipped ranking is produced, at least in part, by the pins and not by the Desk.")
        print("   Do not tell a judge the Desk ranked these three on its own.")
        print("   Honest framings that still hold:")
        print("     - the watchers found the underlying evidence, and that part is real")
        print("     - the merge joins refs across CRM, Mail, Tasks and Calendar for one account")
        print("     - the ranking carries a hand-tuned playbook prior, which is a product decision")
        print("       you can defend, as long as you name it before a judge greps for it")
    return 0 if same_order else 1


if __name__ == "__main__":
    raise SystemExit(main())
