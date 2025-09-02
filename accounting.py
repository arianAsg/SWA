import sqlite3
import jdatetime
from typing import List, Dict, Optional

DB_FILE = "accounting.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    con = get_connection()
    cur = con.cursor()

    # جدول طرف حساب‌ها
    cur.execute('''
        CREATE TABLE IF NOT EXISTS parties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            mobile TEXT,
            national_id TEXT NOT NULL,
            address TEXT,
            type TEXT CHECK(type IN ('مشتری', 'همکار', 'سایر')),
            account_status TEXT CHECK(account_status IN ('طلبکار', 'بدهکار')),
            initial_balance INTEGER DEFAULT 0,
            notes TEXT
        )
    ''')

    # جدول سیم کارت‌ها
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sim_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT NOT NULL UNIQUE,
            operator TEXT CHECK(operator IN ('همراه اول', 'ایرانسل', 'رایتل')),
            status TEXT CHECK(status IN ('فعال', 'غیرفعال', 'مسدود')),
            purchase_date TEXT,
            purchase_price INTEGER,
            sale_date TEXT,
            sale_price INTEGER,
            current_owner_id INTEGER,
            notes TEXT,
            FOREIGN KEY (current_owner_id) REFERENCES parties(id)
        )
    ''')

    # جدول تراکنش‌ها
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tx_type TEXT,
            amount INTEGER,
            shamsi_datetime TEXT,
            description TEXT,
            contract_file TEXT,
            party_id INTEGER,
            sim_card_id INTEGER,
            payment_method TEXT,
            bank_account TEXT,
            reference_number TEXT,
            FOREIGN KEY (party_id) REFERENCES parties(id),
            FOREIGN KEY (sim_card_id) REFERENCES sim_cards(id)
        )
    ''')
    cur.execute("""
        CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            check_number TEXT NOT NULL,
            type TEXT CHECK(type IN ('دریافت', 'پرداخت')),
            bank_id INTEGER,
            amount INTEGER NOT NULL,
            due_date TEXT,
            status TEXT CHECK(status IN ('در جریان', 'وصول شد', 'برگشتی')),
            notes TEXT,
            FOREIGN KEY (bank_id) REFERENCES banks(id)
        )
    """)

    # جدول پرداخت‌های متعدد
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transaction_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER,
            payment_method TEXT,
            amount INTEGER,
            bank_account TEXT,
            reference_number TEXT,
            notes TEXT,
            FOREIGN KEY (transaction_id) REFERENCES transactions(id)
        )
    """)



    con.commit()
    con.close()

def migrate_db_v2():
    """ایجاد جدول بانک‌ها در صورت نبودن"""
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS banks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            account_number TEXT NOT NULL,
            owner TEXT,
            notes TEXT
        )
    """)

    con.commit()
    con.close()


def add_transaction(tx_type, amount, description="", contract_file="", party_id=None, sim_card_id=None, payment_method="", bank_account="", reference_number=""):
    con = get_connection()
    cur = con.cursor()
    shamsi_datetime = jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute('''
        INSERT INTO transactions 
        (tx_type, amount, shamsi_datetime, description, contract_file, party_id, sim_card_id, payment_method, bank_account, reference_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tx_type, amount, shamsi_datetime, description, contract_file, party_id, sim_card_id, payment_method, bank_account, reference_number))
    con.commit()
    con.close()

def get_all_transactions():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM transactions ORDER BY id DESC")
    rows = cur.fetchall()
    cols = [c[0] for c in cur.description]
    con.close()
    return [dict(zip(cols, r)) for r in rows]

def update_transaction(tx_id, tx_type, amount, description):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        UPDATE transactions SET tx_type=?, amount=?, description=? WHERE id=?
    """, (tx_type, amount, description, tx_id))
    con.commit()
    con.close()

def delete_transaction(tx_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM transactions WHERE id=?", (tx_id,))
    con.commit()
    con.close()
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        SELECT t.id, t.tx_type, t.amount, t.shamsi_datetime, t.description, 
               t.contract_file, p.name, s.number, t.payment_method,
               t.bank_account, t.reference_number
        FROM transactions t
        LEFT JOIN parties p ON t.party_id = p.id
        LEFT JOIN sim_cards s ON t.sim_card_id = s.id
        ORDER BY t.shamsi_datetime DESC
    ''')
    rows = cur.fetchall()
    con.close()
    return [
        {
            "id": row[0], "type": row[1], "amount": row[2], "date": row[3],
            "description": row[4], "contract_file": row[5], "party_name": row[6],
            "sim_number": row[7], "payment_method": row[8],
            "bank_account": row[9], "reference_number": row[10]
        }
        for row in rows
    ]

def finance_summary():
    txs = get_all_transactions()
    total_income = sum(t["amount"] for t in txs if t["type"].startswith("دریافت"))
    total_outcome = sum(t["amount"] for t in txs if t["type"].startswith("پرداخت"))
    balance = total_income - total_outcome
    return {
        "total_income": total_income,
        "total_outcome": total_outcome,
        "balance": balance
    }

def get_financial_reports(start_date=None, end_date=None):
    con = get_connection()
    cur = con.cursor()
    
    query = '''
        SELECT 
            strftime('%Y-%m', shamsi_datetime) as month,
            SUM(CASE WHEN tx_type LIKE 'دریافت%' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN tx_type LIKE 'پرداخت%' THEN amount ELSE 0 END) as expense,
            SUM(CASE WHEN tx_type LIKE 'دریافت%' THEN amount ELSE -amount END) as balance
        FROM transactions
    '''
    
    params = []
    if start_date and end_date:
        query += " WHERE shamsi_datetime BETWEEN ? AND ?"
        params = [start_date, end_date]

    query += " GROUP BY strftime('%Y-%m', shamsi_datetime) ORDER BY month"
    cur.execute(query, params)
    monthly_report = cur.fetchall()
    
    by_operator = []
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sim_cards'")
        if cur.fetchone():
            query = '''
                SELECT 
                    s.operator,
                    COUNT(*) as transaction_count,
                    SUM(t.amount) as total_amount
                FROM transactions t
                LEFT JOIN sim_cards s ON t.sim_card_id = s.id
                WHERE t.sim_card_id IS NOT NULL
            '''
            if start_date and end_date:
                query += " AND t.shamsi_datetime BETWEEN ? AND ?"
                cur.execute(query, [start_date, end_date])
            else:
                cur.execute(query)
            by_operator = cur.fetchall()
    except:
        pass
    
    con.close()
    
    return {
        'monthly': monthly_report,
        'by_operator': by_operator
    }

def add_party(name, phone="", mobile="", national_id="", address="", party_type="مشتری", account_status="طلبکار", initial_balance=0, notes=""):
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        INSERT INTO parties (name, phone, mobile, national_id, address, type, account_status, initial_balance, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, phone, mobile, national_id, address, party_type, account_status, initial_balance, notes))
    con.commit()
    con.close()

def get_parties():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM parties")
    rows = cur.fetchall()
    cols = [c[0] for c in cur.description]
    con.close()
    return [dict(zip(cols, r)) for r in rows]


def add_sim_card(
    number: str,
    operator: str,
    purchase_price: Optional[int] = None,
    purchase_date: Optional[str] = None,
    current_owner_id: Optional[int] = None,
    notes: str = ""
):
    shamsi_date = jdatetime.datetime.now().strftime("%Y-%m-%d") if not purchase_date else purchase_date
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        INSERT INTO sim_cards 
        (number, operator, status, purchase_date, purchase_price, current_owner_id, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (number, operator, 'فعال', shamsi_date, purchase_price, current_owner_id, notes))
    con.commit()
    con.close()

def get_sim_cards():
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        SELECT s.id, s.number, s.operator, s.status, s.purchase_price, 
               s.sale_price, p.name as owner_name
        FROM sim_cards s
        LEFT JOIN parties p ON s.current_owner_id = p.id
        ORDER BY s.number
    ''')
    rows = cur.fetchall()
    con.close()
    return [
        {
            "id": row[0], "number": row[1], "operator": row[2], 
            "status": row[3], "purchase_price": row[4],
            "sale_price": row[5], "owner_name": row[6]
        }
        for row in rows
    ]

def update_sim_owner(sim_id: int, new_owner_id: Optional[int], sale_price: Optional[int] = None):
    shamsi_date = jdatetime.datetime.now().strftime("%Y-%m-%d")
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        UPDATE sim_cards 
        SET current_owner_id = ?, sale_price = ?, sale_date = ?
        WHERE id = ?
    ''', (new_owner_id, sale_price, shamsi_date, sim_id))
    con.commit()
    con.close()

# ===== مدیریت بانک‌ها =====
def add_bank(name, account_number, owner="", notes=""):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO banks (name, account_number, owner, notes)
        VALUES (?, ?, ?, ?)
    """, (name, account_number, owner, notes))
    con.commit()
    con.close()

def get_banks():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM banks")
    rows = cur.fetchall()
    cols = [c[0] for c in cur.description]
    con.close()
    return [dict(zip(cols, r)) for r in rows]

def add_check(check_number, type, bank_id, amount, due_date, status="در جریان", notes=""):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO checks (check_number, type, bank_id, amount, due_date, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (check_number, type, bank_id, amount, due_date, status, notes))
    con.commit()
    con.close()

def get_checks():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM checks ORDER BY id DESC")
    rows = cur.fetchall()
    cols = [c[0] for c in cur.description]
    con.close()
    return [dict(zip(cols, r)) for r in rows]

def update_check(check_id, **kwargs):
    con = get_connection()
    cur = con.cursor()
    fields = ", ".join([f"{k}=?" for k in kwargs.keys()])
    cur.execute(f"UPDATE checks SET {fields} WHERE id=?", (*kwargs.values(), check_id))
    con.commit()
    con.close()

def delete_check(check_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM checks WHERE id=?", (check_id,))
    con.commit()
    con.close()

# ===== پرداخت‌های چندگانه =====
def add_payment_to_transaction(transaction_id, payment_method, amount, bank_account="", reference_number="", notes=""):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO transaction_payments
        (transaction_id, payment_method, amount, bank_account, reference_number, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (transaction_id, payment_method, amount, bank_account, reference_number, notes))
    con.commit()
    con.close()

def get_payments_by_transaction(transaction_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM transaction_payments WHERE transaction_id=?", (transaction_id,))
    rows = cur.fetchall()
    cols = [c[0] for c in cur.description]
    con.close()
    return [dict(zip(cols, r)) for r in rows]

def delete_payment(payment_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM transaction_payments WHERE id=?", (payment_id,))
    con.commit()
    con.close()

def migrate_db():
    con = get_connection()
    cur = con.cursor()

    # تغییر نوع ستون type
    try:
        cur.execute("""
            ALTER TABLE parties RENAME TO parties_old
        """)
        cur.execute('''
            CREATE TABLE parties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                mobile TEXT NOT NULL,
                national_id TEXT NOT NULL,
                address TEXT,
                type TEXT CHECK(type IN ('مشتری', 'همکار', 'سایر')),
                account_status TEXT CHECK(account_status IN ('طلبکار', 'بدهکار')),
                initial_balance INTEGER DEFAULT 0,
                notes TEXT
            )
        ''')
        cur.execute('''
            INSERT INTO parties (id, name, phone, mobile, national_id, address, type, notes)
            SELECT id, name, phone, '' as mobile, national_id, address,
                   CASE WHEN type='فروشنده' THEN 'همکار' ELSE type END as type,
                   notes
            FROM parties_old
        ''')
        cur.execute("DROP TABLE parties_old")
    except sqlite3.OperationalError:
        # اضافه کردن ستون‌ها به جدول قدیمی، اگر وجود نداشتند
        try: cur.execute("ALTER TABLE parties ADD COLUMN mobile TEXT")
        except: pass
        try: cur.execute("ALTER TABLE parties ADD COLUMN account_status TEXT")
        except: pass
        try: cur.execute("ALTER TABLE parties ADD COLUMN initial_balance INTEGER DEFAULT 0")
        except: pass

    con.commit()
    con.close()