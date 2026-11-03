# C3 — Components

> Design status: **TARGET V1** · Zooms into the two backend blocks. These components have no code yet.

## 1. API

```mermaid
flowchart TB
    web["Web App<br/><i>[Container]</i>"]
    zalo["Zalo OA<br/><i>[External System]</i>"]

    subgraph apiBox["API [Container]"]
        direction TB
        http["HTTP API<br/><i>[Component: Controllers]</i><br/>Endpoint, kiểm tra đầu vào,<br/>giới hạn tần suất, lỗi RFC 7807"]
        identity["Identity & Access<br/><i>[Component]</i><br/>Đăng nhập, JWT, vai trò,<br/>quyền theo dữ liệu"]
        intake["Intake<br/><i>[Component]</i><br/>Lưu tin gốc, tạo ca ở mức an toàn,<br/>cấp mã tra cứu"]
        review["Case Review<br/><i>[Component]</i><br/>Duyệt, sửa, ghim vị trí,<br/>xác minh, gộp, hoàn tác"]
        dispatch["Dispatch<br/><i>[Component]</i><br/>Gợi ý đội, phân công,<br/>cảnh báo"]
        missions["Missions<br/><i>[Component]</i><br/>Nhận, từ chối, báo kết quả<br/>không tạo trùng"]
        analytics["Analytics<br/><i>[Component]</i><br/>Dashboard, báo cáo,<br/>chất lượng AI, xuất Excel"]
        admin["Administration<br/><i>[Component]</i><br/>Đợt, đội, tài khoản, từ khóa"]
        audit["Audit<br/><i>[Component]</i><br/>Ghi thao tác nhạy cảm"]
        hub["Live Hub<br/><i>[Component: SignalR]</i><br/>Đẩy thay đổi, báo ai đang mở ca"]
        persistence["Persistence<br/><i>[Component: EF Core]</i><br/>Repository, giao dịch"]
        files["File Storage Adapter<br/><i>[Component]</i>"]
    end

    db[("PostgreSQL<br/><i>[Container]</i>")]
    disk[("Kho ảnh<br/><i>[Container]</i>")]

    web --> http
    zalo -.-> http
    http --> identity
    http --> intake
    http --> review
    http --> dispatch
    http --> missions
    http --> analytics
    http --> admin
    intake --> persistence
    intake --> files
    review --> persistence
    dispatch --> persistence
    missions --> persistence
    analytics --> persistence
    admin --> persistence
    identity --> persistence
    review -.-> audit
    dispatch -.-> audit
    analytics -.-> audit
    admin -.-> audit
    missions -.-> audit
    audit --> persistence
    persistence --> db
    files --> disk
    db -. "NOTIFY" .-> hub
    hub -.-> web

    style http fill:#1168bd,color:#fff
    style identity fill:#1168bd,color:#fff
    style intake fill:#0b4f9e,color:#fff
    style review fill:#1168bd,color:#fff
    style dispatch fill:#0b4f9e,color:#fff
    style missions fill:#0b4f9e,color:#fff
    style analytics fill:#1168bd,color:#fff
    style admin fill:#1168bd,color:#fff
    style audit fill:#1168bd,color:#fff
    style hub fill:#1168bd,color:#fff
    style persistence fill:#1168bd,color:#fff
    style files fill:#1168bd,color:#fff
    style web fill:#999,color:#fff
    style zalo fill:#999,color:#fff
    style db fill:#999,color:#fff
    style disk fill:#999,color:#fff
```

| Component | Owns | Does not own |
|---|---|---|
| HTTP API | Protocol, input validation, error mapping | SQL, business decisions |
| Identity & Access | Login, lockout after 5 failures, roles, data-level permissions (BR20) | What the interface shows or hides |
| Intake | Saving messages before any processing, duplicate-send protection, creating P2 cases awaiting a human read | Calling AI |
| Case Review | Case lifecycle from `NEW` to `TRIAGED`, `MERGED`, `INVALID`; stores AI values and final human values | Assigning teams |
| Dispatch | Suggesting up to 3 teams, preventing duplicate assignment, acknowledging alerts | Picking a team on its own (BR14) |
| Missions | Team updates, resending without duplicates, moving cases to `RESOLVED` or `TRIAGED` | Personal data after a mission ends (BR20) |
| Analytics | Aggregate queries, Excel export | Changing business data |
| Administration | Events, deadlines, teams, accounts, danger keywords | Hard deletes |
| Audit | Phone views, data exports, priority changes, assignments, merges, case closures (AC-US24) | The case timeline |
| Live Hub | Pushing IDs and statuses, no personal data | Business decisions |
| Persistence | Repositories, transactions, optimistic locking | Business rules |
| File Storage Adapter | Format checks, key generation, reading and writing files | Permission to view images |

Dependency direction: `HTTP API → Identity & Access → business component → Persistence → PostgreSQL`. No business component opens its own database connection.

## 2. Worker

```mermaid
flowchart TB
    subgraph workerBox["Worker [Container]"]
        direction TB
        queue["AI Queue Consumer<br/><i>[Component]</i><br/>Lấy tin PENDING,<br/>thử lại tối đa 3 lần"]
        pipeline["Extraction Pipeline<br/><i>[Component]</i><br/>Điều phối các bước xử lý một tin"]
        gateway["AI Gateway<br/><i>[Component: IAiExtractor]</i><br/>Prompt, schema cố định, timeout 30 giây"]
        priority["Priority Policy<br/><i>[Component]</i><br/>Từ khóa nguy hiểm và luật<br/>chỉ nâng, không hạ"]
        geocoding["Geocoding Adapter<br/><i>[Component: IGeocoder]</i><br/>Goong hoặc Nominatim"]
        duplicate["Duplicate Finder<br/><i>[Component]</i><br/>Trùng điện thoại, cách dưới 200 m<br/>và nội dung tương tự trong 24 giờ"]
        jobs["Scheduled Jobs<br/><i>[Component]</i><br/>SLA_CHECK mỗi phút,<br/>ANONYMIZE hằng ngày"]
        notifier["Notifier<br/><i>[Component]</i><br/>Gửi NOTIFY sau mỗi thay đổi"]
        persistence["Persistence<br/><i>[Component: EF Core]</i>"]
    end

    db[("PostgreSQL<br/><i>[Container]</i>")]
    claude["Claude API<br/><i>[External System]</i>"]
    geocoder["Dịch vụ định vị<br/><i>[External System]</i>"]

    queue --> pipeline
    pipeline --> gateway
    pipeline --> priority
    pipeline --> geocoding
    pipeline --> duplicate
    pipeline --> persistence
    jobs --> persistence
    pipeline --> notifier
    jobs --> notifier
    notifier --> db
    persistence --> db
    gateway --> claude
    geocoding --> geocoder

    style queue fill:#1168bd,color:#fff
    style pipeline fill:#0b4f9e,color:#fff
    style gateway fill:#1168bd,color:#fff
    style priority fill:#0b4f9e,color:#fff
    style geocoding fill:#1168bd,color:#fff
    style duplicate fill:#1168bd,color:#fff
    style jobs fill:#1168bd,color:#fff
    style notifier fill:#1168bd,color:#fff
    style persistence fill:#1168bd,color:#fff
    style db fill:#999,color:#fff
    style claude fill:#999,color:#fff
    style geocoder fill:#999,color:#fff
```

| Component | Owns | Does not own |
|---|---|---|
| AI Queue Consumer | Taking work, counting attempts, writing `ai_status` | Understanding message content |
| Extraction Pipeline | Order of steps; one failing step does not damage the case | Changing case status |
| AI Gateway | Calling the Claude API; model from configuration; message content is only data (BR06) | Deciding the final level |
| Priority Policy | Takes the higher of AI and keywords; confidence below 0.6 means at least P2 (BR03, BR04) | Lowering the level |
| Geocoding Adapter | Turning addresses into coordinates with a confidence value | Overriding a location a person pinned |
| Duplicate Finder | Creates `merge_suggestions` with a reason | Merging on its own (BR02, BR09) |
| Scheduled Jobs | Overdue alerts, returning cases when a team misses the acceptance deadline, anonymising after 90 days | Repeating an unacknowledged alert |
| Notifier | Tells the API something changed | Sending personal data |

## 3. Why it is split this way

- The API and the Worker share the `SOSLink.Application` business layer, so each rule is written only once.
- Priority Policy is separate from AI Gateway so it runs when AI fails, and can be tested without calling the real API.
- Only the Worker calls the Claude API, so AI errors cannot block an intake request.

---

**Previous:** [C2 — Containers](02-container.md) · **Next:** [C4 — Code](04-code.md)
