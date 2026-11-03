# SOSLink API

> Design status: **TARGET V1** · Implementation status: **no backend yet**

The contract is in [openapi.yaml](openapi.yaml) (OpenAPI 3.0.4): 58 paths, 68 operations. It is the source of truth for paths, input and output data, errors and permissions. When the backend is written, controllers and DTOs must follow this file exactly.

Sample data and error messages in the examples stay in Vietnamese, because the product interface is Vietnamese.

## 1. Scope

| Group | Serves |
|---|---|
| Public | Residents send messages and images, look up by code |
| Auth, Profile | Login, invitation links, personal profile |
| Events, Config | Disaster events, deadlines, danger keywords, administrative units |
| Reports | Original messages entered by volunteers |
| Cases | Queue, review, edit, pin location, verification, merge, timeline |
| Dispatch | Team suggestions, assignment, cancelling, telling a team about new information |
| Alerts, Teams | Overdue alerts, team management |
| Missions | Teams accept, decline and report outcomes, even offline |
| Analytics | Dashboard, after-action report, AI quality, Excel export |
| Users, Audit | Accounts, audit log |
| Webhooks, System | Zalo OA, service health |

The original message table is named `reports`, so statistical reports use the `/analytics` prefix to avoid a name clash.

## 2. Addresses and formats

- Base path: `/api/v1`. Development machine: `http://localhost:5000/api/v1`.
- Data: `application/json`. Errors: `application/problem+json`. Image upload: `multipart/form-data`.
- Time: ISO 8601 in UTC; the frontend converts to Vietnam time for display.
- A field with no value does not appear in the JSON. Only the AI output keeps `null` for fields the AI is unsure about.
- Pagination: `page` starts at 1, `pageSize` defaults to 20, maximum 100. Results have `items` and `meta`. An empty list still returns `200`.

## 3. Authentication and permissions

```http
Authorization: Bearer ACCESS_TOKEN
```

The JWT lasts 60 minutes, with no refresh token. The server checks account status on every request, so a disabled account loses access on its next request. Logging out means the client deletes the token and locally stored data.

Each operation has three extension fields:

| Field | Meaning |
|---|---|
| `x-roles` | Roles allowed to call it. `PUBLIC` means no token needed |
| `x-scope` | Further limits by data, for example `VOLUNTEER` sees only their own messages |
| `x-stories` | User stories the operation serves |

Hiding a button in the frontend is only for usability. The backend always checks again.

## 4. Errors

Errors follow RFC 7807. The frontend relies on `errorCode`, not `detail`. `traceId` is for finding the request in logs.

| `errorCode` | HTTP | When |
|---|---|---|
| `VALIDATION_FAILED` | 400 | Invalid data; `errors` lists each field |
| `PASSWORD_INCORRECT` | 400 | Wrong old password when changing password |
| `AUTH_INVALID_CREDENTIALS` | 401 | Wrong login or account locked, same message for both |
| `AUTH_TOKEN_INVALID` | 401 | Missing, wrong or expired token |
| `ZALO_SIGNATURE_INVALID` | 401 | Webhook with a wrong signature |
| `ACCESS_DENIED` | 403 | No permission, or the mission has ended |
| `RESOURCE_NOT_FOUND` | 404 | Not found |
| `TRACKING_CODE_NOT_FOUND` | 404 | Wrong tracking code |
| `CASE_VERSION_CONFLICT` | 409 | The case was just edited by someone else |
| `CASE_STATE_INVALID` | 409 | The case is not in a state that allows this operation |
| `CASE_ALREADY_ASSIGNED` | 409 | The case is already assigned; the error names the team and who assigned it |
| `EVENT_CLOSED` | 409 | No open event, or the event is closed |
| `EVENT_SELECTION_REQUIRED` | 409 | Several events are open and none was chosen |
| `MISSION_NOT_OFFERED` | 409 | Acceptance deadline passed or mission cancelled |
| `NO_ACTIVE_ASSIGNMENT` | 409 | The case has no team on the way |
| `ATTACHMENT_LIMIT_REACHED` | 409 | The message already has 4 images |
| `BUSINESS_CONFLICT` | 409 | Other conflicts, for example duplicate email or keyword |
| `INVITATION_INVALID` | 410 | Invitation link wrong, expired or already used |
| `FILE_TOO_LARGE` | 413 | Image larger than 5 MB |
| `UNSUPPORTED_MEDIA_TYPE` | 415 | Not a JPEG, PNG or WebP image |
| `PRIORITY_REASON_REQUIRED` | 422 | Priority lowered without a reason |
| `RATE_LIMITED` | 429 | Too many calls |
| `RATE_LIMIT_CONFIRM_REQUIRED` | 429 | Over 10 messages in 10 minutes; confirm and resend |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected error |

## 5. Three hard situations

**Two people acting on one case.** Every command that changes a case sends its current `version`. A version mismatch returns `409`. Assignment also has a partial unique index on `assignments.case_id`, so even if two commands arrive together only one succeeds (AC-US15).

**Weak network, repeated sending.** The device generates an ID and resends until it gets a response: `idempotencyKey` for messages, `clientUpdateId` for team updates. The first call returns `201`, later calls return `200` and create no new record (BR18). An update arriving after the assignment has ended is still saved, but does not change the case status (`applied` is `false`).

**Phone numbers.** `getCase` returns masked numbers only. Seeing the full number requires `revealCasePhones`, and each call writes `VIEW_PHONE` to the audit log (BR22). `getMission` returns full numbers so the team can call while offline, and is logged too. Known limit: original messages are shown verbatim (BR05), so a number the sender wrote inside a message is not masked.

## 6. Realtime

OpenAPI cannot describe two-way connections, so this part is documented here. The backend uses SignalR at `/hubs/live`, with the same JWT as REST. The hub sends only IDs and statuses, no personal data. The client receives the signal and then calls REST for details.

| Direction | Name | Data | Used for |
|---|---|---|---|
| Client calls | `JoinEvent(eventId)` | | Receive changes in an event (`COORDINATOR`, `ADMIN`) |
| Client calls | `JoinCase(caseId)`, `LeaveCase(caseId)` | | Show who has a case open (AC-US11) |
| Server sends | `caseChanged` | `caseId`, `version`, `status`, `priority` | Map and queue update within 5 seconds (US14) |
| Server sends | `alertRaised` | `alertId`, `caseId`, `type` | Alerts |
| Server sends | `teamChanged` | `teamId`, `status` | Team column on the map |
| Server sends | `caseViewers` | `caseId`, `names` | Show who else has the case open |
| Server sends | `missionOffered`, `missionChanged` | `assignmentId`, `status` | Teams receive missions (grouped by team) |

When disconnected, the frontend shows the banner "Dữ liệu dừng cập nhật lúc HH:mm" (data stopped updating at HH:mm) and locks the assign button. After reconnecting, the client calls `listCases` with `updatedSince` to fetch what it missed.

V1 can only notify a team while the page is open. Web Push comes later. So a team without the page open misses the acceptance deadline, the case returns to the queue and the coordinator is alerted (BR15).

## 7. Sample API calls

A resident sends a message:

```bash
curl --request POST \
  --url http://localhost:5000/api/v1/public/reports \
  --header "Content-Type: application/json" \
  --data '{
    "idempotencyKey": "6f0a4c1e-2b7d-4e9a-8c11-5d3e7a9b0c21",
    "gps": { "lat": 13.0, "lng": 109.215 },
    "situationText": "nước lên tới mái nhà",
    "peopleCount": 3,
    "vulnerable": ["ELDERLY", "INFANT"]
  }'
```

Look up by code:

```bash
curl --url http://localhost:5000/api/v1/public/track/SOS-7K2Q
```

A volunteer enters a message with an image:

```bash
curl --request POST \
  --url http://localhost:5000/api/v1/reports \
  --header "Authorization: Bearer ACCESS_TOKEN" \
  --form "eventId=7b1e2c44-5a10-4c7e-9a31-2f6d8e0a1b01" \
  --form "idempotencyKey=1c9e6f20-7d41-4b0a-9e55-0a2b3c4d5e6f" \
  --form "text=cứu vs ạ, nhà e ở gần cầu Sông Ba thôn 3 hòa thịnh" \
  --form "photos=@anh-chup.png"
```

A coordinator assigns a team:

```bash
curl --request POST \
  --url http://localhost:5000/api/v1/cases/c1045000-0000-4000-8000-000000001045/assignments \
  --header "Authorization: Bearer ACCESS_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{ "version": 2, "teamId": "d0000005-0000-4000-8000-000000000005" }'
```

A team reports an outcome. Resending to the same address creates no new record:

```bash
curl --request PUT \
  --url http://localhost:5000/api/v1/missions/b1042000-0000-4000-8000-000000000001/updates/f0000001-0000-4000-8000-000000000001 \
  --header "Authorization: Bearer ACCESS_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{ "kind": "OUTCOME", "occurredAt": "2026-11-03T07:58:00Z", "outcome": "RESCUED", "peopleRescued": 3 }'
```

## 8. Viewing and validating

Paste the contents of `openapi.yaml` into [Swagger Editor](https://editor.swagger.io), or validate with:

```bash
npx @redocly/cli lint docs/api/openapi.yaml
```

This reports 4 warnings, all intentional: `info-license` because the project has not chosen a licence, `no-server-example.com` because a development address is listed, and `operation-4xx-response` on `getFormStatus` and `getHealth` because those two operations have no 4xx errors.

## 9. Story → Operation mapping

The right column lists `operationId` values. AI reading, geocoding and duplicate search run in the Worker, so US07–US10 only have operations that read and edit the results.

| Story | Operations |
|---|---|
| US01 Log in | `login` · `logout` |
| US02 Profile | `getMyProfile` · `updateMyProfile` · `changeMyPassword` |
| US03 Send message | `getFormStatus` · `submitPublicReport` · `uploadPublicAttachment` |
| US04 Look up | `trackReport` |
| US05 Paste message | `createReport` · `listReports` · `getReport` · `downloadReportAttachment` |
| US06 Zalo OA | `receiveZaloMessage` |
| US07 Extraction | `getReport` · `getCase` |
| US08 Geocoding | `getCase` · `pinCaseLocation` |
| US09 Duplicate suggestions | `getCase` · `rejectMergeSuggestion` |
| US10 Priority suggestions | `listCases` · `getCase` · `updateCase` |
| US11 Review | `downloadReportAttachment` · `listCases` · `getCase` · `updateCase` · `reviewCase` · `invalidateCase` · `getCaseTimeline` |
| US12 Merge, undo | `mergeCase` · `unmergeCase` · `rejectMergeSuggestion` · `notifyTeamOfNewInfo` |
| US13 Verification | `listReports` · `getCase` · `revealCasePhones` · `addCaseVerification` |
| US14 Map, queue | `getEventOverview` · `listAdminUnits` · `listCases` · `listTeams` |
| US15 Assignment | `suggestTeams` · `assignTeam` · `cancelAssignment` |
| US16 Alerts | `getEventOverview` · `listAlerts` · `acknowledgeAlert` |
| US17 Receive mission | `downloadReportAttachment` · `listMyMissions` · `getMission` · `acceptMission` · `declineMission` |
| US18 Report outcome | `resolveCase` · `getCaseTimeline` · `submitMissionUpdate` |
| US19 Dashboard | `getEventDashboard` · `getAfterActionReport` · `saveLessonsLearned` · `exportEventData` |
| US20 AI quality | `getAiQuality` |
| US21 Accounts | `inspectInvitation` · `acceptInvitation` · `listUsers` · `inviteUser` · `getUser` · `updateUser` · `disableUser` · `enableUser` · `resendInvitation` |
| US22 Teams | `listTeams` · `createTeam` · `getTeam` · `updateTeam` |
| US23 Disaster events | `getFormStatus` · `listEvents` · `openEvent` · `getEvent` · `updateEvent` · `closeEvent` · `listDangerKeywords` · `addDangerKeyword` · `removeDangerKeyword` |
| US24 Audit log, anonymisation | `listEvents` · `revealCasePhones` · `exportEventData` · `listAuditLogs` |

## 10. API design decisions

| Situation | Handling |
|---|---|
| Several events can be open at once (AC-US23) but the public form has no event picker | With one open event the server assigns it. With several, `getFormStatus` returns a list for the frontend to offer |
| The form has a place field and a situation field, but `reports` only has `raw_text` | The server joins both fields into `raw_text` on save |
| A weak network can fail the whole request if text and images are sent together | The public form sends text first, images separately once it has a code |
| The lookup page needs a status for not-verified and merged cases | Not verified shows as `CLOSED`, with no reason. A merged case follows the main case |
| The invitation link is in the page URL | The API takes the token in the body so it stays out of API logs |
| No email service yet | `inviteUser` returns `inviteUrl` once, for the administrator to send themselves |
| A team leader is an account, not a column in `teams` | `leaderName` comes from the `TEAM` account belonging to the team |
| Team location used for suggestions | Taken from `gps` when a team accepts or sends an update; an administrator can edit it with `updateTeam` |
| `X-ZEvent-Signature` | Header name taken from [Zalo's Mini App webhook documentation](https://miniapp.zaloplatforms.com/documents/open-apis/partner/event-review-mini-app). Needs checking against the Zalo OA documentation when registering the OA |

---

**Related:** [User stories](../04-user-stories.md) · [Scope & rules](../02-scope.md) · [Data model](../07-data-model.md) · [C4](../architecture/c4/README.md) · [Code structure](../08-code-structure.md)
