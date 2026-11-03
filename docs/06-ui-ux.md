# 06 — UI/UX

> Design status: **TARGET V1** · Level: **sample interface** (not connected to a backend)
>
> All data in the images is **sample data**. The interface is in Vietnamese. All screens and states, by role: [screenshots/README.md](screenshots/README.md).

## 1. Design principles

| # | Principle | Applied as |
|---|---|---|
| 1 | **Design for people in panic** | Public form usable with one hand, pick instead of type, 112 always at the top of the page |
| 2 | **Always see the original message** | AI results never replace the original; both sit side by side |
| 3 | **AI is recognisable at a glance** | Everything AI produces has a purple border, a confidence value and a reason |
| 4 | **Dangerous cases surface on their own** | Queue sorted by priority and waiting time; overdue cases change colour |
| 5 | **No work lost when offline** | Stale data is clearly marked; form and team screens save on the device and resend automatically |
| 6 | **Few words, large buttons in the field** | Team screens use buttons at least 56 px tall |
| 7 | **Not colour alone** | Priority always has the text P1–P4; usable by colour-blind people |

## 2. Design tokens

### 2.1 Colours

| Token | Value | Used for |
|---|---|---|
| `p1` | `#B91C1C` / background `#FEE2E2` | Danger to life, overdue, Send button |
| `p2` | `#C2410C` / background `#FFEDD5` | Urgent |
| `p3` | `#A16207` / background `#FEF9C3` | Needs support |
| `p4` | `#4B5563` / background `#E5E7EB` | Information |
| `primary` | `#1168BD` / background `#E8F1FB` | Main actions, rescue teams on the map |
| `ai` | `#7A4FBF` / background `#F3ECFD` | AI-generated data |
| `success` | `#047857` / background `#D1FAE5` | Handled, connected |
| `warning` | `#B45309` / background `#FEF3C7` | Needs attention, no location, saving on device |

### 2.2 Type and spacing

| Token | Value |
|---|---|
| Font | The device's system font: Segoe UI (Windows), San Francisco (Apple), Roboto (Android), Arial as fallback; technical codes use Consolas. No web fonts, so pages stay light on weak networks and still show Vietnamese correctly offline |
| Text size | 12 secondary · 13–14 body · 16–18 headings · 22–28 figures |
| Spacing | 4 px scale |
| Touch target on phones | ≥ 44 px; team's main actions ≥ 56 px |
| Breakpoints | `< 768 px` phone · `≥ 1280 px` command centre |

### 2.3 Shared components

| Component | Notes |
|---|---|
| Priority badge | Always has the text P1–P4 and a colour |
| Case card | Level, summary, location, number of people, time left to the deadline |
| AI data field | Purple border; returns to a normal border once a person edits it |
| Map pin | Round: case; rectangle: team |
| Connection banner | Green: connected; red: data stopped updating at HH:mm |
| Confirmation modal | Only for assigning and closing cases |

## 3. Main screens

The screens below cover the main flow: **send → enter → review → assign → report outcome → report**.

### 3.1 SCR-01 · Resident sends a message (phone)

<img src="screenshots/citizen/scr-01-sos-form.png" alt="SCR-01" width="360">

- The number **112** at the top of the page: SOSLink does not replace the official emergency channel.
- A place description is required only when there is no GPS; number of people and vulnerable groups are just tapped.
- The page is very light for weak networks; when offline it keeps the content and allows resending.

### 3.2 SCR-02 + SCR-03 · Sent and lookup (phone)

<img src="screenshots/citizen/scr-02-sos-sent.png" alt="SCR-02" width="360"> <img src="screenshots/citizen/scr-03-track.png" alt="SCR-03" width="360">

- Answers what the sender is worried about: "Has anyone received my message?" (P7).
- Shows general progress only, with no personal data, because anyone with the code can see it.

### 3.3 SCR-10 · Volunteer enters a message

![SCR-10](screenshots/volunteer/scr-10-intake.png)

- Paste, press `Ctrl + Enter`, the input clears: optimised for constant repetition.
- AI processes in the background and never makes the volunteer wait.
- Volunteers see only their own messages; the menu has only Nhập tin (Enter message) and Tin của tôi (My messages).

### 3.4 SCR-20 · Command map

![SCR-20](screenshots/coordinator/scr-20-command.png)

| Area | Behaviour |
|---|---|
| Queue (left) | Sorted by priority then waiting time; countdown to the deadline; overdue cases have a red background |
| Map (centre) | Pins for cases and teams; click a pin to open the case |
| Alerts, teams (right) | Overdue cases, teams not updating; status of each team |
| Top bar | Selected event, number of P1 cases with no team, connection status |

A case with no location stays in the queue and has its own counter, so it does not vanish just because it cannot be shown on the map.

### 3.5 SCR-22 · Review case

![SCR-22](screenshots/coordinator/scr-22-review.png)

- **Left:** original message, location, verification record. **Centre:** AI result with purple border, priority with a reason. **Right:** possible duplicates.
- AI only suggests merging, with Compare and Skip buttons.
- Lowering priority requires a reason; raising does not.
- Human edits are stored to measure AI quality.

### 3.6 SCR-24 · Assign team

![SCR-24](screenshots/coordinator/scr-24-assign-team.png)

- Up to 3 suggestions with vehicle, distance and number of active missions.
- **A clear warning** that distance does not account for flooded roads. The coordinator still decides.

### 3.7 SCR-31 + SCR-32 · Rescue team (phone)

<img src="screenshots/team-leader/scr-31-mission.png" alt="SCR-31" width="360"> <img src="screenshots/team-leader/scr-32-report-result.png" alt="SCR-32" width="360">

- The most important information is on top: number of people, vulnerable groups, condition.
- Buttons to open Google Maps and to call; the original message is always visible.
- Outcomes are reported with large buttons. When offline, the screen reports how many updates are saved and that they will be sent once online.

### 3.8 SCR-40 · Event dashboard

![SCR-40](screenshots/coordinator/scr-40-dashboard.png)

- Shows whether the system is meeting its deadlines. AI quality is on SCR-53.
- The "Ca đang kẹt" (stuck cases) list says why each case is stuck: overdue, team silent, deadline close.

## 4. Screen states

Details in [05-information-architecture.md](05-information-architecture.md#7-screen-states).

## 5. Accessibility

- Text-to-background contrast ≥ 4.5:1 (WCAG AA); colour pairs need checking with a tool when building the real interface.
- Every command-centre action works from the keyboard: `J`/`K` to change case, `A` to assign, `Enter` to approve.
- The public form has real labels, and text ≥ 16 px on phones to avoid automatic zoom.

## 6. Next steps

- Have 2–3 people unfamiliar with the product try sending a message on a phone; measure time and errors.
- Show SCR-20 and SCR-22 to real coordinators and ask whether any information is missing for making decisions.

---

**Related:** [Information architecture](05-information-architecture.md) · [User stories](04-user-stories.md)
