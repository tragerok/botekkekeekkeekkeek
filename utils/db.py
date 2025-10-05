import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def create_user(user_id, lang="ru"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tg (id, lang) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
        (user_id, lang)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_user(user_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM tg WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_user_by_id(user_id):
    return get_user(user_id)

def get_all_users():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM tg ORDER BY id")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

def get_users_page(page=1, page_size=20):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    offset = (page - 1) * page_size
    cur.execute("SELECT * FROM tg ORDER BY id LIMIT %s OFFSET %s", (page_size, offset))
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

def set_language(user_id, lang):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tg SET lang=%s, updated_at=NOW() WHERE id=%s", (lang, user_id))
    conn.commit()
    cur.close()
    conn.close()

def update_balance(user_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tg SET balance=balance + %s, updated_at=NOW() WHERE id=%s", (amount, user_id))
    conn.commit()
    cur.close()
    conn.close()

def set_balance(user_id, value):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tg SET balance=%s, updated_at=NOW() WHERE id=%s", (value, user_id))
    conn.commit()
    cur.close()
    conn.close()

def block_user_by_id(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tg SET blocked=TRUE WHERE id=%s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def unblock_user_by_id(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tg SET blocked=FALSE WHERE id=%s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def get_balance(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM tg WHERE id=%s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else 0

def get_all_programs():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM program ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_program_by_id(program_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM program WHERE id=%s", (program_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_all_tariffs():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM subscription_options ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_tariff_by_id(option_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM subscription_options WHERE id=%s", (option_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def update_tariff_price(option_id, new_price):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE subscription_options SET price=%s WHERE id=%s", (new_price, option_id))
    conn.commit()
    cur.close()
    conn.close()

def add_license(tg_id, program_id, hwid, valid_until, option_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO licenses (tg_id, program_id, hwid, valid_until, option_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (tg_id, program_id, hwid, valid_until, option_id))
    license_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return license_id

def get_licenses_for_user(tg_id, only_active=False):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    query = """SELECT l.*, p.name AS program_name, o.name as tariff_name, o.price as tariff_price
    FROM licenses l
    JOIN program p ON l.program_id = p.id
    JOIN subscription_options o ON l.option_id = o.id
    WHERE l.tg_id = %s"""
    if only_active:
        query += " AND l.valid_until > NOW()"
    query += " ORDER BY l.id ASC"
    cur.execute(query, (tg_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_license_by_id(license_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT l.*, p.name AS program_name, o.name as tariff_name, o.price as tariff_price
        FROM licenses l
        JOIN program p ON l.program_id = p.id
        JOIN subscription_options o ON l.option_id = o.id
        WHERE l.id=%s
    """, (license_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_all_licenses():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT l.*, p.name AS program_name, o.name as tariff_name, o.price as tariff_price
        FROM licenses l
        JOIN program p ON l.program_id = p.id
        JOIN subscription_options o ON l.option_id = o.id
        ORDER BY l.id ASC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def log_admin_action(admin_id, user_id, old_value, new_value):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO admin_log (admin_id, user_id, old_value, new_value, created_at) VALUES (%s, %s, %s, %s, NOW())",
        (admin_id, user_id, old_value, new_value)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_stats(days):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*), COALESCE(SUM(o.price),0)
        FROM licenses l
        JOIN subscription_options o ON l.option_id = o.id
        WHERE l.valid_until > NOW() - interval '%s days'
    """, (days,))
    count, money = cur.fetchone()
    cur.close()
    conn.close()
    return count, money

def renew_license(license_id, add_days):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        UPDATE licenses
        SET valid_until = valid_until + interval '%s days', updated_at=NOW()
        WHERE id=%s
        RETURNING valid_until
    """, (add_days, license_id))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result['valid_until'] if result else None

def set_hwid(license_id, hwid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE licenses SET hwid=%s, hwid_updated=NOW(), updated_at=NOW()
        WHERE id=%s
    """, (hwid, license_id))
    conn.commit()
    cur.close()
    conn.close()
