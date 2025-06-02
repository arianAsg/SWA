from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
import io

class ContractGenerator:
    def __init__(self):
        self.doc = Document()
        self._setup_document_style()

    def _setup_document_style(self):
        """تنظیم استایل پیش‌فرض سند"""
        style = self.doc.styles['Normal']
        font = style.font
        font.name = 'B Nazanin'
        font.size = Pt(12)
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    def _add_rtl_paragraph(self, text, bold=False):
        """اضافه کردن پاراگراف راست‌چین"""
        paragraph = self.doc.add_paragraph()
        run = paragraph.add_run(text)
        run.bold = bold
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        paragraph.paragraph_format.space_after = Pt(0)
        return paragraph

    def generate_contract(self, contract_data):
        """
        تولید سند قرارداد بر اساس داده‌های ورودی
        
        Args:
            contract_data (dict): دیکشنری حاوی تمام اطلاعات قرارداد
        Returns:
            io.BytesIO: فایل Word در قالب BytesIO
        """
        # اطلاعات پایه
        self._add_rtl_paragraph("بسمه تعالی", bold=True)
        self.doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.RIGHT
        self.doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # اطلاعات فروشنده
        seller_info = (
            f"متولد:\t{contract_data['seller_birth']}\t\tصادره از:\t{contract_data['seller_issued']}\t\t"
            f"شماره کد ملی:\t{contract_data['seller_national_id']}\t\tفرزند:\t{contract_data['seller_child']}\t\t"
            f"فروشنده:\t{contract_data['seller_name']}"
        )
        self._add_rtl_paragraph(seller_info)

        seller_contact = f"تلفن:\t{contract_data['seller_phone']}\t\tنشانی:\t{contract_data['seller_address']}"
        self._add_rtl_paragraph(seller_contact)

        # اطلاعات خریدار
        buyer_info = (
            f"متولد:\t{contract_data['buyer_birth']}\t\tصادره از:\t{contract_data['buyer_issued']}\t\t"
            f"شماره کد ملی:\t{contract_data['buyer_national_id']}\t\tفرزند:\t{contract_data['buyer_child']}\t\t"
            f"خریدار:\t{contract_data['buyer_name']}"
        )
        self._add_rtl_paragraph(buyer_info)

        buyer_contact = f"تلفن:\t{contract_data['buyer_phone']}\t\tنشانی:\t{contract_data['buyer_address']}"
        self._add_rtl_paragraph(buyer_contact)

        # متن اصلی قرارداد
        contract_text = (
            f"\nو شماره {contract_data['sim_number']} مورد فروش: کلیه حقوق عینه، متصوره و فرضیه متعلق به یک رشته سیم کارت شرکت همراه اول به شماره\n"
            f"اعم از حق الامتیاز و حق الاشتراک و وام و ودیعه متعلقه احتمالی به نحویکه دیگر هیچگونه حق و ادعایی برای فروشنده در مورد سیم کارت\n"
            f"فروش باقی نماند و خریدار قائم مقام قانونی و رسمی فروشنده در شرکت همراه اول می باشد تا مطابق مقررات بنام و نفع خود استفاده نماید.\n"
            f"تومان که تماماً به اقراره تسلیم فروشنده گردیده است. {contract_data['sale_amount_toman']} ریال معادل {contract_data['sale_amount']} مبلغ مورد فروش: مبلغ\n"
        )
        self._add_rtl_paragraph(contract_text)

        # جدول واریزها
        self._add_payment_table(contract_data['payment_methods'])

        # ادامه متن قرارداد
        remaining_text = (
            f"\nبا توجه به ماده 390 قانون مدنی در خصوص ضمان درک از آنجایی که فروشنده مبیع مورد معامله را به استناد اسناد صدوری از مخابرات و در ید بودن سیم کارت در زمان انتقال به خود هیچ اطلاعی از معاملات قبلی قبل از مالک شدن خودش ندارد و به دلیل جلوگیری از ضمان قانونی فروشنده مبنی بر مستحق الغیر بودن مبی در یده‌ای قبل فروشنده ضمن انتقال رسمی خط مورد معامله درج عدم ضمان نسبت به خریدار را در قرارداد مزبور و درج و خریدار نیز درکمال آگاهی و صحت عقل این عدم ضمان را می‌پذیرد.\n\n"
            f"می باشد. مورخ: تاریخ و زمان تحویل سیم کارت به مصالح ساعت: {contract_data['payment_date']}\n"
            f"ریال توسط فروشنده پرداخت شده است. {contract_data['invoice_amount']} به مبلغ: صورتحساب و آبونمان خط مذکور تا تاریخ: {contract_data['invoice_date']}\n"
            f"صحیح و سالم به رویت خریدار رسیده و خریدار اقرار به دریافت و تصرف صحیح و سالم آن نموده است. مورد فروش در تاریخ {contract_data['payment_date']}\n"
            f"می باشد. این سیم کارت به صورت\n\n"
            f"توضیحات: {contract_data['notes']}\n\n"
            f"شاهد                                     شاهد         خریدار         فروشنده"
        )
        self._add_rtl_paragraph(remaining_text)

        # ذخیره فایل در حافظه
        file_stream = io.BytesIO()
        self.doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

    def _add_payment_table(self, payment_methods):
        """اضافه کردن جدول واریزها به سند"""
        table = self.doc.add_table(rows=1, cols=5)
        table.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # هدرهای جدول
        hdr_cells = table.rows[0].cells
        headers = ['توضیحات', 'مبلغ واریزی (ریال)', 'بانک', 'شرح واریز', 'نحوه پرداخت']
        
        for i, header in enumerate(headers):
            hdr_cells[i].text = header
            hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
            hdr_cells[i].paragraphs[0].runs[0].font.name = 'B Nazanin'
            hdr_cells[i].paragraphs[0].runs[0].bold = True
        
        # اضافه کردن داده‌های واریز
        for payment in payment_methods:
            if any(payment):
                row_cells = table.add_row().cells
                for i, item in enumerate(payment):
                    row_cells[i].text = str(item)
                    row_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    row_cells[i].paragraphs[0].runs[0].font.name = 'B Nazanin'