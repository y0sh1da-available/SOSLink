# C4 — Code

> Design status: **TARGET V1** · Class-level design for the two core flows. No code yet; each file's location is in the [code structure](../../08-code-structure.md).

## 1. Message intake and AI processing

```mermaid
flowchart TB
    subgraph apiSide["API"]
        public["PublicController, ReportsController<br/><i>[ASP.NET Core Controller]</i>"]
        intake["IntakeService<br/><i>[C# class]</i><br/>Lưu tin, tạo ca P2, cấp mã"]
    end

    subgraph workerSide["Worker"]
        job["AiExtractionJob<br/><i>[BackgroundService]</i>"]
        pipeline["ExtractionPipeline<br/><i>[C# class]</i>"]
        matcher["DangerKeywordMatcher<br/><i>[C# class]</i>"]
        policy["PriorityPolicy<br/><i>[C# class]</i><br/>Chỉ nâng, không hạ"]
        finder["DuplicateFinder<br/><i>[C# class]</i>"]
    end

    subgraph ports["Application: giao diện"]
        repo["IReportRepository, ICaseRepository<br/><i>[C# interface]</i>"]
        queue["IReportQueue<br/><i>[C# interface]</i>"]
        extractor["IAiExtractor<br/><i>[C# interface]</i>"]
        geocoder["IGeocoder<br/><i>[C# interface]</i>"]
        storage["IFileStorage<br/><i>[C# interface]</i>"]
        notifier["IRealtimeNotifier<br/><i>[C# interface]</i>"]
    end

    subgraph infra["Infrastructure"]
        efRepo["EfReportRepository, EfCaseRepository"]
        pgQueue["PostgresReportQueue<br/>FOR UPDATE SKIP LOCKED"]
        claude["ClaudeAiExtractor"]
        goong["GoongGeocoder, NominatimGeocoder"]
        local["LocalFileStorage"]
        pgNotify["PostgresNotifier"]
    end

    public --> intake
    intake --> repo
    intake --> storage
    job --> queue
    job --> pipeline
    pipeline --> extractor
    pipeline --> matcher
    pipeline --> policy
    pipeline --> geocoder
    pipeline --> finder
    pipeline --> repo
    pipeline --> notifier
    efRepo -.-> repo
    pgQueue -.-> queue
    claude -.-> extractor
    goong -.-> geocoder
    local -.-> storage
    pgNotify -.-> notifier

    style intake fill:#0b4f9e,color:#fff
    style pipeline fill:#0b4f9e,color:#fff
    style policy fill:#0b4f9e,color:#fff
```

The final level is computed by `PriorityPolicy`, not taken directly from AI:

```text
level = the higher of (AI suggestion, level from danger_keywords)
if confidence < 0.6 or AI failed: level is at least P2, needs_human_read = true
```

```mermaid
sequenceDiagram
    actor U as Người gửi
    participant A as API
    participant D as PostgreSQL
    participant W as Worker
    participant C as Claude API
    participant G as Dịch vụ định vị
    actor K as Điều phối viên

    U->>A: POST /public/reports
    A->>D: Một giao dịch: lưu reports (PENDING), lưu cases (P2, cần người đọc)
    A-->>U: 201, mã tra cứu
    Note over U,A: Người gửi có mã ngay, không chờ AI
    W->>D: Lấy tin PENDING bằng SKIP LOCKED
    W->>C: Gửi tin, chờ tối đa 30 giây
    alt AI trả kết quả
        C-->>W: JSON theo schema cố định
        W->>W: Chạy từ khóa nguy hiểm, tính mức ưu tiên
        W->>G: Đổi địa chỉ thành tọa độ
        G-->>W: Tọa độ và độ tin cậy, hoặc không tìm thấy
        W->>D: Lưu ai_extractions, cập nhật cases, tạo merge_suggestions
    else AI lỗi hoặc quá 30 giây
        W->>D: Ghi FAILED hoặc TIMEOUT, giữ P2 và nhãn cần người đọc
        Note over W,D: Thử lại ở nền, tối đa 3 lần
    end
    W->>D: NOTIFY case_changed
    D-->>A: Tín hiệu có ca thay đổi
    A-->>K: SignalR caseChanged
    K->>A: GET /cases/{caseId}
    A-->>K: Tin gốc cạnh kết quả AI
```

## 2. Assignment and outcome reporting

```mermaid
flowchart TB
    subgraph apiSide["API"]
        dispatchCtl["DispatchController<br/><i>[ASP.NET Core Controller]</i>"]
        missionCtl["MissionsController<br/><i>[ASP.NET Core Controller]</i>"]
        hub["LiveHub, LiveEventBridge<br/><i>[SignalR]</i>"]
    end

    subgraph app["Application"]
        dispatch["DispatchService<br/><i>[C# class]</i><br/>Phân công, hủy phân công"]
        suggester["TeamSuggester<br/><i>[C# class]</i><br/>Khoảng cách, phương tiện, số nhiệm vụ"]
        mission["MissionService<br/><i>[C# class]</i><br/>Nhận, từ chối, nhận cập nhật"]
        machine["CaseStateMachine<br/><i>[C# class]</i><br/>Các bước chuyển hợp lệ"]
        alerts["AlertService<br/><i>[C# class]</i>"]
        access["CaseAccessPolicy<br/><i>[C# class]</i><br/>Quyền theo dữ liệu, BR20"]
        ports["ICaseRepository, IAssignmentRepository,<br/>ITeamUpdateRepository, IUnitOfWork<br/><i>[C# interface]</i>"]
    end

    subgraph workerSide["Worker"]
        sla["SlaCheckJob<br/><i>[BackgroundService]</i><br/>Mỗi phút"]
    end

    ef["EF Core repositories<br/><i>[Infrastructure]</i>"]

    dispatchCtl --> dispatch
    dispatchCtl --> suggester
    missionCtl --> mission
    dispatch --> access
    dispatch --> machine
    dispatch --> ports
    mission --> access
    mission --> machine
    mission --> alerts
    mission --> ports
    sla --> alerts
    sla --> machine
    alerts --> ports
    ef -.-> ports

    style dispatch fill:#0b4f9e,color:#fff
    style mission fill:#0b4f9e,color:#fff
    style machine fill:#0b4f9e,color:#fff
```

Two layers block duplicate assignment: `UPDATE cases ... WHERE version = @version` in the application, and a partial unique index on `assignments.case_id` in the database.

```mermaid
sequenceDiagram
    actor L as Lan
    actor S as Sơn
    participant A as API
    participant D as PostgreSQL
    actor T as Đội 3

    L->>A: GET /cases/{caseId}/team-suggestions
    S->>A: GET /cases/{caseId}/team-suggestions
    A-->>L: Tối đa 3 đội, kèm cảnh báo về khoảng cách
    A-->>S: Tối đa 3 đội, kèm cảnh báo về khoảng cách
    L->>A: POST /cases/{caseId}/assignments (Đội 3, version 2)
    S->>A: POST /cases/{caseId}/assignments (Đội 5, version 2)
    A->>D: Lệnh của Lan: UPDATE cases WHERE version = 2
    D-->>A: 1 dòng, tạo assignments (OFFERED)
    A-->>L: 201, ca sang ASSIGNED
    A-->>T: SignalR missionOffered, còn 5 phút để nhận
    A->>D: Lệnh của Sơn: UPDATE cases WHERE version = 2
    D-->>A: 0 dòng, version đã là 3
    A-->>S: 409 CASE_ALREADY_ASSIGNED, Lan đã giao Đội 3
    T->>A: POST /missions/{assignmentId}/accept
    A-->>T: 200, nhiệm vụ sang EN_ROUTE
    Note over T,A: Mất mạng khi báo kết quả
    T->>T: Lưu vào outbox, sinh clientUpdateId
    T->>A: PUT /missions/{assignmentId}/updates/{clientUpdateId}
    A->>D: Lưu team_updates, ca sang RESOLVED
    A-->>T: 201
    T->>A: Gửi lại cùng clientUpdateId vì chưa nhận được phản hồi
    A-->>T: 200, không tạo bản ghi mới
```

## 3. Shared rules

1. Controllers contain neither SQL nor business rules.
2. Services depend on interfaces, not directly on PostgreSQL or the Claude API.
3. Every case status change goes through `CaseStateMachine` and writes a row to `case_events` (BR17).
4. Data-level permissions are always checked in Application, so the API and the Worker share one set of rules.
5. `IAiExtractor` only returns data. It holds no reference to any service with write access.
6. Write tests for `PriorityPolicy` and `CaseStateMachine` first, because errors in these two affect safety.

---

**Previous:** [C3 — Components](03-component.md) · **Related:** [Code structure](../../08-code-structure.md) · [API](../../api/README.md) · [Scope & rules](../../02-scope.md)
