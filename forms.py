import streamlit as st

def seller_form():
    col1, col2, col3 = st.columns(3)
    with col1:
        birth = st.text_input("متولد (فروشنده):", key="seller_birth")
        phone = st.text_input("تلفن (فروشنده):", key="seller_phone")
    with col2:
        issued = st.text_input("صادره از (فروشنده):", key="seller_issued")
        address = st.text_input("نشانی (فروشنده):", key="seller_address")
    with col3:
        national_id = st.text_input("شماره کد ملی (فروشنده):", key="seller_national_id")
        name = st.text_input("نام فروشنده:", key="seller_name")
    child = st.text_input("فرزند (فروشنده):", key="seller_child")
    return {
        "birth": birth, "phone": phone, "issued": issued, "address": address,
        "national_id": national_id, "name": name, "child": child
    }

def buyer_form():
    col1, col2, col3 = st.columns(3)
    with col1:
        birth = st.text_input("متولد (خریدار):", key="buyer_birth")
        phone = st.text_input("تلفن (خریدار):", key="buyer_phone")
    with col2:
        issued = st.text_input("صادره از (خریدار):", key="buyer_issued")
        address = st.text_input("نشانی (خریدار):", key="buyer_address")
    with col3:
        national_id = st.text_input("شماره کد ملی (خریدار):", key="buyer_national_id")
        name = st.text_input("نام خریدار:", key="buyer_name")
    child = st.text_input("فرزند (خریدار):", key="buyer_child")
    return {
        "birth": birth, "phone": phone, "issued": issued, "address": address,
        "national_id": national_id, "name": name, "child": child
    }

def sim_card_form():
    number = st.text_input("شماره سیم کارت:", key="sim_number")
    col1, col2 = st.columns(2)
    with col1:
        sale_amount = st.text_input("مبلغ مورد فروش (ریال):", key="sale_amount")
    with col2:
        sale_amount_toman = st.text_input("مبلغ مورد فروش (تومان):", key="sale_amount_toman")
    return {
        "number": number,
        "sale_amount": sale_amount,
        "sale_amount_toman": sale_amount_toman
    }

def payment_form():
    date = st.text_input("تاریخ و زمان تحویل سیم کارت:", key="payment_date")
    col1, col2 = st.columns(2)
    with col1:
        invoice_amount = st.text_input("مبلغ صورتحساب پرداخت شده (ریال):", key="invoice_amount")
    with col2:
        invoice_date = st.text_input("تاریخ صورتحساب و آبونمان:", key="invoice_date")
    return {
        "date": date,
        "invoice_amount": invoice_amount,
        "invoice_date": invoice_date
    }

def transfers_form():
    transfers = []
    st.write("لطفاً اطلاعات واریز را وارد کنید (حداکثر 3 ردیف):")
    for i in range(3):
        st.subheader(f"ردیف {i+1}")
        cols = st.columns(5)
        with cols[0]:
            description = st.text_input(f"شرح واریز", key=f"desc_{i}")
        with cols[1]:
            bank = st.text_input(f"بانک", key=f"bank_{i}")
        with cols[2]:
            amount = st.text_input(f"مبلغ واریزی (ریال)", key=f"amount_{i}")
        with cols[3]:
            method = st.text_input(f"نحوه پرداخت", key=f"method_{i}")
        with cols[4]:
            notes = st.text_input(f"توضیحات", key=f"notes_{i}")
        transfers.append((description, bank, amount, method, notes))
    return transfers

def notes_form():
    notes = st.text_area("توضیحات اضافی:", key="notes")
    return notes
