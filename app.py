import streamlit as st
from contract_generator import ContractGenerator
from forms import seller_form, buyer_form, sim_card_form, payment_form, transfers_form, notes_form

# تزریق css راست‌چین:
st.markdown("""
<style>
    * { direction: rtl; text-align: right; font-family: 'B Nazanin', Tahoma, sans-serif; }
    .stTextInput input, .stTextArea textarea { text-align: right; }
    .stSelectbox select { text-align: right; }
</style>
""", unsafe_allow_html=True)

st.title("📝 تولید متن قرارداد فروش سیم کارت")

# گرفتن داده‌های هر بخش به صورت مجزا
st.header("🔵 اطلاعات فروشنده")
seller = seller_form()
st.header("🔵 اطلاعات خریدار")
buyer = buyer_form()
st.header("📱 اطلاعات سیم کارت")
sim_card = sim_card_form()
st.header("💵 اطلاعات پرداخت")
payment = payment_form()
st.header("🏦 اطلاعات واریز")
transfers = transfers_form()
notes = notes_form()

# ساخت دیتا برای قرار دادن در ContractGenerator
contract_data = {
    'seller_birth': seller['birth'],
    'seller_issued': seller['issued'],
    'seller_national_id': seller['national_id'],
    'seller_child': seller['child'],
    'seller_name': seller['name'],
    'seller_phone': seller['phone'],
    'seller_address': seller['address'],
    'buyer_birth': buyer['birth'],
    'buyer_issued': buyer['issued'],
    'buyer_national_id': buyer['national_id'],
    'buyer_child': buyer['child'],
    'buyer_name': buyer['name'],
    'buyer_phone': buyer['phone'],
    'buyer_address': buyer['address'],
    'sim_number': sim_card['number'],
    'sale_amount': sim_card['sale_amount'],
    'sale_amount_toman': sim_card['sale_amount_toman'],
    'payment_date': payment['date'],
    'invoice_amount': payment['invoice_amount'],
    'invoice_date': payment['invoice_date'],
    'payment_methods': transfers,
    'notes': notes,
}

if st.button("🖨️ تولید فایل Word", type="primary"):
    generator = ContractGenerator()
    file_stream = generator.generate_contract(contract_data)
    st.download_button(
        label="⬇️ دانلود فایل Word",
        data=file_stream,
        file_name="قرارداد_فروش_سیم_کارت.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    st.success("✅ فایل Word با موفقیت تولید شد!")

