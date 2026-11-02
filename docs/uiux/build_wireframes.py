"""Sinh wireframe low-fi (SVG) cho các màn hình chính của SOSLink.

Chạy: python docs/uiux/build_wireframes.py
Kết quả: docs/uiux/wf-*.svg — nhúng vào docs/06-ui-ux.md.

Quy ước màu: đỏ/cam/vàng/xám = mức ưu tiên P1–P4; xanh = hành động chính; tím = phần do AI tạo.
Dữ liệu trong wireframe là giả lập.
"""

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent
FONT = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"
K = {
    "bg": "#ffffff", "canvas": "#f3f4f6", "line": "#d1d5db", "box": "#f9fafb",
    "text": "#111827", "muted": "#6b7280", "faint": "#9ca3af",
    "primary": "#1168bd", "primary_bg": "#e8f1fb",
    "ai": "#7a4fbf", "ai_bg": "#f3ecfd",
    "ok": "#047857", "ok_bg": "#d1fae5",
    "warn": "#b45309", "warn_bg": "#fef3c7",
    "p1": "#b91c1c", "p1_bg": "#fee2e2",
    "p2": "#c2410c", "p2_bg": "#ffedd5",
    "p3": "#a16207", "p3_bg": "#fef9c3",
    "p4": "#4b5563", "p4_bg": "#e5e7eb",
    "side": "#111827",
}


class Canvas:
    def __init__(self, w, h, title):
        self.w, self.h, self.title, self.parts = w, h, title, []

    def rect(self, x, y, w, h, fill=K["bg"], stroke=K["line"], r=6, dash=None, sw=1):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" '
                          f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def text(self, x, y, s, size=13, color=K["text"], weight=400, anchor="start"):
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" '
                          f'text-anchor="{anchor}">{escape(s)}</text>')

    def line(self, x1, y1, x2, y2, color=K["line"], sw=1):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"/>')

    def circle(self, x, y, r, fill, stroke=None):
        s = stroke or fill
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{s}"/>')

    def image(self, x, y, w, h):
        self.rect(x, y, w, h, fill=K["box"])
        self.line(x, y, x + w, y + h)
        self.line(x + w, y, x, y + h)

    def button(self, x, y, w, label, kind="primary", h=34, size=13):
        s = {"primary": (K["primary"], K["primary"], "#fff"), "secondary": (K["bg"], K["line"], K["text"]),
             "ai": (K["ai_bg"], K["ai"], K["ai"]), "danger": (K["p1"], K["p1"], "#fff"),
             "ok": (K["ok"], K["ok"], "#fff")}[kind]
        self.rect(x, y, w, h, fill=s[0], stroke=s[1])
        self.text(x + w / 2, y + h / 2 + size / 2 - 1, label, size, s[2], 600, "middle")

    def field(self, x, y, w, label, value="", ai=False, h=34):
        self.text(x, y - 6, label, 12, K["muted"], 600)
        fill, stroke = (K["ai_bg"], K["ai"]) if ai else (K["bg"], K["line"])
        self.rect(x, y, w, h, fill=fill, stroke=stroke)
        self.text(x + 10, y + h / 2 + 5, value, 13, K["text"] if value else K["faint"])

    def badge(self, x, y, label, kind="p4"):
        fg, bg = {"p1": (K["p1"], K["p1_bg"]), "p2": (K["p2"], K["p2_bg"]), "p3": (K["p3"], K["p3_bg"]),
                  "p4": (K["p4"], K["p4_bg"]), "ai": (K["ai"], K["ai_bg"]), "ok": (K["ok"], K["ok_bg"]),
                  "warn": (K["warn"], K["warn_bg"]), "primary": (K["primary"], K["primary_bg"])}[kind]
        w = 12 + len(label) * 6.6
        self.rect(x, y, w, 20, fill=bg, stroke=bg, r=10)
        self.text(x + w / 2, y + 14, label, 11, fg, 700, "middle")
        return w

    def desktop_shell(self, active, title):
        self.rect(0, 0, self.w, self.h, fill=K["canvas"], stroke=K["line"], r=0)
        self.rect(0, 0, 64, self.h, fill=K["side"], stroke=K["side"], r=0)
        self.text(32, 34, "SL", 15, "#fff", 700, "middle")
        items = ["Bản đồ", "Duyệt", "Ca", "Nhập", "Báo cáo", "Quản trị"]
        for i, it in enumerate(items):
            y = 70 + i * 62
            on = it == active
            self.rect(10, y, 44, 50, fill="#374151" if on else K["side"], stroke="#374151" if on else K["side"])
            self.circle(32, y + 17, 8, "#fff" if on else "#6b7280")
            self.text(32, y + 42, it, 10, "#fff" if on else "#9ca3af", 600 if on else 400, "middle")
        self.rect(64, 0, self.w - 64, 52, fill=K["bg"], stroke=K["line"], r=0)
        self.text(84, 32, title, 16, K["text"], 700)
        self.button(self.w - 560, 10, 210, "Đợt: Diễn tập lũ  ▾", "secondary", 32, 12)
        self.badge(self.w - 336, 16, "7 ca P1 chưa có đội", "p1")
        self.circle(self.w - 170, 26, 5, K["ok"])
        self.text(self.w - 160, 31, "Đang kết nối", 12, K["muted"])
        self.circle(self.w - 66, 26, 13, K["box"], K["line"])
        self.badge(self.w - 62, 6, "3", "p1")
        self.circle(self.w - 28, 26, 13, K["line"])

    def mobile_frame(self, title, right=None):
        self.rect(0, 0, self.w, self.h, fill=K["canvas"], stroke=K["side"], r=26, sw=2)
        self.rect(0, 0, self.w, 60, fill=K["bg"], stroke=K["line"], r=0)
        self.text(18, 38, title, 16, K["text"], 700)
        if right:
            self.text(self.w - 18, 38, right, 13, K["p1"], 700, "end")

    def save(self, name):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {self.w} {self.h}" font-family="{FONT}"><title>{escape(self.title)}</title>'
               + "".join(self.parts) + "</svg>")
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        return name


def sos_form():
    c = Canvas(390, 844, "SCR-01 Gửi tin cầu cứu")
    c.mobile_frame("Gửi tin cầu cứu")
    c.rect(14, 72, 362, 56, fill=K["p1"], stroke=K["p1"], r=10)
    c.text(195, 96, "Nguy hiểm ngay? Hãy gọi 112", 15, "#fff", 700, "middle")
    c.text(195, 116, "Bấm để gọi", 12, "#fee2e2", 400, "middle")
    c.text(14, 158, "Bạn đang ở đâu?", 14, K["text"], 700)
    c.button(14, 170, 362, "Lấy vị trí của tôi", "primary", 44, 14)
    c.field(14, 242, 362, "Hoặc mô tả nơi ở (thôn, xã, gần đâu)", "Gần cầu Sông Ba, thôn 3...", h=44)
    c.text(14, 318, "Có bao nhiêu người?", 14, K["text"], 700)
    for i, t in enumerate(["1", "2", "3", "4", "5+"]):
        on = t == "3"
        c.rect(14 + i * 74, 330, 66, 44, fill=K["primary_bg"] if on else K["bg"], stroke=K["primary"] if on else K["line"], sw=2 if on else 1)
        c.text(47 + i * 74, 358, t, 15, K["primary"] if on else K["text"], 700, "middle")
    c.text(14, 402, "Có ai cần chú ý?", 14, K["text"], 700)
    for i, (t, on) in enumerate([("Trẻ nhỏ", True), ("Người già", True), ("Bị thương", False), ("Thai phụ", False)]):
        x, y = 14 + (i % 2) * 185, 414 + (i // 2) * 50
        c.rect(x, y, 177, 42, fill=K["primary_bg"] if on else K["bg"], stroke=K["primary"] if on else K["line"], sw=2 if on else 1)
        c.text(x + 88, y + 26, t, 14, K["primary"] if on else K["text"], 600, "middle")
    c.field(14, 548, 362, "Tình trạng hiện tại", "Nước lên tới mái nhà...", h=60)
    c.field(14, 636, 362, "Số điện thoại liên lạc", "09xx xxx 234", h=44)
    c.button(14, 700, 362, "GỬI TIN", "danger", 56, 18)
    c.text(195, 780, "Chỉ mã và trạng thái được hiển thị công khai.", 11, K["muted"], 400, "middle")
    c.text(195, 798, "Thông tin của bạn chỉ dùng để cứu hộ.", 11, K["muted"], 400, "middle")
    return c.save("wf-01-sos-form")


def sos_track():
    c = Canvas(390, 844, "SCR-02/03 Đã gửi và tra cứu")
    c.mobile_frame("Tình trạng tin của bạn")
    c.rect(14, 72, 362, 110, fill=K["ok_bg"], stroke=K["ok_bg"], r=10)
    c.text(195, 104, "Đã nhận được tin của bạn", 16, K["ok"], 700, "middle")
    c.text(195, 136, "Mã tra cứu", 12, K["muted"], 400, "middle")
    c.text(195, 164, "SOS-7K2Q", 24, K["text"], 700, "middle")
    c.text(14, 220, "Tiến trình", 14, K["text"], 700)
    steps = [("Đã nhận tin", "14:02", True), ("Đang xử lý", "14:05", True), ("Đã có đội nhận", "14:11", True), ("Đã xử lý", "", False)]
    for i, (t, tm, on) in enumerate(steps):
        y = 256 + i * 66
        c.circle(34, y, 11, K["ok"] if on else K["bg"], K["ok"] if on else K["line"])
        if i < 3:
            c.line(34, y + 11, 34, y + 55, K["ok"] if steps[i + 1][2] else K["line"], 2)
        c.text(58, y + 5, t, 15, K["text"] if on else K["faint"], 600)
        c.text(372, y + 5, tm, 12, K["muted"], 400, "end")
    c.rect(14, 512, 362, 84, fill=K["p1_bg"], stroke=K["p1_bg"], r=10)
    c.text(30, 542, "Nếu tình hình xấu đi, hãy gọi 112.", 14, K["p1"], 700)
    c.text(30, 570, "Giữ điện thoại, đội có thể gọi cho bạn.", 13, K["text"])
    c.button(14, 616, 362, "Gửi thêm thông tin mới", "secondary", 48, 14)
    c.text(195, 700, "Trang này không hiện tên, điện thoại và địa chỉ.", 12, K["muted"], 400, "middle")
    return c.save("wf-02-sos-track")


def intake():
    c = Canvas(1280, 720, "SCR-10 Nhập tin")
    c.desktop_shell("Nhập", "Nhập tin từ mạng xã hội")
    c.rect(88, 72, 640, 620)
    c.text(112, 108, "Dán nội dung bài đăng", 15, K["text"], 700)
    c.rect(112, 122, 592, 250, fill=K["box"])
    for i, t in enumerate(["cứu vs ạ, nhà e ở gần cầu Sông Ba thôn 3 hòa thịnh,", "nc lên tới mái r, có 2 cụ già vs bé 8 tháng, đt 09xxxxx234", "goi ko dc thì gọi số chị e"]):
        c.text(128, 154 + i * 24, t, 14)
    c.rect(112, 388, 592, 90, fill=K["bg"], dash="4 3")
    c.text(408, 438, "Kéo thả hoặc dán ảnh chụp màn hình (tối đa 4 ảnh)", 13, K["muted"], 600, "middle")
    c.field(112, 516, 592, "Link bài gốc (không bắt buộc)", "https://facebook.com/...")
    c.button(112, 580, 592, "Lưu tin (Ctrl + Enter)", "primary", 48, 15)
    c.text(408, 656, "Tin được lưu ngay. AI xử lý ở nền, bạn có thể nhập tin kế tiếp.", 13, K["muted"], 400, "middle")
    c.rect(752, 72, 500, 620)
    c.text(776, 108, "Tin vừa nhập", 15, K["text"], 700)
    c.text(1228, 108, "Hôm nay: 42 tin", 12, K["muted"], 400, "end")
    rows = [("nhà e ở gần cầu Sông Ba...", "AI đang đọc", "ai", "14:02"), ("cần thuyền gấp xóm 5...", "P1 · Chờ duyệt", "p1", "14:01"),
            ("mẹ tôi ở Hòa Xuân Tây...", "P2 · Có đội", "p2", "13:58"), ("xin mì tôm nước uống...", "P3 · Chờ phân công", "p3", "13:55"),
            ("ai biết tin chú Ba không...", "Có thể không phải cầu cứu", "p4", "13:52"), ("đoàn cứu trợ ở đâu...", "Cần người đọc", "warn", "13:50")]
    for i, (t, s, k, tm) in enumerate(rows):
        y = 128 + i * 82
        c.rect(776, y, 452, 70, fill=K["box"])
        c.text(792, y + 26, t, 14)
        c.text(1212, y + 26, tm, 12, K["muted"], 400, "end")
        c.badge(792, y + 38, s, k)
    return c.save("wf-10-intake")


def command():
    c = Canvas(1440, 860, "SCR-20 Bản đồ điều phối")
    c.desktop_shell("Bản đồ", "Bản đồ điều phối")
    c.rect(64, 52, 410, 808, fill=K["bg"], stroke=K["line"], r=0)
    c.text(84, 86, "Hàng đợi", 15, K["text"], 700)
    for i, (t, k) in enumerate([("P1 7", "p1"), ("P2 15", "p2"), ("P3 23", "p3"), ("Chưa vị trí 4", "warn")]):
        c.badge(84 + i * 76, 98, t, k)
    cases = [("P1", "p1", "Trên mái nhà, có trẻ 8 tháng", "Thôn 3, Hòa Thịnh · 3 người", "Quá hạn 4 phút", True),
             ("P1", "p1", "Nước đang lên, người già", "Xóm 5, Hòa Xuân · 2 người", "Còn 3 phút", False),
             ("P1", "p1", "Người bị thương, cô lập", "Vị trí chưa rõ · 4 người", "Còn 6 phút", False),
             ("P2", "p2", "Hết nước uống, 2 trẻ em", "An Thạch · 5 người", "Còn 18 phút", False),
             ("P2", "p2", "Cô lập, có người già", "Đông Hòa · 6 người", "Còn 25 phút", False),
             ("P3", "p3", "Cần nhu yếu phẩm", "Tuy An · 12 người", "Còn 1 giờ 40", False)]
    for i, (p, k, t, sub, sla, over) in enumerate(cases):
        y = 132 + i * 98
        c.rect(80, y, 378, 88, fill=K["p1_bg"] if over else K["box"], stroke=K["p1"] if over else K["line"])
        c.badge(92, y + 12, p, k)
        c.text(130, y + 27, t, 14, K["text"], 600)
        c.text(92, y + 52, sub, 12, K["muted"])
        c.text(92, y + 74, sla, 12, K["p1"] if over or "Còn 3" in sla else K["muted"], 700 if over else 400)
        c.button(374, y + 52, 74, "Phân công", "primary", 28, 11)
    # bản đồ
    c.rect(474, 52, 700, 808, fill="#e5efe9", stroke=K["line"], r=0)
    c.parts.append('<path d="M474 300 C 620 340, 760 260, 900 340 S 1100 460, 1174 420" fill="none" stroke="#93c5fd" stroke-width="26"/>')
    c.parts.append('<path d="M650 52 L 700 300 L 820 560 L 840 860" fill="none" stroke="#fff" stroke-width="7"/>')
    c.text(494, 84, "Bản đồ (OpenStreetMap)", 12, K["muted"], 600)
    for (x, y, lab, k) in [(640, 330, "P1", "p1"), (760, 290, "P1", "p1"), (980, 400, "P2", "p2"), (860, 500, "P2", "p2"), (600, 610, "P3", "p3"), (1040, 660, "P3", "p3")]:
        c.circle(x, y, 17, K[k], "#fff")
        c.text(x, y + 4, lab, 11, "#fff", 700, "middle")
    for (x, y, lab) in [(700, 420, "Đội 2"), (930, 580, "Đội 5")]:
        c.rect(x - 30, y - 14, 60, 28, fill=K["primary"], stroke="#fff")
        c.text(x, y + 5, lab, 12, "#fff", 700, "middle")
    c.rect(494, 770, 300, 70, fill="#ffffff", stroke=K["line"])
    c.text(510, 796, "Tròn: ca (màu và nhãn theo mức ưu tiên)", 12, K["muted"])
    c.text(510, 820, "Chữ nhật: đội cứu hộ", 12, K["muted"])
    # cột đội và cảnh báo
    c.rect(1174, 52, 266, 808, fill=K["bg"], stroke=K["line"], r=0)
    c.text(1192, 86, "Cảnh báo", 15, K["text"], 700)
    for i, (t, s) in enumerate([("Ca P1 quá 10 phút chưa có đội", "Thôn 3, Hòa Thịnh"), ("Đội 3 chưa cập nhật 30 phút", "Ca An Thạch")]):
        y = 100 + i * 76
        c.rect(1190, y, 234, 66, fill=K["p1_bg"], stroke=K["p1_bg"])
        c.text(1202, y + 26, t, 12, K["p1"], 700)
        c.text(1202, y + 48, s, 12, K["text"])
    c.text(1192, 286, "Đội cứu hộ", 15, K["text"], 700)
    teams = [("Đội 1 · Thuyền", "Sẵn sàng", "ok"), ("Đội 2 · Thuyền", "Đang đến", "primary"), ("Đội 3 · Xe", "Đang đến", "primary"),
             ("Đội 4 · Đi bộ", "Sẵn sàng", "ok"), ("Đội 5 · Thuyền", "Sẵn sàng", "ok"), ("Đội 6 · Xe", "Nghỉ", "p4")]
    for i, (t, s, k) in enumerate(teams):
        y = 302 + i * 62
        c.rect(1190, y, 234, 52, fill=K["box"])
        c.text(1202, y + 22, t, 13, K["text"], 600)
        c.badge(1202, y + 28, s, k)
    return c.save("wf-20-command")


def review():
    c = Canvas(1440, 820, "SCR-22 Duyệt ca")
    c.desktop_shell("Duyệt", "Duyệt ca #1042")
    c.rect(88, 72, 500, 724)
    c.text(112, 106, "Tin gốc", 15, K["text"], 700)
    c.badge(170, 92, "Facebook", "p4")
    c.badge(244, 92, "Nhập bởi Lan · 14:02", "p4")
    c.rect(112, 122, 452, 150, fill=K["box"])
    for i, t in enumerate(["cứu vs ạ, nhà e ở gần cầu Sông Ba thôn 3 hòa thịnh,", "nc lên tới mái r, có 2 cụ già vs bé 8 tháng,", "đt 09xxxxx234 goi ko dc thì gọi số chị e"]):
        c.text(128, 154 + i * 26, t, 14)
    c.text(112, 300, "Vị trí", 15, K["text"], 700)
    c.rect(112, 314, 452, 240, fill="#e5efe9")
    c.circle(330, 430, 15, K["p1"], "#fff")
    c.text(330, 434, "P1", 10, "#fff", 700, "middle")
    c.rect(124, 326, 200, 26, fill="#fff")
    c.text(134, 344, "Độ tin cậy vị trí: Trung bình", 12, K["warn"], 600)
    c.button(424, 322, 130, "Ghim lại vị trí", "secondary", 30, 12)
    c.text(112, 584, "Xác minh", 15, K["text"], 700)
    c.button(112, 598, 150, "Đã gọi được", "secondary", 38)
    c.button(274, 598, 180, "Không liên lạc được", "secondary", 38)
    c.field(112, 666, 452, "Ghi chú cuộc gọi", "", h=60)
    # kết quả AI
    c.rect(612, 72, 500, 724)
    c.text(636, 106, "AI trích xuất", 15, K["ai"], 700)
    c.badge(752, 92, "Độ tin cậy 0,86", "ai")
    c.field(636, 138, 452, "Địa chỉ", "Gần cầu Sông Ba, thôn 3, Hòa Thịnh", ai=True)
    c.field(636, 200, 214, "Điện thoại", "09xxxxx234", ai=True)
    c.field(874, 200, 214, "Số người", "3", ai=True)
    c.field(636, 262, 452, "Nhóm yếu thế", "Người già (2) · Trẻ sơ sinh (1)", ai=True)
    c.field(636, 324, 452, "Tình trạng", "Nước ngập tới mái nhà", ai=True)
    c.rect(636, 380, 452, 120, fill=K["p1_bg"], stroke=K["p1"])
    c.text(652, 410, "Mức ưu tiên đề xuất", 12, K["muted"], 600)
    c.badge(652, 420, "P1 · Nguy hiểm tính mạng", "p1")
    c.text(652, 464, "Lý do: nước tới mái, có trẻ 8 tháng và 2 người già.", 13)
    c.text(652, 486, "Từ khóa nguy hiểm: \"mái\", \"8 tháng\".", 13, K["muted"])
    c.text(636, 532, "Đổi mức", 12, K["muted"], 600)
    for i, (p, k) in enumerate([("P1", "p1"), ("P2", "p2"), ("P3", "p3"), ("P4", "p4")]):
        c.rect(636 + i * 116, 542, 104, 38, fill=K[k + "_bg"], stroke=K[k], sw=2 if p == "P1" else 1)
        c.text(688 + i * 116, 566, p, 14, K[k], 700, "middle")
    c.text(636, 606, "Hạ mức ưu tiên phải ghi lý do", 12, K["muted"])
    c.button(636, 640, 214, "Không xác thực…", "secondary", 44)
    c.button(874, 640, 214, "Duyệt và phân công", "primary", 44)
    c.text(636, 726, "Duyệt không làm mất tin gốc. Giá trị bạn sửa được dùng để đo chất lượng AI.", 12, K["muted"])
    # ca trùng
    c.rect(1136, 72, 280, 724)
    c.text(1156, 106, "Có thể trùng (2)", 15, K["text"], 700)
    for i, (t, r) in enumerate([("#1038 · nhà chị Hoa thôn 3...", "Trùng số điện thoại"), ("#1031 · gần cầu Sông Ba có...", "Cách 150 m, nội dung tương tự")]):
        y = 124 + i * 170
        c.rect(1152, y, 248, 156, fill=K["box"])
        c.text(1166, y + 28, t, 12, K["text"], 600)
        c.badge(1166, y + 42, r, "ai")
        c.text(1166, y + 88, "AI chỉ đề xuất, không tự gộp", 11, K["muted"])
        c.button(1166, y + 104, 106, "So sánh", "secondary", 36)
        c.button(1282, y + 104, 106, "Bỏ qua", "secondary", 36)
    return c.save("wf-22-review")


def dispatch():
    c = Canvas(1440, 820, "SCR-24 Phân công đội")
    c.desktop_shell("Bản đồ", "Bản đồ điều phối")
    c.rect(64, 52, 1376, 768, fill="#111827", stroke="#111827", r=0)
    c.parts[-1] = c.parts[-1].replace('fill="#111827"', 'fill="#111827" fill-opacity="0.55"', 1)
    c.rect(400, 96, 640, 660, r=10)
    c.text(428, 134, "Phân công ca #1042", 18, K["text"], 700)
    c.badge(630, 118, "P1", "p1")
    c.rect(428, 150, 584, 92, fill=K["box"])
    c.text(444, 178, "Trên mái nhà, có trẻ 8 tháng và 2 người già", 14, K["text"], 600)
    c.text(444, 202, "Gần cầu Sông Ba, thôn 3, Hòa Thịnh · 3 người", 13, K["muted"])
    c.text(444, 226, "Xác minh: Đã gọi được lúc 14:06", 13, K["ok"], 600)
    c.text(428, 276, "Đội được gợi ý", 14, K["text"], 700)
    teams = [("Đội 1", "Thuyền · 1,2 km · 0 nhiệm vụ", True), ("Đội 5", "Thuyền · 3,4 km · 0 nhiệm vụ", False), ("Đội 4", "Đi bộ · 0,8 km · 1 nhiệm vụ", False)]
    for i, (t, s, on) in enumerate(teams):
        y = 290 + i * 84
        c.rect(428, y, 584, 74, fill=K["primary_bg"] if on else K["bg"], stroke=K["primary"] if on else K["line"], sw=2 if on else 1)
        c.circle(456, y + 37, 9, K["primary"] if on else K["bg"], K["primary"] if on else K["line"])
        c.text(482, y + 32, t, 15, K["text"], 700)
        c.text(482, y + 56, s, 13, K["muted"])
        if i == 0:
            c.badge(884, y + 26, "Phù hợp nhất", "primary")
    c.rect(428, 552, 584, 58, fill=K["warn_bg"], stroke=K["warn_bg"])
    c.text(444, 576, "Khoảng cách đường chim bay, chưa tính đường ngập.", 13, K["warn"], 600)
    c.text(444, 598, "Hãy xác nhận với đội trước khi điều động.", 13, K["warn"])
    c.text(428, 642, "Đội có 5 phút để nhận; quá hạn ca quay lại hàng đợi.", 12, K["muted"])
    c.button(428, 672, 180, "Hủy", "secondary", 48)
    c.button(748, 672, 264, "Phân công Đội 1", "primary", 48, 15)
    return c.save("wf-24-dispatch")


def mission():
    c = Canvas(390, 844, "SCR-31 + SCR-32 Nhiệm vụ của đội")
    c.mobile_frame("Nhiệm vụ #1042", "P1")
    c.rect(14, 72, 362, 76, fill=K["p1_bg"], stroke=K["p1"], r=10)
    c.text(30, 102, "3 người · 2 người già, 1 trẻ sơ sinh", 15, K["text"], 700)
    c.text(30, 128, "Nước ngập tới mái nhà", 14, K["p1"], 600)
    c.rect(14, 160, 362, 170, fill="#e5efe9", r=10)
    c.circle(195, 240, 15, K["p1"], "#fff")
    c.text(195, 244, "P1", 10, "#fff", 700, "middle")
    c.text(30, 354, "Gần cầu Sông Ba, thôn 3, Hòa Thịnh", 14, K["text"], 600)
    c.button(14, 368, 175, "Mở Google Maps", "secondary", 48, 14)
    c.button(201, 368, 175, "Gọi 09xxxxx234", "secondary", 48, 14)
    c.text(14, 446, "Tin gốc", 14, K["text"], 700)
    c.rect(14, 458, 362, 96, fill=K["bg"], r=10)
    for i, t in enumerate(["cứu vs ạ, nhà e ở gần cầu Sông Ba thôn 3,", "nc lên tới mái r, có 2 cụ già vs bé 8 tháng"]):
        c.text(28, 490 + i * 24, t, 13)
    c.rect(14, 566, 362, 34, fill=K["warn_bg"], stroke=K["warn_bg"], r=8)
    c.text(28, 588, "Đã lưu, sẽ gửi khi có mạng (1 cập nhật)", 12, K["warn"], 600)
    c.button(14, 612, 362, "ĐÃ CỨU", "ok", 60, 18)
    c.button(14, 682, 175, "Không tiếp cận được", "secondary", 56, 13)
    c.button(201, 682, 175, "Không tìm thấy", "secondary", 56, 13)
    c.button(14, 748, 362, "Đã có người khác cứu", "secondary", 56, 14)
    return c.save("wf-31-mission")


def dashboard():
    c = Canvas(1280, 780, "SCR-40 Dashboard theo đợt")
    c.desktop_shell("Báo cáo", "Dashboard đợt thiên tai")
    c.text(88, 80, "Dữ liệu trong wireframe là giả lập", 12, K["muted"])
    kp = [("Tin đã nhận", "1.284", "Trong đó 31% trùng"), ("Ca thật", "886", "Sau khi gộp"), ("Ca P1 chưa có đội", "7", "Quá hạn: 1"), ("Đã xử lý", "612 ca", "1.740 người được hỗ trợ")]
    for i, (a, b, d) in enumerate(kp):
        x = 88 + i * 292
        c.rect(x, 92, 276, 96)
        c.text(x + 16, 118, a, 12, K["muted"], 600)
        c.text(x + 16, 150, b, 24, K["p1"] if i == 2 else K["text"], 700)
        c.text(x + 16, 174, d, 12, K["muted"])
    c.rect(88, 204, 584, 280)
    c.text(108, 234, "Thời gian từ tin đến phân công (trung vị)", 14, K["text"], 700)
    for i, (p, v, k, sla) in enumerate([("P1", 8, "p1", "SLA 10 phút"), ("P2", 22, "p2", "SLA 30 phút"), ("P3", 74, "p3", "SLA 2 giờ")]):
        y = 268 + i * 66
        c.badge(108, y - 2, p, k)
        c.rect(160, y, min(v * 4.4, 340), 24, fill=K[k], stroke=K[k], r=4)
        c.text(160 + min(v * 4.4, 340) + 10, y + 17, f"{v} phút", 13, K["text"], 600)
        c.text(652, y + 17, sla, 12, K["muted"], 400, "end")
    c.rect(688, 204, 564, 280)
    c.text(708, 234, "Chất lượng AI trong đợt", 14, K["ai"], 700)
    for i, (t, v) in enumerate([("Địa chỉ đúng không cần sửa", 78), ("Số điện thoại đúng", 97), ("Gợi ý trùng được chấp nhận", 84), ("Ca P1 được AI nhận ra", 96)]):
        y = 262 + i * 54
        c.text(708, y + 4, t, 13)
        c.rect(708, y + 12, 420, 14, fill=K["box"], r=7)
        c.rect(708, y + 12, 420 * v / 100, 14, fill=K["ai"], stroke=K["ai"], r=7)
        c.text(1232, y + 24, f"{v}%", 13, K["text"], 700, "end")
    c.text(88, 516, "Ca cần xem lại", 14, K["text"], 700)
    c.rect(88, 528, 1164, 228)
    hdr = [("Ca", 108), ("Mức", 220), ("Tình trạng", 300), ("Thời gian chờ", 780), ("Trạng thái", 960)]
    for t, x in hdr:
        c.text(x, 556, t, 12, K["muted"], 600)
    rows = [("#1042", "P1", "p1", "Thôn 3, Hòa Thịnh · trên mái nhà", "14 phút", "Chờ phân công", "warn"),
            ("#1037", "P1", "p1", "Chưa có vị trí · người bị thương", "11 phút", "Chưa có vị trí", "warn"),
            ("#1021", "P2", "p2", "An Thạch · đội không cập nhật", "42 phút", "Đang đến", "primary"),
            ("#1009", "P2", "p2", "Không liên lạc được", "55 phút", "Chờ phân công", "warn")]
    for i, (a, p, k, t, w, s, sk) in enumerate(rows):
        y = 568 + i * 46
        c.line(88, y - 2, 1252, y - 2)
        c.text(108, y + 26, a, 13, K["text"], 600)
        c.badge(220, y + 11, p, k)
        c.text(300, y + 26, t, 13)
        c.text(780, y + 26, w, 13)
        c.badge(960, y + 11, s, sk)
    return c.save("wf-40-dashboard")


if __name__ == "__main__":
    for fn in (sos_form, sos_track, intake, command, review, dispatch, mission, dashboard):
        print("Đã tạo", fn() + ".svg")
