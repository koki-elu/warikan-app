import os
import sqlite3

from config import DATA_DIR, DB_PATH, DEFAULT_MEMBERS


def _connect():
    os.makedirs(DATA_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS members (name TEXT PRIMARY KEY)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, location TEXT)
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT, payment_id INTEGER, member_name TEXT, amount INTEGER, is_settled INTEGER DEFAULT 0,
            FOREIGN KEY(payment_id) REFERENCES payments(id)
        )
    """)
    conn.commit()
    conn.close()


def set_default_members():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM members")
    if cursor.fetchone()[0] == 0:
        for name in DEFAULT_MEMBERS:
            cursor.execute("INSERT INTO members (name) VALUES (?)", (name,))
        conn.commit()
    conn.close()


def get_members():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM members")
    members = [row[0] for row in cursor.fetchall()]
    conn.close()
    return members


def add_member(name):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO members (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def create_payment(date, location, member_amounts):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO payments (date, location) VALUES (?, ?)", (str(date), location))
    payment_id = cursor.lastrowid
    for member, mem_amount in member_amounts.items():
        cursor.execute(
            "INSERT INTO payment_details (payment_id, member_name, amount) VALUES (?, ?, ?)",
            (payment_id, member, mem_amount),
        )
    conn.commit()
    conn.close()


def get_unpaid_details():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pd.id, pd.member_name, p.date, p.location, pd.amount
        FROM payment_details pd JOIN payments p ON pd.payment_id = p.id WHERE pd.is_settled = 0 ORDER BY p.date DESC
    """)
    details = cursor.fetchall()
    conn.close()
    return details


def settle_detail(detail_id):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE payment_details SET is_settled = 1 WHERE id = ?", (detail_id,))
    conn.commit()
    conn.close()


def get_settled_details():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.date, p.location, pd.member_name, pd.amount
        FROM payment_details pd JOIN payments p ON pd.payment_id = p.id WHERE pd.is_settled = 1 ORDER BY p.date DESC
    """)
    details = cursor.fetchall()
    conn.close()
    return details


def get_all_payments():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, location FROM payments ORDER BY date DESC")
    payments = cursor.fetchall()
    conn.close()
    return payments


def get_payment(payment_id):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT date, location FROM payments WHERE id = ?", (payment_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def get_payment_details(payment_id):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, member_name, amount FROM payment_details WHERE payment_id = ?", (payment_id,))
    details = cursor.fetchall()
    conn.close()
    return details


def update_payment(payment_id, date, location, edit_amounts):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE payments SET date = ?, location = ? WHERE id = ?", (str(date), location, payment_id))
    for detail_id, new_amt in edit_amounts.items():
        cursor.execute("UPDATE payment_details SET amount = ? WHERE id = ?", (new_amt, detail_id))
    conn.commit()
    conn.close()


def delete_payment(payment_id):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payment_details WHERE payment_id = ?", (payment_id,))
    cursor.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()
