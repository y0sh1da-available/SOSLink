# 07 — Mô hình dữ liệu (Database)

> Trạng thái thiết kế: **TARGET V1** · CSDL: **PostgreSQL**
>
> Nguồn chính: [database/soslink.dbml](database/soslink.dbml). Xem sơ đồ: mở [dbdiagram.io](https://dbdiagram.io) → *Import* → *From DBML* → dán nội dung file.

## 1. Quy ước

| Quy ước | Áp dụng |
|---|---|
| Khóa chính | `uuid`; `case_events`, `audit_logs` dùng `bigserial` vì ghi nhiều |
| Thời gian | `timestamptz`, lưu UTC, hiển thị giờ Việt Nam |
| Xóa dữ liệu | Không xóa nghiệp vụ; ẩn danh theo đợt sau 90 ngày |
| Token | Chỉ lưu hash; IP cũng chỉ lưu hash |
| Mã công khai | `tracking_code` ngẫu nhiên, không suy ra được từ khóa nội bộ |

## 2. Bảng theo phân hệ

| Phân hệ | Bảng | Vai trò |
|---|---|---|
| Tài khoản | `users`, `invitations` | Tài khoản 4 vai trò, link mời |
| Cấu hình | `disaster_events`, `danger_keywords`, `admin_units` | Đợt thiên tai và thời hạn, từ khóa nguy hiểm, địa giới |
| Tiếp nhận | `reports`, `report_attachments` | **Tin gốc** và ảnh đính kèm |
| Xử lý AI | `ai_extractions` | Mỗi lần gọi AI: kết quả gốc, độ tin cậy, chi phí |
| Ca | `cases`, `merge_suggestions`, `verification_logs`, `case_events` | Ca đã gộp, đề xuất trùng, xác minh, dòng thời gian |
| Đo AI | `case_field_corrections` | Giá trị AI và giá trị người chốt |
| Điều phối | `teams`, `assignments`, `team_updates` | Đội, phân công, cập nhật có khả năng gửi lại |
| Hệ thống | `alerts`, `audit_logs`, `job_runs` | Cảnh báo, nhật ký, job |

## 3. Quan hệ chính

```text
disaster_events 1 ── n reports n ── 0..1 cases
reports 1 ── n report_attachments
reports 1 ── n ai_extractions
cases 1 ── n merge_suggestions, verification_logs, case_events, case_field_corrections
cases 0..1 ── n cases                  (merged_into_id: ca phụ trỏ tới ca chính)
cases 1 ── n assignments n ── 1 teams
assignments 1 ── n team_updates
cases 1 ── n alerts
teams 1 ── n users                     (đội trưởng, thành viên có tài khoản)
```

## 4. Thiết kế đáng chú ý

### 4.1 Tách `reports` và `cases`

Đây là quyết định quan trọng nhất của mô hình:

- **`reports`** là **sự thật gốc**: nguyên văn tin, ai gửi, kênh nào. Không bị sửa.
- **`cases`** là **cách hiểu đã chuẩn hóa**: một tình huống cần xử lý, tổng hợp từ một hoặc nhiều tin.

Nhờ tách như vậy, gộp tin chỉ là đổi `reports.case_id` và đặt `merged_into_id` trên ca phụ. Việc này **hoàn tác được và không làm mất dữ liệu** (BR01, BR09).

### 4.2 Lưu tin trước, xử lý sau

```text
1. INSERT reports (ai_status = PENDING)        ← luôn thành công nếu database còn chạy
2. INSERT cases (priority = P2, needs_human_read = true)
3. Trả mã tra cứu ngay cho người gửi
4. Worker gọi AI, ghi ai_extractions, cập nhật ca
```

Ca được tạo ngay ở mức an toàn **P2, cần người đọc**. AI chạy xong mới cập nhật. Vì vậy, AI chậm hoặc hỏng thì tin vẫn xuất hiện trong hàng đợi (BR03, BR07).

### 4.3 Ưu tiên chỉ tăng khi tự động

Khi AI xong, mức của ca được tính:

```text
mức = cao hơn của (đề xuất của AI, mức từ danger_keywords)
nếu độ tin cậy < 0,6 hoặc AI lỗi: mức tối thiểu là P2, needs_human_read = true
```

Khi có tin mới gộp vào, mức ca lấy **mức cao nhất**. Chỉ người mới hạ được, và phải có lý do (ghi vào `case_events`).

### 4.4 Chống phân công trùng

- `cases.version` dùng khóa lạc quan.
- Partial unique index: một `case_id` chỉ có một phân công ở `OFFERED`, `ACCEPTED` hoặc `EN_ROUTE`.

### 4.5 Cập nhật khi mất mạng

Máy đội tự sinh `team_updates.client_update_id`. Gửi lại nhiều lần vẫn chỉ tạo một bản ghi. `occurred_at` lưu thời điểm thật trên máy, `received_at` lưu lúc server nhận.

### 4.6 Ràng buộc

| Ràng buộc | Mục đích |
|---|---|
| `reports`: CHECK có ít nhất một trong `raw_text`, ảnh đính kèm hoặc GPS | Không có tin rỗng (kiểm ở ứng dụng với ảnh) |
| `assignments`: partial unique `case_id` khi đang hiệu lực | Một ca một đội tại một thời điểm |
| `alerts`: partial unique `(case_id, type)` khi chưa xác nhận | Không báo lặp |
| `users`: CHECK `role <> 'TEAM' OR team_id IS NOT NULL` | Đội trưởng phải thuộc đội |

### 4.7 Index cho truy vấn chính

| Truy vấn | Index |
|---|---|
| Hàng đợi điều phối | `cases (event_id, status, priority, created_at)` |
| Job cảnh báo quá hạn | `cases (status, sla_due_at)`, `assignments (status, accept_due_at)` |
| Tìm ca trùng theo điện thoại | `reports (contact_phone)` |
| Tìm ca trùng theo khoảng cách | `cases (lat, lng)`; nên dùng index GiST của PostGIS khi triển khai |
| Dòng thời gian | `case_events (case_id, created_at)` |

## 5. Ẩn danh dữ liệu

Khi `closed_at` quá 90 ngày, job `ANONYMIZE` thực hiện:

| Bảng | Xử lý |
|---|---|
| `reports` | Xóa `raw_text`, `contact_phone`, `gps_*`, `source_url`, `ip_hash`; xóa ảnh |
| `ai_extractions` | Xóa `output` |
| `cases` | Xóa `address_text`, `phones`, `summary`; làm tròn tọa độ cấp xã |
| `case_field_corrections` | Xóa `ai_value`, `final_value` nếu chứa địa chỉ, điện thoại |
| `case_events`, `verification_logs` | Xóa `note`, giá trị chứa thông tin cá nhân |

Giữ lại: số ca, mức ưu tiên, thời gian phản hồi, kết quả, chỉ số chất lượng AI.

## 6. Ánh xạ Use case → Bảng

| Use case | Bảng ghi chính |
|---|---|
| UC03, UC05, UC06 Tiếp nhận | `reports`, `report_attachments`, `cases` |
| UC07–UC10 Xử lý AI | `ai_extractions`, `cases`, `merge_suggestions` |
| UC11–UC13 Duyệt | `cases`, `case_field_corrections`, `verification_logs`, `case_events` |
| UC15–UC16 Phân công, cảnh báo | `assignments`, `alerts`, `job_runs` |
| UC17–UC18 Đội | `assignments`, `team_updates`, `cases` |
| UC20 Chất lượng AI | `ai_extractions`, `case_field_corrections`, `merge_suggestions` |
| UC24 Nhật ký, ẩn danh | `audit_logs`, `job_runs` |

---

**Liên quan:** [Phạm vi & quy tắc](02-scope.md) · [User stories](04-user-stories.md)
