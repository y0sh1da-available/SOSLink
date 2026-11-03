# 07 — Data Model (Database)

> Design status: **TARGET V1** · Database: **PostgreSQL**
>
> Main source: [database/soslink.dbml](database/soslink.dbml). To see the diagram: open [dbdiagram.io](https://dbdiagram.io) → *Import* → *From DBML* → paste the file contents.

## 1. Conventions

| Convention | Applied as |
|---|---|
| Primary key | `uuid`; `case_events`, `audit_logs` use `bigserial` because they are write-heavy |
| Time | `timestamptz`, stored in UTC, shown in Vietnam time |
| Deleting data | Business data is not deleted; anonymised per event after 90 days |
| Tokens | Only hashes stored; IP addresses too |
| Public code | `tracking_code` is random and cannot be derived from internal keys |

## 2. Tables by module

| Module | Tables | Role |
|---|---|---|
| Accounts | `users`, `invitations` | Accounts with 4 roles, invitation links |
| Configuration | `disaster_events`, `danger_keywords`, `admin_units` | Events and deadlines, danger keywords, administrative units |
| Intake | `reports`, `report_attachments` | **Original messages** and attached images |
| AI processing | `ai_extractions` | Each AI call: raw result, confidence, cost |
| Cases | `cases`, `merge_suggestions`, `verification_logs`, `case_events` | Merged cases, duplicate suggestions, verification, timeline |
| AI measurement | `case_field_corrections` | AI values and final human values |
| Dispatch | `teams`, `assignments`, `team_updates` | Teams, assignments, resendable updates |
| System | `alerts`, `audit_logs`, `job_runs` | Alerts, audit log, jobs |

## 3. Main relationships

```text
disaster_events 1 ── n reports n ── 0..1 cases
reports 1 ── n report_attachments
reports 1 ── n ai_extractions
cases 1 ── n merge_suggestions, verification_logs, case_events, case_field_corrections
cases 0..1 ── n cases                  (merged_into_id: secondary case points to main case)
cases 1 ── n assignments n ── 1 teams
assignments 1 ── n team_updates
cases 1 ── n alerts
teams 1 ── n users                     (team leader, members with accounts)
```

## 4. Notable design points

### 4.1 Separating `reports` and `cases`

This is the most important decision in the model:

- **`reports`** is the **original truth**: the message verbatim, who sent it, which channel. It is never edited.
- **`cases`** is the **normalised understanding**: one situation to handle, compiled from one or more messages.

Because of this split, merging only changes `reports.case_id` and sets `merged_into_id` on the secondary case. It **can be undone and loses no data** (BR01, BR09).

### 4.2 Save first, process later

```text
1. INSERT reports (ai_status = PENDING)        ← always succeeds while the database is up
2. INSERT cases (priority = P2, needs_human_read = true)
3. Return the tracking code to the sender at once
4. Worker calls AI, writes ai_extractions, updates the case
```

A case is created right away at the safe level **P2, needs a human read**. Only when AI finishes is it updated. So if AI is slow or down, the message still appears in the queue (BR03, BR07).

### 4.3 Priority only rises automatically

When AI finishes, the case's level is computed as:

```text
level = the higher of (AI suggestion, level from danger_keywords)
if confidence < 0.6 or AI failed: level is at least P2, needs_human_read = true
```

When a new message merges in, the case takes the **highest level**. Only a person can lower it, and must give a reason (written to `case_events`).

### 4.4 Preventing duplicate assignment

- `cases.version` uses optimistic locking.
- Partial unique index: one `case_id` has only one assignment in `OFFERED`, `ACCEPTED` or `EN_ROUTE`.

### 4.5 Updates while offline

The team's device generates `team_updates.client_update_id` itself. Resending many times creates only one record. `occurred_at` stores the real time on the device, `received_at` the time the server received it.

### 4.6 Constraints

| Constraint | Purpose |
|---|---|
| `reports`: CHECK at least one of `raw_text`, attached image or GPS | No empty messages (checked in the application for images) |
| `assignments`: partial unique `case_id` while active | One case, one team at a time |
| `alerts`: partial unique `(case_id, type)` while unacknowledged | No repeat alerts |
| `users`: CHECK `role <> 'TEAM' OR team_id IS NOT NULL` | A team leader must belong to a team |

### 4.7 Indexes for the main queries

| Query | Index |
|---|---|
| Command queue | `cases (event_id, status, priority, created_at)` |
| Overdue alert job | `cases (status, sla_due_at)`, `assignments (status, accept_due_at)` |
| Duplicates by phone | `reports (contact_phone)` |
| Duplicates by distance | `cases (lat, lng)`; a PostGIS GiST index is preferable on deployment |
| Timeline | `case_events (case_id, created_at)` |

## 5. Data anonymisation

When `closed_at` is more than 90 days old, the `ANONYMIZE` job does the following:

| Table | Handling |
|---|---|
| `reports` | Clears `raw_text`, `contact_phone`, `gps_*`, `source_url`, `ip_hash`; deletes images |
| `ai_extractions` | Clears `output` |
| `cases` | Clears `address_text`, `phones`, `summary`; rounds coordinates to commune level |
| `case_field_corrections` | Clears `ai_value`, `final_value` if they contain addresses or phone numbers |
| `case_events`, `verification_logs` | Clears `note` and values containing personal information |

Kept: number of cases, priority levels, response times, outcomes, AI quality metrics.

## 6. Use case → Table mapping

| Use case | Main tables written |
|---|---|
| UC03, UC05, UC06 Intake | `reports`, `report_attachments`, `cases` |
| UC07–UC10 AI processing | `ai_extractions`, `cases`, `merge_suggestions` |
| UC11–UC13 Review | `cases`, `case_field_corrections`, `verification_logs`, `case_events` |
| UC15–UC16 Assignment, alerts | `assignments`, `alerts`, `job_runs` |
| UC17–UC18 Teams | `assignments`, `team_updates`, `cases` |
| UC20 AI quality | `ai_extractions`, `case_field_corrections`, `merge_suggestions` |
| UC24 Audit log, anonymisation | `audit_logs`, `job_runs` |

---

**Related:** [Scope & rules](02-scope.md) · [User stories](04-user-stories.md)
