import streamlit as st
from contract_generator import ContractGenerator

# تزریق CSS برای راست‌چین کردن تمام عناصر
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

def get_user_input():
    """دریافت اطلاعات از کاربر از طریق رابط Streamlit"""
    st.title("📝 تولید متن قرارداد فروش سیم کارت")
    
    contract_data = {
        'seller': {},
        'buyer': {},
        'sim_card': {},
        'payment': {},
        'transfers': [],
        'notes': ''
    }
    
    # اطلاعات فروشنده
    st.header("🔵 اطلاعات فروشنده")
    col1, col2, col3 = st.columns(3)
    with col1:
        contract_data['seller']['birth'] = st.text_input("متولد (فروشنده):", key="seller_birth")
        contract_data['seller']['phone'] = st.text_input("تلفن (فروشنده):", key="seller_phone")
    with col2:
        contract_data['seller']['issued'] = st.text_input("صادره از (فروشنده):", key="seller_issued")
        contract_data['seller']['address'] = st.text_input("نشانی (فروشنده):", key="seller_address")
    with col3:
        contract_data['seller']['national_id'] = st.text_input("شماره کد ملی (فروشنده):", key="seller_national_id")
        contract_data['seller']['name'] = st.text_input("نام فروشنده:", key="seller_name")
    contract_data['seller']['child'] = st.text_input("فرزند (فروشنده):", key="seller_child")
    
    # اطلاعات خریدار
    st.header("🔵 اطلاعات خریدار")
    col1, col2, col3 = st.columns(3)
    with col1:
        contract_data['buyer']['birth'] = st.text_input("متولد (خریدار):", key="buyer_birth")
        contract_data['buyer']['phone'] = st.text_input("تلفن (خریدار):", key="buyer_phone")
    with col2:
        contract_data['buyer']['issued'] = st.text_input("صادره از (خریدار):", key="buyer_issued")
        contract_data['buyer']['address'] = st.text_input("نشانی (خریدار):", key="buyer_address")
    with col3:
        contract_data['buyer']['national_id'] = st.text_input("شماره کد ملی (خریدار):", key="buyer_national_id")
        contract_data['buyer']['name'] = st.text_input("نام خریدار:", key="buyer_name")
    contract_data['buyer']['child'] = st.text_input("فرزند (خریدار):", key="buyer_child")
    
    # اطلاعات سیم کارت
    st.header("📱 اطلاعات سیم کارت")
    contract_data['sim_card']['number'] = st.text_input("شماره سیم کارت:", key="sim_number")
    col1, col2 = st.columns(2)
    with col1:
        contract_data['payment']['sale_amount'] = st.text_input("مبلغ مورد فروش (ریال):", key="sale_amount")
    with col2:
        contract_data['payment']['sale_amount_toman'] = st.text_input("مبلغ مورد فروش (تومان):", key="sale_amount_toman")
    
    # اطلاعات پرداخت
    st.header("💵 اطلاعات پرداخت")
    contract_data['payment']['date'] = st.text_input("تاریخ و زمان تحویل سیم کارت:", key="payment_date")
    col1, col2 = st.columns(2)
    with col1:
        contract_data['payment']['invoice_amount'] = st.text_input("مبلغ صورتحساب پرداخت شده (ریال):", key="invoice_amount")
    with col2:
        contract_data['payment']['invoice_date'] = st.text_input("تاریخ صورتحساب و آبونمان:", key="invoice_date")
    
    # اطلاعات واریز
    st.header("🏦 اطلاعات واریز")
    st.write("لطفاً اطلاعات واریز را وارد کنید (حداکثر 3 ردیف):")
    for i in range(3):
        st.subheader(f"ردیف {i+1}")
        cols = st.columns(5)
        transfer = {}
        with cols[0]:
            transfer['description'] = st.text_input(f"شرح واریز", key=f"desc_{i}")
        with cols[1]:
            transfer['bank'] = st.text_input(f"بانک", key=f"bank_{i}")
        with cols[2]:
            transfer['amount'] = st.text_input(f"مبلغ واریزی (ریال)", key=f"amount_{i}")
        with cols[3]:
            transfer['method'] = st.text_input(f"نحوه پرداخت", key=f"method_{i}")
        with cols[4]:
            transfer['notes'] = st.text_input(f"توضیحات", key=f"notes_{i}")
        contract_data['transfers'].append(transfer)
    
    contract_data['notes'] = st.text_area("توضیحات اضافی:", key="notes")
    
    return contract_data

def prepare_contract_data(raw_data):
    """تبدیل ساختار داده‌های ورودی به فرمت مناسب برای کلاس ContractGenerator"""
    return {
        'seller_birth': raw_data['seller']['birth'],
        'seller_issued': raw_data['seller']['issued'],
        'seller_national_id': raw_data['seller']['national_id'],
        'seller_child': raw_data['seller']['child'],
        'seller_name': raw_data['seller']['name'],
        'seller_phone': raw_data['seller']['phone'],
        'seller_address': raw_data['seller']['address'],
        'buyer_birth': raw_data['buyer']['birth'],
        'buyer_issued': raw_data['buyer']['issued'],
        'buyer_national_id': raw_data['buyer']['national_id'],
        'buyer_child': raw_data['buyer']['child'],
        'buyer_name': raw_data['buyer']['name'],
        'buyer_phone': raw_data['buyer']['phone'],
        'buyer_address': raw_data['buyer']['address'],
        'sim_number': raw_data['sim_card']['number'],
        'sale_amount': raw_data['payment']['sale_amount'],
        'sale_amount_toman': raw_data['payment']['sale_amount_toman'],
        'payment_date': raw_data['payment']['date'],
        'invoice_amount': raw_data['payment']['invoice_amount'],
        'invoice_date': raw_data['payment']['invoice_date'],
        'payment_methods': [
            (
                t['description'], 
                t['bank'], 
                t['amount'], 
                t['method'], 
                t['notes']
            ) for t in raw_data['transfers']
        ],
        'notes': raw_data['notes']
    }

def main():
    # دریافت اطلاعات از کاربر
    raw_data = get_user_input()
    
    if st.button("🖨️ تولید فایل Word", type="primary"):
        # آماده‌سازی داده‌ها
        contract_data = prepare_contract_data(raw_data)
        
        # تولید قرارداد
        generator = ContractGenerator()
        file_stream = generator.generate_contract(contract_data)
        
        # ایجاد دکمه دانلود
        st.download_button(
            label="⬇️ دانلود فایل Word",
            data=file_stream,
            file_name="قرارداد_فروش_سیم_کارت.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        st.success("✅ فایل Word با موفقیت تولید شد!")

if __name__ == "__main__":
    main()