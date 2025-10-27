from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_pdf_report(title: str, sections: dict, path="report.pdf"):
    """生成簡易 PDF 報告"""
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 80, title)
    c.setFont("Helvetica", 12)
    y = height - 120
    for section, content in sections.items():
        c.drawString(80, y, f"【{section}】")
        y -= 20
        for line in content.split("\n"):
            c.drawString(100, y, line)
            y -= 16
        y -= 12
    c.drawString(100, 40, f"生成時間：{datetime.now():%Y-%m-%d %H:%M}")
    c.save()
    return path
