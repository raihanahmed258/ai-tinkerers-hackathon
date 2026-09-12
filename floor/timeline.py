"""Per-account timeline tracker for Desk escalation control.

Track per account:
- last_decision: when Desk last acted on this account
- drafts_prepared: list of refs where drafts were created
- waiting_on: "human" | "customer" | "none"
- escalated_at: when account was first escalated to humans
- escalation_count: how many times escalated

API is mock-friendly and can run without Ambiguous live.
"""
from __future__ import annotations
import datetime as dt
import json
import os
from pathlib import Path
from typing import Literal

WaitingOn = Literal["human", "customer", "none"]


class AccountTimeline:
    """State for one account's timeline."""
    
    def __init__(
        self,
        account: str,
        last_decision: str | None = None,
        drafts_prepared: list[str] | None = None,
        waiting_on: WaitingOn = "none",
        escalated_at: str | None = None,
        escalation_count: int = 0,
        last_escalation_cause: str | None = None,
    ):
        self.account = account
        self.last_decision = last_decision  # ISO date
        self.drafts_prepared = drafts_prepared or []
        self.waiting_on = waiting_on
        self.escalated_at = escalated_at  # ISO date of first escalation
        self.escalation_count = escalation_count
        self.last_escalation_cause = last_escalation_cause
    
    def to_dict(self) -> dict:
        return {
            "account": self.account,
            "last_decision": self.last_decision,
            "drafts_prepared": self.drafts_prepared,
            "waiting_on": self.waiting_on,
            "escalated_at": self.escalated_at,
            "escalation_count": self.escalation_count,
            "last_escalation_cause": self.last_escalation_cause,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> AccountTimeline:
        return cls(
            account=data["account"],
            last_decision=data.get("last_decision"),
            drafts_prepared=data.get("drafts_prepared", []),
            waiting_on=data.get("waiting_on", "none"),
            escalated_at=data.get("escalated_at"),
            escalation_count=data.get("escalation_count", 0),
            last_escalation_cause=data.get("last_escalation_cause"),
        )
    
    def is_waiting_on_human(self) -> bool:
        """True if account is currently waiting on a human response."""
        return self.waiting_on == "human"
    
    def days_since_escalation(self) -> int | None:
        """Days since first escalation, or None if never escalated."""
        if not self.escalated_at:
            return None
        try:
            esc_date = dt.date.fromisoformat(self.escalated_at)
            return (dt.date.today() - esc_date).days
        except Exception:
            return None


class TimelineStore:
    """Store and retrieve account timeline state."""
    
    def __init__(self, store_path: Path | None = None):
        if store_path is None:
            root = Path(__file__).resolve().parent.parent
            configured = os.environ.get("FLOOR_TIMELINE_PATH")
            store_path = Path(configured).expanduser() if configured else root / ".floor" / "timeline.json"
        self.store_path = store_path
        self._cache: dict[str, AccountTimeline] = {}
        self._load()
    
    def _load(self) -> None:
        """Load timeline data from JSON."""
        if not self.store_path.exists():
            self._cache = {}
            return
        
        try:
            data = json.loads(self.store_path.read_text(encoding="utf-8"))
            self._cache = {
                item["account"].lower().strip(): AccountTimeline.from_dict(item)
                for item in data.get("accounts", [])
            }
        except Exception:
            self._cache = {}
    
    def _save(self) -> None:
        """Save timeline data to JSON."""
        data = {
            "accounts": [tl.to_dict() for tl in self._cache.values()]
        }
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self.store_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    def get(self, account: str) -> AccountTimeline:
        """Get timeline for an account, creating empty one if not present."""
        account_key = account.lower().strip()
        if account_key not in self._cache:
            self._cache[account_key] = AccountTimeline(account=account)
        return self._cache[account_key]
    
    def update(
        self,
        account: str,
        *,
        last_decision: str | None = None,
        add_draft: str | None = None,
        waiting_on: WaitingOn | None = None,
        escalate: bool = False,
        escalation_cause: str | None = None,
    ) -> None:
        """Update timeline for an account.
        
        Args:
            account: Account name
            last_decision: ISO date of last decision (defaults to today)
            add_draft: Ref to add to drafts_prepared list
            waiting_on: Update waiting status
            escalate: If True, record an escalation
            escalation_cause: Text describing why escalated
        """
        tl = self.get(account)
        
        if last_decision is not None:
            tl.last_decision = last_decision
        elif last_decision is None and (add_draft or waiting_on or escalate):
            # Auto-set to today if any update happens
            tl.last_decision = dt.date.today().isoformat()
        
        if add_draft:
            if add_draft not in tl.drafts_prepared:
                tl.drafts_prepared.append(add_draft)
        
        if waiting_on is not None:
            tl.waiting_on = waiting_on
        
        if escalate:
            if not tl.escalated_at:
                tl.escalated_at = dt.date.today().isoformat()
            tl.escalation_count += 1
            tl.waiting_on = "human"
            if escalation_cause:
                tl.last_escalation_cause = escalation_cause
        
        self._save()
    
    def should_escalate(self, account: str) -> tuple[bool, str]:
        """Check if account should be escalated to humans.
        
        Returns:
            (should_escalate, reason)
            - (True, "") if okay to escalate
            - (False, "already waiting on human") if blocked
            - (False, "recently escalated (N days ago)") if too soon
        """
        tl = self.get(account)
        
        if tl.is_waiting_on_human():
            days = tl.days_since_escalation()
            if days is not None and days < 3:
                return (False, f"already waiting on human ({days} days ago)")
        
        return (True, "")
    
    def resolve_escalation(self, account: str, resolution: str = "resolved") -> None:
        """Mark an escalation as resolved (human has responded)."""
        tl = self.get(account)
        tl.waiting_on = "none"
        tl.last_decision = dt.date.today().isoformat()
        self._save()


def get_default_store() -> TimelineStore:
    """Get the runtime timeline store (untracked `.floor/` by default)."""
    return TimelineStore()
