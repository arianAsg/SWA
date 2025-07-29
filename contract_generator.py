from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
import io
import os

class ContractGenerator:
    def __init__(self):
        self.doc = Document()
        self._setup_document_style()
        self._add_logo_if_exists()

    def _setup_document_style(self):
        style = self.doc.styles['Normal']
        font = style.font
        font.name = 'B Nazanin'
        font.size = Pt(12)
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    def _add_logo_if_exists(self):
        logo_path = "logo/uploaded_logo.png"
        if os.path.exists(logo_path):
            self.doc.add_picture(logo_path, width=Inches(2))
            last_paragraph = self.doc.paragraphs[-1]
            last_paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    def _add_rtl_paragraph(self, text, bold=False):
        paragraph = self.doc.add_paragraph()
        run = paragraph.add_run(text)
        run.bold = bold
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        paragraph.paragraph_format.space_after = Pt(0)
        return paragraph

    def generate_contract(self, contract_data):
        self._add_rtl_paragraph("بسمه تعالی", bold=True)
        self.doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.RIGHT
        self.doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.RIGHT

        seller_info = (
            f"متولد: {contract_data['seller_birth']}   صادره از: {contract_data['seller_issued']}   "
            f"شماره کد ملی: {contract_data['seller_national_id']}   فرزند: {contract_data['seller_child']}   "
            f"فروشنده: {contract_data['seller_name']}"
        )
        self._add_rtl_paragraph(seller_info)
        seller_contact = f"تلفن: {contract_data['seller_phone']}   نشانی: {contract_data['seller_address']}"
        self._add_rtl_paragraph(seller_contact)

        buyer_info = (
            f"متولد: {contract_data['buyer_birth']}   صادره از: {contract_data['buyer_issued']}   "
            f"شماره کد ملی: {contract_data['buyer_national_id']}   فرزند: {contract_data['buyer_child']}   "
            f"خریدار: {contract_data['buyer_name']}"
        )
        self._add_rtl_paragraph(buyer_info)
        buyer_contact = f"تلفن: {contract_data['buyer_phone']}   نشانی: {contract_data['buyer_address']}"
        self._add_rtl_paragraph(buyer_contact)

        contract_text = (
            f"\nو شماره {contract_data['sim_number']} مورد فروش: کلیه حقوق عینه، متصوره و فرضیه متعلق به یک رشته سیم کارت شرکت همراه اول به شماره\n"
            f"اعم از حق الامتیاز و حق الاشتراک و وام و ودیعه متعلقه احتمالی به نحوی که دیگر هیچگونه حق و ادعایی برای فروشنده در مورد سیم کارت\n"
            f"فروش باقی نماند و خریدار قائم مقام قانونی و رسمی فروشنده در شرکت همراه اول می باشد تا مطابق مقررات بنام و نفع خود استفاده نماید.\n"
            f"تومان که تماماً به اقراره تسلیم فروشنده گردیده است. {contract_data['sale_amount_toman']} ریال معادل {contract_data['sale_amount']} مبلغ مورد فروش: مبلغ\n"
        )
        self._add_rtl_paragraph(contract_text)

        self._add_payment_table(contract_data['payment_methods'])

        remaining_text = (
            f"\nبا توجه به ماده 390 قانون مدنی در خصوص ضمان درک ...\n"
            f"تاریخ و زمان تحویل سیم کارت به مصالح: {contract_data['payment_date']}\n"
            f"مبلغ صورتحساب و آبونمان خط مذکور تا تاریخ {contract_data['invoice_date']}: {contract_data['invoice_amount']} ریال\n"
            f"توضیحات: {contract_data['notes']}\n"
            f"\nشاهد                                     شاهد         خریدار         فروشنده"
        )
        self._add_rtl_paragraph(remaining_text)

        file_stream = io.BytesIO()
        self.doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

    def _add_payment_table(self, payment_methods):
        table = self.doc.add_table(rows=1, cols=5)
        table.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hdr_cells = table.rows[0].cells
        headers = ['توضیحات', 'مبلغ واریزی (ریال)', 'بانک', 'شرح واریز', 'نحوه پرداخت']
        for i, header in enumerate(headers):
            hdr_cells[i].text = header
            hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
            hdr_cells[i].paragraphs[0].runs[0].font.name = 'B Nazanin'
            hdr_cells[i].paragraphs[0].runs[0].bold = True
        for payment in payment_methods:
            if any(payment):
                row_cells = table.add_row().cells
                for i, item in enumerate(payment):
                    row_cells[i].text = str(item)
                    row_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    row_cells[i].paragraphs[0].runs[0].font.name = 'B Nazanin'
