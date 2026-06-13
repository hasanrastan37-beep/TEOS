from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

class PDFReportGenerator:
    def __init__(self):
        # ثبت فونت فارسی (در صورت وجود)
        font_path = os.path.join(os.path.dirname(__file__), "../../fonts/Vazir.ttf")
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Vazir', font_path))
            self.font = 'Vazir'
        else:
            self.font = 'Helvetica'

    def generate_sales_report(self, data: dict) -> bytes:
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.setFont(self.font, 12)
        y = 280 * mm
        p.drawString(20 * mm, y, "گزارش فروش")
        y -= 10 * mm
        for key, value in data.items():
            p.drawString(20 * mm, y, f"{key}: {value}")
            y -= 6 * mm
        p.showPage()
        p.save()
        return buffer.getvalue()

pdf_generator = PDFReportGenerator()
