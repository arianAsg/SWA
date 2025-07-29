import sqlite3
import jdatetime
from typing import List, Dict, Optional

DB_FILE = "accounting.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    con = get_connection()
    cur = con.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS parties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            national_id TEXT,
            address TEXT,
            type TEXT CHECK(type IN ('مشتری', 'فروشنده', 'سایر')),
            notes TEXT
        )
    ''')
    
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
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bank_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bank_name TEXT NOT NULL,
            account_number TEXT NOT NULL,
            account_holder TEXT,
            current_balance INTEGER DEFAULT 0,
            notes TEXT
        )
    ''')

    con.commit()
    con.close()

def add_transaction(
    tx_type: str,
    amount: int,
    description: str = "",
    contract_file: str = "",
    party_id: Optional[int] = None,
    sim_card_id: Optional[int] = None,
    payment_method: str = "",
    bank_account: str = "",
    reference_number: str = ""
):
    shamsi_now = jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        INSERT INTO transactions
        (tx_type, amount, shamsi_datetime, description, contract_file, 
         party_id, sim_card_id, payment_method, bank_account, reference_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tx_type, amount, shamsi_now, description, contract_file, 
          party_id, sim_card_id, payment_method, bank_account, reference_number))
    con.commit()
    con.close()

def get_all_transactions() -> List[Dict]:
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

def add_party(name: str, phone: str = "", national_id: str = "", 
              address: str = "", party_type: str = "مشتری", notes: str = ""):
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        INSERT INTO parties 
        (name, phone, national_id, address, type, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, phone, national_id, address, party_type, notes))
    con.commit()
    con.close()

def get_parties():
    con = get_connection()
    cur = con.cursor()
    cur.execute('SELECT id, name, phone, national_id, type FROM parties ORDER BY name')
    rows = cur.fetchall()
    con.close()
    return [{"id": row[0], "name": row[1], "phone": row[2], "national_id": row[3], "type": row[4]} for row in rows]

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




def migrate_db():
    con = get_connection()
    cur = con.cursor()
    
    try:
        # اضافه کردن ستون‌های جدید اگر وجود ندارند
        cur.execute("ALTER TABLE transactions ADD COLUMN payment_method TEXT")
        cur.execute("ALTER TABLE transactions ADD COLUMN bank_account TEXT")
        cur.execute("ALTER TABLE transactions ADD COLUMN reference_number TEXT")
        cur.execute("ALTER TABLE transactions ADD COLUMN party_id INTEGER")
        cur.execute("ALTER TABLE transactions ADD COLUMN sim_card_id INTEGER")
    except sqlite3.OperationalError as e:
        print(f"Migration warning: {e}")
    
    con.commit()
    con.close()