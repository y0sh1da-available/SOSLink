# 03 — Actors, Roles, Permissions & Use Cases

> Design status: **TARGET V1**

## 1. Actors

| Code | Display name | Type | Interface |
|---|---|---|---|
| — | Resident (person in danger, relative) | No account needed | Public pages, mobile-first |
| `VOLUNTEER` | Volunteer on message duty | User | Intake screen |
| `COORDINATOR` | Coordinator | User | Command centre |
| `TEAM` | Rescue team leader | User | Mission screen on a phone |
| `ADMIN` | Administrator / group leader | User | Command centre + Administration |
| `SYSTEM` | Scheduler | Automatic | None |
| `AI` | Claude API | External system | None |

Each account has exactly one role. `ADMIN` has all `COORDINATOR` permissions.

## 2. Permission matrix

| Function | Resident | VOLUNTEER | COORDINATOR | TEAM | ADMIN |
|---|:---:|:---:|:---:|:---:|:---:|
| Send a message through the public form | ✓ | | | | |
| Look up by code (general status only) | ✓ | | | | |
| Log in, personal profile | | ✓ | ✓ | ✓ | ✓ |
| Paste messages / screenshots | | ✓ | ✓ | | ✓ |
| View messages | | Own | All | Of assigned cases | All |
| Review, edit, change priority | | | ✓ | | ✓ |
| Confirm or undo a merge | | | ✓ | | ✓ |
| Record a verification call | | Own messages | ✓ | | ✓ |
| View the command map | | | ✓ | | ✓ |
| Assign teams | | | ✓ | | ✓ |
| Mark a case as not verified | | | ✓ (with reason) | | ✓ |
| Accept or decline missions, report outcomes | | | | Own team's cases | |
| Update on a team's behalf (by phone) | | | ✓ | | ✓ |
| Reports, dashboard | | | ✓ | | ✓ |
| AI quality, audit log, data export | | | | | ✓ |
| Manage accounts, teams, disaster events, configuration | | | | | ✓ |

The backend checks permissions on every API call; `TEAM` loses access to a case's personal information when the mission ends (BR20).

## 3. Overall Use Case Diagram

The diagram shows the main features only. The full list is in section 4.

![Overall use case](usecase/ucd-overview.svg)

## 4. Use case list

| ID | Use case | Actors | Module |
|---|---|---|---|
| UC01 | Log in, log out | VOLUNTEER, COORDINATOR, TEAM, ADMIN | M1 |
| UC02 | Manage profile, change password | VOLUNTEER, COORDINATOR, TEAM, ADMIN | M1 |
| UC03 | Send a call for help through the form | Resident | M2 |
| UC04 | Look up status by code | Resident | M2 |
| UC05 | Enter messages from social media (paste text, images) | VOLUNTEER, COORDINATOR | M2 |
| UC06 | Receive messages from Zalo OA | SYSTEM | M2 |
| UC07 | AI extracts information | AI | M3 |
| UC08 | Geocode the address | SYSTEM | M3 |
| UC09 | Suggest merging duplicates | AI, SYSTEM | M3 |
| UC10 | Suggest priority | AI, SYSTEM | M3 |
| UC11 | Review and edit a case | COORDINATOR | M4 |
| UC12 | Confirm or undo a merge | COORDINATOR | M4 |
| UC13 | Record verification | VOLUNTEER, COORDINATOR | M4 |
| UC14 | View the command map and queue | COORDINATOR | M5 |
| UC15 | Assign a rescue team | COORDINATOR | M5 |
| UC16 | Alert on overdue cases | SYSTEM | M5 |
| UC17 | Accept or decline a mission | TEAM | M6 |
| UC18 | Update progress, report outcome | TEAM, COORDINATOR | M6 |
| UC19 | View dashboard, after-action report | COORDINATOR, ADMIN | M7 |
| UC20 | Measure AI quality | ADMIN | M7 |
| UC21 | Manage accounts | ADMIN | M8 |
| UC22 | Manage rescue teams | ADMIN | M8 |
| UC23 | Manage disaster events and configuration | ADMIN | M8 |
| UC24 | View audit log, anonymise data | ADMIN, SYSTEM | M8 |

**Main relationships:**
- **UC03, UC05, UC06 `«include»` UC07:** every message goes through AI, and AI failure does not block intake (BR07).
- **UC11 `«include»` UC10:** the priority suggested by AI is always reviewed by a person.
- **UC12 `«extend»` UC11:** only happens when there is a merge suggestion.

## 5. Key use case specifications

### UC05 + UC07–UC10 — From a messy message to a case awaiting review

| Item | Content |
|---|---|
| Actors | VOLUNTEER; AI; Geocoding service |
| Precondition | A disaster event is open |
| Postcondition | The original message is saved; there is a `NEW` case or a suggestion to merge into an existing case |

**Main flow**
1. The volunteer pastes the content or uploads a screenshot, with the link to the original post if available.
2. The system **saves the original immediately**, then processes asynchronously; the volunteer can keep entering messages.
3. AI returns structured information, a suggested priority, a reason and a confidence value.
4. The danger keyword set runs independently and can raise the priority.
5. The system geocodes the address and looks for likely duplicate cases.
6. The case appears in the review queue by priority.

**Exceptions**
- 3a. AI fails or exceeds 30 seconds → the case gets P2, label `CẦN NGƯỜI ĐỌC` (needs a human read), and is retried in the background.
- 3b. Confidence below 0.6 → at least P2, label `CẦN NGƯỜI ĐỌC`.
- 3c. AI judges it is not a call for help → it still enters the queue with the label `CÓ THỂ KHÔNG PHẢI CẦU CỨU` (may not be a call for help); only a person can remove it.
- 5a. Geocoding fails → the case still enters the queue with the label `CHƯA CÓ VỊ TRÍ` (no location yet), awaiting a verification call or a manual pin.

### UC11 + UC12 — Case review

1. The coordinator opens the case: original message on the left, AI-extracted information on the right.
2. They edit information, change the priority or re-pin the location. The system stores both the AI value and the final human value to measure quality (UC20).
3. If there is a duplicate suggestion: view both messages side by side, choose **Merge** or **Not a duplicate**.
4. Press **Approve** → the case moves to `TRIAGED`.

### UC15 — Team assignment

1. The coordinator picks a case in the queue. The system suggests up to 3 teams by distance, vehicle and number of active missions.
2. The coordinator picks a team and presses **Assign** → the case moves to `ASSIGNED`, and the team is notified.
3. Team accepts within 5 minutes → `EN_ROUTE`. Declines or times out → back to `TRIAGED`, and the coordinator is alerted.

### UC18 — Reporting the outcome

1. The team leader chooses: **Rescued** (enter number of people), **Someone else rescued them**, **Cannot reach** or **Not found**.
2. **Cannot reach** returns the case to the queue and raises an alert; the other outcomes end the mission.
3. While offline, the update is saved on the device and resent automatically.
4. The coordinator can update on the team's behalf when the team reports by phone; the timeline records who entered it.

---

**Related:** [User stories](04-user-stories.md) · [Scope & rules](02-scope.md) · [Information architecture](05-information-architecture.md)
