"""Vẽ Use Case Diagram tổng quát (chuẩn UML) của SOSLink dưới dạng SVG.

Chạy: python docs/usecase/build_usecase_diagram.py
Kết quả: docs/usecase/ucd-overview.svg
"""

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent
FONT = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"
C = {
    "bg": "#ffffff", "text": "#1f2937", "muted": "#6b7280",
    "boundary": "#1168bd", "boundary_bg": "#f5f9ff",
    "ell": "#e8f1fb", "ell_stroke": "#1168bd", "ai": "#f3ecfd", "ai_stroke": "#7a4fbf",
    "line": "#475569", "rel": "#7a4fbf",
}

# (mã, nhãn, có AI) — thứ tự từ trên xuống để đường nối hai bên ít chồng nhau
UCS = [
    ("SEND", "Gửi tin cầu cứu", False),
    ("TRACK", "Tra cứu tình trạng", False),
    ("PASTE", "Nhập tin từ mạng xã hội", False),
    ("AI", "AI trích xuất, gộp, ưu tiên", True),
    ("REVIEW", "Duyệt và xác minh ca", False),
    ("DISPATCH", "Phân công đội cứu hộ", False),
    ("MISSION", "Nhận nhiệm vụ, báo kết quả", False),
    ("ALERT", "Cảnh báo ca quá hạn", False),
    ("REPORT", "Báo cáo và đo chất lượng AI", False),
    ("ADMIN", "Quản trị hệ thống", False),
]


def stick(x, y, name):
    s = C["text"]
    return (f'<g stroke="{s}" stroke-width="2" fill="none">'
            f'<circle cx="{x}" cy="{y + 12}" r="12" fill="#fff"/>'
            f'<line x1="{x}" y1="{y + 24}" x2="{x}" y2="{y + 60}"/>'
            f'<line x1="{x - 22}" y1="{y + 36}" x2="{x + 22}" y2="{y + 36}"/>'
            f'<line x1="{x}" y1="{y + 60}" x2="{x - 18}" y2="{y + 88}"/>'
            f'<line x1="{x}" y1="{y + 60}" x2="{x + 18}" y2="{y + 88}"/></g>'
            f'<text x="{x}" y="{y + 110}" text-anchor="middle" font-weight="600" '
            f'font-size="15" fill="{s}">{escape(name)}</text>')


def box_actor(x, cy, name, stereo):
    w, h = 130, 64
    return (f'<rect x="{x - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="6" fill="#fff" '
            f'stroke="{C["text"]}" stroke-width="2"/>'
            f'<text x="{x}" y="{cy - 8}" text-anchor="middle" font-size="12" fill="{C["muted"]}">'
            f'&#171;{stereo}&#187;</text>'
            f'<text x="{x}" y="{cy + 14}" text-anchor="middle" font-size="15" font-weight="600" '
            f'fill="{C["text"]}">{escape(name)}</text>')


def build():
    ow, oh, row = 320, 46, 66
    margin, title_h, pad = 30, 56, 50
    left_zone, right_zone = 220, 230
    bx = margin + left_zone
    bw = ow + 2 * pad
    bt = title_h + margin
    top = bt + 50
    W = bx + bw + right_zone + margin
    bottom = top + len(UCS) * row
    H = bottom + margin + 30
    pos = {k: top + i * row + oh / 2 for i, (k, _, _) in enumerate(UCS)}
    cx = bx + pad + ow / 2
    le, re = bx + pad, bx + pad + ow

    def ry(r):
        return top + r * row + oh / 2

    lax, rax = margin + 90, bx + bw + right_zone / 2
    # (tên, x, y của tay, cạnh, use case)
    people = [
        ("Người dân", lax, ry(0.6), "L", ["SEND", "TRACK"]),
        ("Tình nguyện viên", lax, ry(3.2), "L", ["PASTE"]),
        ("Điều phối viên", lax, ry(6.2), "L", ["REVIEW", "DISPATCH", "REPORT"]),
        ("Đội cứu hộ", rax, ry(6.0), "R", ["MISSION"]),
        ("Quản trị viên", rax, ry(8.8), "R", ["REPORT", "ADMIN"]),
    ]
    systems = [
        ("Claude API", "external", ry(2.0), ["AI"]),
        ("Scheduler", "system", ry(4.3), ["ALERT"]),
    ]

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>',
         f'<text x="{W / 2}" y="{margin + 18}" text-anchor="middle" font-size="20" font-weight="700" '
         f'fill="{C["text"]}">Use Case tổng quát — SOSLink</text>',
         f'<rect x="{bx}" y="{bt}" width="{bw}" height="{bottom - bt + 10}" rx="10" fill="{C["boundary_bg"]}" '
         f'stroke="{C["boundary"]}" stroke-width="2"/>',
         f'<text x="{bx + 16}" y="{bt + 26}" font-size="15" font-weight="700" fill="{C["boundary"]}">'
         f'SOSLink — System Boundary</text>']

    def line(x1, y1, x2, y2):
        o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C["line"]}" stroke-width="1.2"/>')

    for _, x, y, side, keys in people:
        for k in keys:
            if side == "L":
                line(x + 22, y, le, pos[k])
            else:
                line(x - 22, y, re, pos[k])
    for _, _, cy, keys in systems:
        for k in keys:
            line(rax - 65, cy, re, pos[k])

    for k, label, ai in UCS:
        fill, stroke = (C["ai"], C["ai_stroke"]) if ai else (C["ell"], C["ell_stroke"])
        o.append(f'<ellipse cx="{cx}" cy="{pos[k]}" rx="{ow / 2}" ry="{oh / 2}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="1.5"/>'
                 f'<text x="{cx}" y="{pos[k] + 5}" text-anchor="middle" font-size="14" '
                 f'fill="{C["text"]}">{escape(label)}</text>')

    for name, x, y, _, _ in people:
        o.append(stick(x, y - 36, name))
    for name, stereo, cy, _ in systems:
        o.append(box_actor(rax, cy, name, stereo))

    o.append(f'<g font-size="11" fill="{C["muted"]}">'
             f'<ellipse cx="{bx + 14}" cy="{H - 18}" rx="14" ry="7" fill="{C["ai"]}" stroke="{C["ai_stroke"]}"/>'
             f'<text x="{bx + 34}" y="{H - 14}">AI chỉ đề xuất; con người duyệt và phân công</text></g>')
    o.append("</svg>")
    (OUT / "ucd-overview.svg").write_text("\n".join(o), encoding="utf-8")


if __name__ == "__main__":
    build()
    print("Đã tạo ucd-overview.svg")
