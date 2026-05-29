import streamlit as st
import datetime
import sqlite3
import time

# --- データベースの初期設定 ---
def init_db():
    conn = sqlite3.connect("warikan.db")
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

init_db()

def set_default_members():
    conn = sqlite3.connect("warikan.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM members")
    if cursor.fetchone()[0] == 0:
        for name in ["あおい", "しおん", "てんし", "れい"]:
            cursor.execute("INSERT INTO members (name) VALUES (?)", (name,))
        conn.commit()
    conn.close()

set_default_members()


# --- メイン画面 ---
st.title("💰 支払い・精算管理アプリ")

# 4つのタブを作成（「🛠️ データの編集」タブを新設！）
tab1, tab2, tab3, tab4 = st.tabs(["📝 請求の入力", "📊 現在の未精算状況", "✅ 精算済み履歴", "🛠️ データの編集・削除"])


# --- サイドバー：メンバー管理 ---
st.sidebar.title("👥 メンバー管理")
def get_members():
    conn = sqlite3.connect("warikan.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM members")
    members = [row[0] for row in cursor.fetchall()]
    conn.close()
    return members

current_members = get_members()

new_member = st.sidebar.text_input("新メンバーを追加", placeholder="名前を入力")
if st.sidebar.button("追加"):
    if new_member and new_member not in current_members:
        conn = sqlite3.connect("warikan.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO members (name) VALUES (?)", (new_member,))
        conn.commit()
        conn.close()
        st.sidebar.success(f"「{new_member}」を追加しました！")
        st.rerun()


# ==========================================
# タブ1：請求の入力（🔴 連打防止機能を追加！）
# ==========================================
with tab1:
    st.subheader("📝 新しい支払いを記録")
    date = st.date_input("日付", datetime.date.today())
    location = st.text_input("場所・イベント名", placeholder="例：吉川")

    st.write("👥 メンバーごとの金額を入力してください")
    if len(current_members) == 0:
        st.info("メンバーを追加してください。")
    else:
        cols = st.columns(min(len(current_members), 4))
        member_amounts = {}
        for i, member in enumerate(current_members):
            with cols[i % 4]:
                amount = st.number_input(f"{member} (円)", min_value=0, step=50, value=0, key=f"amt_{member}")
                if amount > 0:
                    member_amounts[member] = amount

        total_amount = sum(member_amounts.values())
        st.metric(label="📊 今回の合計金額", value=f"{total_amount} 円")

        if st.button("データを登録して請求を上乗せする", type="primary"):
            if total_amount == 0:
                st.error("合計金額が0円です。誰か1人以上の金額を入力してください。")
            else:
                # 🔴 解決策：st.spinner を使って処理中のぐるぐるアニメーションを表示
                with st.spinner("データをデータベースに登録中..."):
                    conn = sqlite3.connect("warikan.db")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO payments (date, location) VALUES (?, ?)", (str(date), location))
                    payment_id = cursor.lastrowid
                    for member, mem_amount in member_amounts.items():
                        cursor.execute("INSERT INTO payment_details (payment_id, member_name, amount) VALUES (?, ?, ?)", (payment_id, member, mem_amount))
                    conn.commit()
                    conn.close()
                    time.sleep(0.5) # 体感として「動いた感」を出すためのわずかなウェイト
                
                st.success(f"「{location}」の明細を登録しました！")
                st.rerun()


# ==========================================
# タブ2：現在の未精算状況
# ==========================================
with tab2:
    st.subheader("📊 現在の未精算状況")
    
    conn = sqlite3.connect("warikan.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pd.id, pd.member_name, p.date, p.location, pd.amount 
        FROM payment_details pd JOIN payments p ON pd.payment_id = p.id WHERE pd.is_settled = 0 ORDER BY p.date DESC
    """)
    unpaid_details = cursor.fetchall()
    conn.close()

    if len(current_members) > 0:
        for member in current_members:
            member_total = sum(row[4] for row in unpaid_details if row[1] == member)
            if member_total > 0:
                st.write(f"🔴 **{member} さん**: 未精算トータル **{member_total} 円**")
                with st.expander(f"➔ 明細・精算はこちら"):
                    for detail_id, m_name, p_date, p_loc, amt in unpaid_details:
                        if m_name == member:
                            col_md, col_btn = st.columns([4, 2])
                            with col_md:
                                st.write(f"📅 {p_date} | 📍 {p_loc} : **{amt} 円**")
                            with col_btn:
                                if st.button("精算", key=f"pay_{detail_id}"):
                                    with st.spinner("精算処理中..."):
                                        conn = sqlite3.connect("warikan.db")
                                        cursor = conn.cursor()
                                        cursor.execute("UPDATE payment_details SET is_settled = 1 WHERE id = ?", (detail_id,))
                                        conn.commit()
                                        conn.close()
                                    st.rerun()
            else:
                st.write(f"🟢 **{member} さん**: 未精算なし (0 円)")
    else:
        st.info("メンバーが登録されていません。")


# ==========================================
# タブ3：精算済み履歴
# ==========================================
with tab3:
    st.subheader("✅ 過去の精算済み履歴")
    conn = sqlite3.connect("warikan.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.date, p.location, pd.member_name, pd.amount 
        FROM payment_details pd JOIN payments p ON pd.payment_id = p.id WHERE pd.is_settled = 1 ORDER BY p.date DESC
    """)
    settled_details = cursor.fetchall()
    conn.close()

    if len(settled_details) > 0:
        filter_options = ["全員分を表示"] + current_members
        selected_user = st.selectbox("👤 履歴を見たいメンバーを選択", filter_options)
        st.write("---")
        
        display_count = 0
        for p_date, p_loc, m_name, amt in settled_details:
            if selected_user == "全員分を表示" or m_name == selected_user:
                st.write(f"✨ **{p_date}** | 📍 {p_loc} | 👤 **{m_name} さん** : ~~{amt} 円~~")
                display_count += 1
                
        if display_count == 0:
            st.caption(f"{selected_user} さんの精算済み履歴はまだありません。")
    else:
        st.caption("精算済みのデータはまだありません。")


# ==========================================
# 🔴 新設：タブ4：データの編集・削除機能
# ==========================================
with tab4:
    st.subheader("🛠️ 登録した練習場所や日付の変更・削除")
    st.write("過去に登録したイベントそのものを修正したり、丸ごと削除できます。")

    conn = sqlite3.connect("warikan.db")
    cursor = conn.cursor()
    # 過去のイベント一覧を取得
    cursor.execute("SELECT id, date, location FROM payments ORDER BY date DESC")
    all_payments = cursor.fetchall()
    conn.close()

    if len(all_payments) > 0:
        # 修正したいイベントを選ぶセレクトボックス
        payment_options = {f"📅 {row[1]} | 📍 {row[2]}": row[0] for row in all_payments}
        selected_event_label = st.selectbox("修正・削除するイベントを選択してください", list(payment_options.keys()))
        selected_payment_id = payment_options[selected_event_label]

        # 選択されたイベントの現在のデータをDBから引っ張る
        conn = sqlite3.connect("warikan.db")
        cursor = conn.cursor()
        cursor.execute("SELECT date, location FROM payments WHERE id = ?", (selected_payment_id,))
        p_date, p_loc = cursor.fetchone()
        
        # 内訳（メンバーごとの金額）も取得
        cursor.execute("SELECT id, member_name, amount FROM payment_details WHERE payment_id = ?", (selected_payment_id,))
        details = cursor.fetchall()
        conn.close()

        st.write("---")
        st.write("### ✏️ 内容を書き換える")
        
        # フォーム形式で編集欄を作る
        edit_date = st.date_input("日付を変更", datetime.datetime.strptime(p_date, "%Y-%m-%d").date(), key="edit_date")
        edit_location = st.text_input("場所・イベント名を変更", value=p_loc, key="edit_loc")
        
        st.write("👤 各メンバーの金額を変更")
        edit_amounts = {}
        for detail_id, member_name, amount in details:
            edit_amounts[detail_id] = st.number_input(f"{member_name} の金額", min_value=0, value=amount, step=50, key=f"edit_amt_{detail_id}")

        col_update, col_delete = st.columns(2)
        
        # 変更保存ボタン
        with col_update:
            if st.button("変更を保存する", type="primary", key="btn_update"):
                with st.spinner("データを更新中..."):
                    conn = sqlite3.connect("warikan.db")
                    cursor = conn.cursor()
                    # 1. 親元のイベント情報を更新
                    cursor.execute("UPDATE payments SET date = ?, location = ? WHERE id = ?", (str(edit_date), edit_location, selected_payment_id))
                    # 2. 子元のメンバー別金額を更新
                    for detail_id, new_amt in edit_amounts.items():
                        cursor.execute("UPDATE payment_details SET amount = ? WHERE id = ?", (new_amt, detail_id))
                    conn.commit()
                    conn.close()
                    time.sleep(0.5)
                st.success("データの変更が完了しました！")
                st.rerun()

        # 丸ごと削除ボタン
        with col_delete:
            if st.button("🚨 このイベントを完全に削除する", type="secondary", key="btn_delete"):
                with st.spinner("データを削除中..."):
                    conn = sqlite3.connect("warikan.db")
                    cursor = conn.cursor()
                    # 関連する明細とイベントを両方消す
                    cursor.execute("DELETE FROM payment_details WHERE payment_id = ?", (selected_payment_id,))
                    cursor.execute("DELETE FROM payments WHERE id = ?", (selected_payment_id,))
                    conn.commit()
                    conn.close()
                    time.sleep(0.5)
                st.error("データを完全に削除しました。")
                st.rerun()
    else:
        st.info("編集可能なイベントデータがまだありません。")