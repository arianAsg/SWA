import streamlit as st
from contract_generator import ContractGenerator
import io
import os
import datetime
import json
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ---------- Contract types --------------
CONTRACT_TYPES = {
    "قرارداد فروش": "فروش",
    "قرارداد خرید/صلح (با مفاد ویژه)": "خرید"
}

CONTRACTS_FOLDER = "contracts"
ARCHIVE_FILE = os.path.join(CONTRACTS_FOLDER, "archive.json")
LOGO_FOLDER = "logo"
LOGO_PATH = os.path.join(LOGO_FOLDER, "uploaded_logo.png")
os.makedirs(CONTRACTS_FOLDER, exist_ok=True)
os.makedirs(LOGO_FOLDER, exist_ok=True)

st.markdown("""
<style>
    * {
        direction: rtl;
        text-align: right;
        font-family: 'B Nazanin', Tahoma, sans-serif;
    }
    .stTextInput input, .stTextArea textarea {
        text-align: right;
    }
    .stSelectbox select {
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Logo Upload & Archive ---
st.sidebar.header("تنظیمات/امکانات")
uploaded_logo = st.sidebar.file_uploader("بارگذاری لوگو/سربرگ (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
if uploaded_logo:
    with open(LOGO_PATH, "wb") as f:
        f.write(uploaded_logo.getbuffer())
    st.sidebar.success("لوگو با موفقیت ذخیره شد.")

show_archive = st.sidebar.checkbox("🗂️ مشاهده آرشیو قراردادها")
if show_archive:
    st.sidebar.subheader("آرشیو قراردادها")
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, "r", encoding='utf-8') as fa:
            archive = json.load(fa)
        for item in reversed(archive):
            st.sidebar.write(f"{item['type']} | {item['datetime']}")
            file_path = os.path.join(CONTRACTS_FOLDER, item["filename"])
            if os.path.exists(file_path):
                with open(file_path, "rb") as fx:
                    st.sidebar.download_button(
                        label=f"دانلود [{item['filename']}]",
                        data=fx,
                        file_name=item["filename"],
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=item["filename"])
    else:
        st.sidebar.info("هنوز قراردادی ثبت نشده.")

contract_type = st.sidebar.radio("نوع قرارداد را انتخاب کنید", list(CONTRACT_TYPES.keys()))

def show_common_form():
    st.header("اطلاعات فروشنده")
    seller_name = st.text_input("نام فروشنده")
    seller_phone = st.text_input("تلفن فروشنده")
    seller_address = st.text_input("نشانی فروشنده")
    seller_birth = st.text_input("متولد فروشنده")
    seller_issued = st.text_input("صادره از فروشنده")
    seller_national_id = st.text_input("شماره کد ملی فروشنده")
    seller_child = st.text_input("فرزند فروشنده")

    st.header("اطلاعات خریدار")
    buyer_name = st.text_input("نام خریدار (متصالح)")
    buyer_phone = st.text_input("تلفن خریدار")
    buyer_address = st.text_input("نشانی خریدار")
    buyer_birth = st.text_input("متولد خریدار")
    buyer_issued = st.text_input("صادره از خریدار")
    buyer_national_id = st.text_input("شماره کد ملی خریدار")
    buyer_child = st.text_input("فرزند خریدار")

    st.header("مشخصات سیم کارت")
    sim_number = st.text_input("شماره سیم کارت")

    st.header("اطلاعات مالی")
    sale_amount = st.text_input("مبلغ مورد معامله (ریال)")
    sale_amount_toman = st.text_input("مبلغ مورد معامله (تومان)")
    payment_date = st.text_input("تاریخ و زمان تحویل سیم کارت")
    invoice_amount = st.text_input("مبلغ صورتحساب پرداخت شده (ریال)")
    invoice_date = st.text_input("تاریخ صورتحساب")

    st.header("اطلاعات واریز (حداکثر ۳ ردیف)")
    payment_methods = []
    for i in range(3):
        cols = st.columns(5)
        with cols[0]: description = st.text_input(f"شرح واریز", key=f"desc_{i}")
        with cols[1]: bank = st.text_input(f"بانک", key=f"bank_{i}")
        with cols[2]: amount = st.text_input(f"مبلغ واریزی", key=f"amount_{i}")
        with cols[3]: method = st.text_input(f"نحوه پرداخت", key=f"method_{i}")
        with cols[4]: notes = st.text_input(f"توضیحات", key=f"paynotes_{i}")
        payment_methods.append((description, bank, amount, method, notes))

    notes = st.text_area("توضیحات اضافی:")

    data = dict(
        seller_name=seller_name, seller_phone=seller_phone, seller_address=seller_address,
        seller_birth=seller_birth, seller_issued=seller_issued, seller_national_id=seller_national_id, seller_child=seller_child,
        buyer_name=buyer_name, buyer_phone=buyer_phone, buyer_address=buyer_address,
        buyer_birth=buyer_birth, buyer_issued=buyer_issued, buyer_national_id=buyer_national_id, buyer_child=buyer_child,
        sim_number=sim_number, sale_amount=sale_amount, sale_amount_toman=sale_amount_toman,
        payment_date=payment_date, invoice_amount=invoice_amount, invoice_date=invoice_date,
        payment_methods=payment_methods, notes=notes
    )
    return data

def generate_buy_contract(contract_data):
    doc = Document()
    # درج لوگو اگر موجود بود:
    logo_path = LOGO_PATH
    if os.path.exists(logo_path):
        doc.add_picture(logo_path, width=Pt(100))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    def rtl(text, bold=False):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.bold = bold
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.space_after = Pt(0)

    rtl("بسمه تعالی", bold=True)
    doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.RIGHT

    rtl(f"فروشنده: {contract_data['seller_name']}")
    rtl(f"تلفن: {contract_data['seller_phone']}")
    rtl(f"نشانی: {contract_data['seller_address']}")
    rtl(f"متولد: {contract_data['seller_birth']}   صادره از: {contract_data['seller_issued']}   شماره کد ملی: {contract_data['seller_national_id']}   فرزند: {contract_data['seller_child']}")

    rtl(f"متصالح (خریدار): {contract_data['buyer_name']}")
    rtl(f"تلفن: {contract_data['buyer_phone']}")
    rtl(f"نشانی: {contract_data['buyer_address']}")
    rtl(f"متولد: {contract_data['buyer_birth']}   صادره از: {contract_data['buyer_issued']}   شماره کد ملی: {contract_data['buyer_national_id']}   فرزند: {contract_data['buyer_child']}")

    rtl(f"مورد فروش: کلیه حقوق عینه، متصوره و فرضیه متعلق به یک رشته سیم کارت شرکت همراه اول به شماره {contract_data['sim_number']}\n"
        "اعم از حق الامتیاز و حق الاشتراک و وام و ودیعه متعلقه احتمالی به نحوی که دیگر هیچگونه حق و ادعایی برای فروشنده در مورد صلح باقی نماند و خریدار قائم مقام قانونی و رسمی فروشنده در شرکت همراه اول می باشد تا مطابق مقررات بنام و نفع خود استفاده نماید.")

    rtl(f"مبلغ مورد فروش: مبلغ {contract_data['sale_amount']} ریال معادل {contract_data['sale_amount_toman']} تومان که تمامی آن به اقرار تسلیم فروشنده گردیده است.")

    table = doc.add_table(rows=1, cols=5)
    hdrs = ["توضیحات", "مبلغ واریزی (ریال)", "بانک", "شرح واریز", "نحوه پرداخت"]
    for i, h in enumerate(hdrs):
        cell = table.rows[0].cells[i]
        cell.text = h
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.name = "B Nazanin"
    for payment in contract_data['payment_methods']:
        if any(payment):
            row = table.add_row().cells
            for i, item in enumerate(payment):
                row[i].text = str(item)
                row[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
                row[i].paragraphs[0].runs[0].font.name = "B Nazanin"
    rtl(f"تاریخ و زمان تحویل سیم کارت به متصالح: {contract_data['payment_date']}")

    solh_text = (
"""مفاد و شرایط:
1- مورد صلح صحیح و سالم به رویت متصالح رسیده و متصالح اقرار به دریافت و تصرف صحیح و سالم آن نموده است.
2- هزینه کلیه مکالمات داخل و خارج کشور تا زمان تنظیم صلحنامه به عهده متصالح خواهد بود.
3- متصالح متعهد به همکاری و حضور در تمام مراجع قانونی و قضایی در صورت لزوم می‌باشد.
4- مسئولیت کامل هرگونه سوءاستفاده یا مزاحمت و پرداخت حقوق و دیون مربوطه از زمان تنظیم صلحنامه به عهده متصالح است.
5- متصالح ضامن کشف فساد احتمالی گردید و تعهد به جبران خسارت دارد.
6- سیم کارت تلفن همراه به صورت مال الاجاره می‌باشد و هزینه‌های ما به التفاوت به عهده متصالح است.
7- متصالح هیچگونه حقی نسبت به قطع و سلب امتیاز نخواهد داشت.
8- در صورت کشف فساد مبلغ سیم کارت به خریدار عودت خواهد شد.
9- این سیم کارت به صورت اسقاط کافه خیارات حتی خیار غبن تنظیم و بر اساس مواد 10، 190 و 362 قانون مدنی معتبر است.
""")
    rtl(solh_text)
    rtl(f"توضیحات: {contract_data['notes']}")
    rtl("شاهد                                     شاهد         خریدار         فروشنده")

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

def save_contract_file(word_file, contract_type):
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"contract_{contract_type}_{now}.docx"
    file_path = os.path.join(CONTRACTS_FOLDER, filename)
    with open(file_path, "wb") as f:
        f.write(word_file.getbuffer())
    # ثبت در آرشیو
    try:
        with open(ARCHIVE_FILE, "r", encoding='utf-8') as fa:
            archive = json.load(fa)
    except:
        archive = []
    archive.append({
        "type": contract_type,
        "filename": filename,
        "datetime": now
    })
    with open(ARCHIVE_FILE, "w", encoding='utf-8') as fa:
        json.dump(archive, fa, ensure_ascii=False, indent=2)
    return file_path

# ----------- APP FLOW -----------------
contract_data = show_common_form()
if st.button("📝 تولید و ذخیره قرارداد"):
    if CONTRACT_TYPES[contract_type] == "فروش":
        generator = ContractGenerator()
        word_file = generator.generate_contract(contract_data)
    else:
        word_file = generate_buy_contract(contract_data)
    file_path = save_contract_file(word_file, CONTRACT_TYPES[contract_type])
    filename = os.path.basename(file_path)
    st.success(f"فایل قرارداد با نام {filename} ثبت و ذخیره شد.")
    st.download_button("⬇️ دانلود فایل Word همین قرارداد", data=word_file, file_name=filename)
