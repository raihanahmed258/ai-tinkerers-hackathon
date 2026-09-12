"""The Floor — always-on teammates that do the attention job for a workspace.

Packages:
  client.py       the tool surface the agents use (WorkspaceClient interface + MockClient over seed JSON)
  seed.py         load the fictional company into a client (mock or live)
  router.py       Router-as-code: Ops=CRM, Inbox=mail, Follow-up=tasks/calendar/selected chat
  round.py        the two-pass round orchestration  <-- the thing you build on the day
"""
