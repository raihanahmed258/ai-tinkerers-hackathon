# Brightline Payroll — Ambiguous seed report

**Workspace:** hackathon-aitinkerers  
**Seed date (today):** 2026-09-12 (day offsets converted with `today + timedelta`)  
**MCP namespace:** `user-ambiguous`  
**Pipeline:** Brightline Sales `95725671-e7e5-49e2-9aa2-0b989032a127`  
**Calendar:** default `f3e34034-d441-43cf-bdfc-2b0e1a1f0223`  
**Owner on all CRM/tasks:** Raihan Ahmed `0d46ed86-0fc0-4f8c-8c27-7d79526494c1` (fictional Brightline humans dana/priya/marcus/theo are not Ambiguous users)

---

## Counts created

| Entity | Count | Notes |
|--------|------:|-------|
| Pipeline | 1 | Brightline Sales + 7 stages |
| Companies | 20 | All seed accounts |
| Person contacts | 4 | Priority accounts only (Lena, Sam, Rosa, Jordan) |
| Deals | 20 | Titles include seed id `D-10x` |
| Deal notes (`log_activity`) | 13 | All deals with non-empty seed notes |
| Tasks | 9 | T-1…T-9 linked to deals where present |
| Calendar events | 9 | E-1…E-9; past events used `force: true` |
| Chat messages (#sales) | 15 | Prefixed `[SEED chat · −Nd] Speaker:` |
| Chat messages (#ops-team) | 11 + 1 SEED MAIL | Same prefix; plus mail limitation summary |
| Draft emails | 3 | M-1, M-2, M-3 stubs only — **not sent** |
| Inbound mail threads | 0 | API cannot invent inbound customer mail |

---

## Priority accounts (MUST for demo)

### Copper Kettle Group (D-101)
- **Company:** `4e8c98ed-7a91-4abf-9759-a575116188fa`
- **Contact:** Lena Ortiz `c809f3c3-9b84-4084-8997-40aae7967af8`
- **Deal:** `c5984537-8e5c-4709-9149-a0db6575f2d7` — Contract, $84k, close 2026-09-19
- **Task:** T-1 `a5cedb0a-37fa-454f-ad41-f0e3b427c08e`
- **Event:** E-1 `ee48c905-f106-4ea3-aa47-d752a6643d7f`
- **Draft:** `1bc62018-058d-4530-b7ee-155bc7b523f0`

### Marigold Diners (D-102)
- **Company:** `7afb7ddc-8237-4bbd-b917-50ec9dc4a09f`
- **Contact:** Sam Okafor `35229bdc-38e5-4b92-88ee-94b7a913908e`
- **Deal:** `02486422-5096-421b-9fd3-ca283e36a4c2` — Closed Won — Implementation, won, $42k, close 2026-08-12
- **Task:** T-2 `17554843-3b16-480f-8ab6-47c12b39fe1c`
- **Event:** E-2 `52497b6b-3226-439e-b592-b6ff3f5daf5e`
- **Draft:** `39b26d24-1a45-4197-82e2-fdf305328da7`

### Ember Grill (D-107)
- **Company:** `88981aa0-46f1-4a4e-9762-6bc75a05a40b`
- **Contact:** Rosa Delgado `9c8bf363-1022-4223-95a8-9a7cbee28409`
- **Deal:** `d4c24e45-ebc6-42d6-9b54-7e7e48241f5a` — Customer — Live, won, $30k, close 2025-08-08
- **Event:** E-3 `a8101c20-d5b3-4329-851f-6853f34132eb`
- **Draft:** `28e61ba0-803b-4f5f-98e3-094a8b2f4ada`

### Pine & Salt (D-105)
- **Company:** `cb57606c-242c-4ead-8ba3-01224ff5ec9d`
- **Contact:** Jordan Reyes `15d0507c-653c-45a1-8919-92f121926967`
- **Deal:** `19996120-3198-4152-b3bd-f08154b2a7b8` — Discovery, $120k, close 2026-11-11
- **Event:** E-4 `df50f3ff-095a-4626-ac35-db365666c07b`
- **Mail note:** M-4 bounce (champion left) documented in #ops-team `[SEED MAIL]` only — no inbound message

---

## Remaining deal Ambiguous IDs

| Seed | Title | Deal ID |
|------|-------|---------|
| D-103 | Sunset Taco | `31e73570-239b-4cb2-9690-e76e69444622` |
| D-104 | Harbor Fish Co. | `fbe1c4f0-c00e-40dd-b040-3fd360d62c8d` |
| D-106 | Bluebird Bakeries | `bf2af63f-1b5f-4d01-aa73-1bd3f0d7c0b5` |
| D-108 | Juniper Hospitality | `fdf9854a-9ce4-44ea-95bc-6ba29367d589` |
| D-109 | Two Forks Cafe | `8160bcdb-4859-4fbf-beab-1b3f0c25fcbb` |
| D-110 | Saffron House | `d69b34fc-67fe-4602-ae39-5404113358a6` |
| D-111 | Dockside Oyster Bar | `d335f648-eaf5-4d83-a730-69da53052f5b` |
| D-112 | Northgate Brewing | `0c6e97b4-994c-48e0-9867-6606ce610360` |
| D-113 | Lantern & Vine | `136a25f6-4736-4187-bd96-a114c07e9694` |
| D-114 | Meridian Steakhouse | `285ca54d-22f5-4ca3-b5d0-63f55b066404` |
| D-115 | Gold Leaf Catering | `0fe70320-838a-40b3-903e-88f232ddb401` |
| D-116 | Fig & Thistle | `ee7f1221-3daf-4665-bf33-ed5283db814b` |
| D-117 | Cobalt Kitchen | `60dac5f6-0f00-4ba4-be56-19cb8fd76bd2` |
| D-118 | Prairie Table | `b58ba940-a6a6-4a88-a191-5d4e65749acb` |
| D-119 | Wren & Barrow | `6b407f9b-c5cb-45bb-841d-1754372ea557` |
| D-120 | Alder Street Bistro | `784364ab-71ec-4ae3-aa4c-0c6847ed926a` |

### Pipeline stages
| Stage | ID |
|-------|-----|
| Discovery | `9c1eaf8b-ac91-4564-8461-b8b26c31d2e6` |
| Proposal | `fb09debb-abf5-4768-8198-a29f63e4f77f` |
| Negotiation | `8d8ddffa-073b-4fd2-a2a2-4602a5fed3b7` |
| Contract | `61d3e818-7859-4ac5-8a86-c3607f5ca5ed` |
| Closed Won — Implementation | `7aae85e6-f173-4d87-97e6-dbe50b0051ab` |
| Customer — Live | `1e54820b-cada-4eab-8711-6e06348fcff7` |
| Closed Lost | `f5d6b4f2-2a96-4f2c-96f0-5a54ca519233` |

---

## Chat channels used
- **#sales** `b0781716-0fd8-4b5a-b110-0842cc6f294e` — 15 seed messages  
- **#ops-team** `52661440-bb72-4207-8199-1c31857d6c45` — 11 seed messages + `[SEED MAIL]` summary  
- **Not touched:** agents-floor, attention (per instructions)

---

## Mail limitations (blocker for Inbox watcher)

Ambiguous MCP exposes `list_inbox`, `create_draft_email`, `send_email`, etc., but **no tool to inject fictional inbound customer threads**. Therefore:

1. **Inbound mail not created** — Inbox agent cannot see M-1…M-12 as real inbox messages.
2. **Mitigations applied:**
   - `[SEED MAIL]` summary posted to #ops-team with critical threads (M-1, M-2, M-3, M-4 bounce, M-9).
   - Three **drafts only** for expected outbound replies (M-1 Copper Kettle, M-2 Marigold, M-3 Ember Grill).
3. **`send_email` was never called.** No Project 1 bots contacted.
4. **Side note:** `create_event` with `.example` attendees reported `external_invites_sent` for those fictional addresses (calendar invite path). Domains are non-routable `.example`; no intentional customer email send.

---

## Failures / caveats

- Fictional Brightline people (Dana/Priya/Marcus/Theo) are **not** workspace users — ownership assigned to Raihan; seed owner names live in titles/notes/descriptions.
- Deal `last_activity_days` / `stage_entered_days` cannot be backdated via create API — noted in activity text only.
- Chat history is authored as Raihan with speaker labels in content (cannot post as Priya et al.).
- Calendar past events required `force: true`.
- Ops Theo chat line −7d was lightly completed from truncated seed text for readability.

---

## Success criteria check

- [x] Four priority accounts exist as deals with notes  
- [x] Chat history in sales + ops-team  
- [x] Tasks and calendar events for those accounts  
- [x] SEED_REPORT.md written (this file)  
- [x] No external emails sent via `send_email`; no Project 1 contact  
