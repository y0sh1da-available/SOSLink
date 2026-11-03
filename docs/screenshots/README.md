# Ảnh chụp giao diện SOSLink

Chụp từ prototype tĩnh, chưa nối backend. Toàn bộ dữ liệu trong ảnh là **dữ liệu mẫu**. Danh sách màn hình theo mã `SCR` nằm ở [05-information-architecture.md](../05-information-architecture.md#3-danh-sách-màn-hình).

- [Người dân](#người-dân)
- [Tình nguyện viên](#tình-nguyện-viên)
- [Điều phối viên](#điều-phối-viên)
- [Đội trưởng](#đội-trưởng)
- [Quản trị viên](#quản-trị-viên)
- [Dùng chung](#dùng-chung)

## Người dân

### SCR-01 · Gửi tin cầu cứu

![SCR-01](citizen/scr-01-sos-form.png)

### SCR-02 · Đã gửi, hiện mã

![SCR-02](citizen/scr-02-sos-sent.png)

### SCR-03 · Tra cứu tình trạng

![SCR-03](citizen/scr-03-track.png)

### Trạng thái · Mất mạng khi gửi tin

![Mất mạng khi gửi tin](citizen/state-offline-sos-form.png)

## Tình nguyện viên

### SCR-10 · Nhập tin mới

![SCR-10](volunteer/scr-10-intake.png)

### SCR-11 · Tin của tôi

![SCR-11](volunteer/scr-11-my-messages.png)

## Điều phối viên

### SCR-20 · Bản đồ điều phối

![SCR-20](coordinator/scr-20-command.png)

### SCR-21 · Chờ duyệt

![SCR-21](coordinator/scr-21-review-queue.png)

### SCR-22 · Duyệt ca

![SCR-22](coordinator/scr-22-review.png)

### SCR-23 · So sánh gộp tin

![SCR-23](coordinator/scr-23-compare-merge.png)

### SCR-24 · Phân công đội

![SCR-24](coordinator/scr-24-assign-team.png)

### SCR-25 · Chi tiết ca

![SCR-25](coordinator/scr-25-case-detail.png)

### SCR-25 · Cập nhật hộ đội

![Cập nhật hộ đội](coordinator/scr-25b-update-for-team.png)

### SCR-26 · Tất cả ca

![SCR-26](coordinator/scr-26-all-cases.png)

### SCR-27 · Cảnh báo

![SCR-27](coordinator/scr-27-alerts.png)

### SCR-40 · Dashboard theo đợt

![SCR-40](coordinator/scr-40-dashboard.png)

### SCR-41 · Báo cáo sau sự kiện

![SCR-41](coordinator/scr-41-post-event-report.png)

### Trạng thái · Đang tải

![Đang tải ở Bản đồ](coordinator/state-loading-command.png)

![Đang tải ở Tất cả ca](coordinator/state-loading-all-cases.png)

### Trạng thái · Hàng đợi rỗng

![Hàng đợi rỗng](coordinator/state-empty-review-queue.png)

### Trạng thái · AI đang đọc

![AI đang đọc](coordinator/state-ai-reading.png)

### Trạng thái · AI lỗi

![AI lỗi ở một ca](coordinator/state-ai-failed.png)

![AI hỏng cả loạt](coordinator/state-ai-down-review-queue.png)

### Trạng thái · Chưa có vị trí

![Chưa có vị trí](coordinator/state-no-location-command.png)

### Trạng thái · Mất kết nối

![Mất kết nối ở Bản đồ](coordinator/state-offline-command.png)

![Mất kết nối ở Duyệt ca](coordinator/state-offline-review.png)

### Trạng thái · Xung đột

![Xung đột khi phân công](coordinator/state-conflict-assign.png)

![Xung đột khi duyệt ca](coordinator/state-conflict-review.png)

## Đội trưởng

### SCR-30 · Nhiệm vụ của đội

![SCR-30](team-leader/scr-30-team-missions.png)

### SCR-31 · Chi tiết nhiệm vụ

![SCR-31](team-leader/scr-31-mission.png)

### SCR-32 · Báo kết quả

![SCR-32](team-leader/scr-32-report-result.png)

### Trạng thái · Mất mạng

![Mất mạng ở Chi tiết nhiệm vụ](team-leader/state-offline-mission.png)

![Mất mạng ở Nhiệm vụ của đội](team-leader/state-offline-team-missions.png)

## Quản trị viên

Quản trị viên có toàn bộ quyền của điều phối viên, nên phần này chỉ có màn hình riêng và 2 ảnh minh họa.

### SCR-50 · Đợt thiên tai, cấu hình

![SCR-50](admin/scr-50-events.png)

### SCR-51 · Tài khoản

![SCR-51](admin/scr-51-users.png)

![Mời người mới](admin/scr-51b-invite-user.png)

### SCR-52 · Đội cứu hộ

![SCR-52](admin/scr-52-teams.png)

![Sửa đội](admin/scr-52b-edit-team.png)

### SCR-53 · Chất lượng AI

![SCR-53](admin/scr-53-ai-quality.png)

### SCR-54 · Nhật ký

![SCR-54](admin/scr-54-audit-log.png)

### Bản đồ điều phối khi đăng nhập bằng quản trị viên

![Bản đồ điều phối của quản trị viên](admin/admin-command.png)

### Dashboard khi đăng nhập bằng quản trị viên

![Dashboard của quản trị viên](admin/admin-dashboard.png)

## Dùng chung

### SCR-04 · Đăng nhập

![SCR-04](common/scr-04-login.png)

### SCR-05 · Kích hoạt tài khoản

![SCR-05](common/scr-05-activate.png)

### SCR-06 · Hồ sơ cá nhân

![SCR-06](common/scr-06-profile.png)

### SCR-90 · Không có quyền

![SCR-90](common/scr-90-403.png)

### SCR-91 · Không tìm thấy trang

![SCR-91](common/scr-91-404.png)
