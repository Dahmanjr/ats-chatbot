import streamlit as st
from collections import Counter
from chatbot import process_query
from data import SCHOOLS

st.set_page_config(
    page_title="مساعد مدارس التكنولوجيا التطبيقية",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
}

/* Hide default streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* App header */
.app-header {
    background: linear-gradient(135deg, #1a56db 0%, #0ea5e9 100%);
    padding: 20px 28px;
    border-radius: 16px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    color: white;
}
.app-header h1 { font-size: 22px; font-weight: 800; margin: 0; color: white; }
.app-header p  { font-size: 13px; margin: 0; opacity: 0.9; }

/* Stat card */
.stat-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px 18px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stat-card .num { font-size: 28px; font-weight: 800; color: #1a56db; }
.stat-card .lbl { font-size: 12px; color: #64748b; font-weight: 600; }

/* Chat container */
.chat-wrapper {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 20px;
    min-height: 420px;
    box-shadow: 0 4px 20px rgba(26,86,219,0.08);
}

/* Message bubbles */
.msg-bot {
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    margin-bottom: 12px;
    max-width: 85%;
    direction: rtl;
    text-align: right;
    font-size: 14px;
    line-height: 1.8;
}
.msg-user {
    background: linear-gradient(135deg, #1a56db, #2563eb);
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin-bottom: 12px;
    max-width: 80%;
    margin-right: auto;
    direction: rtl;
    text-align: right;
    font-size: 14px;
}
.msg-user-wrap { display: flex; justify-content: flex-end; }

/* Suggestion pills */
.pill-btn {
    display: inline-block;
    background: #e8f0fe;
    color: #1a56db;
    border-radius: 20px;
    padding: 5px 14px;
    margin: 3px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
}

/* Sidebar */
[data-testid="stSidebar"] {
    direction: rtl;
}
[data-testid="stSidebar"] .stButton button {
    width: 100%;
    text-align: right;
    background: #e8f0fe;
    color: #1a56db;
    border: 1px solid rgba(26,86,219,0.2);
    border-radius: 10px;
    font-family: 'Cairo', sans-serif;
    font-weight: 600;
    padding: 8px 14px;
    margin-bottom: 4px;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #1a56db;
    color: white;
}

/* Input */
.stTextInput input {
    direction: rtl;
    text-align: right;
    font-family: 'Cairo', sans-serif;
    border-radius: 12px;
    border: 2px solid #e2e8f0;
    padding: 10px 16px;
    font-size: 14px;
}
.stTextInput input:focus { border-color: #1a56db; }

/* Send button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1a56db, #0ea5e9);
    color: white;
    border: none;
    border-radius: 12px;
    font-family: 'Cairo', sans-serif;
    font-weight: 700;
    padding: 10px 24px;
}
</style>
""", unsafe_allow_html=True)

# ─── Session state ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""

# ─── Stats ────────────────────────────────────────────────────────────────────
total = len(SCHOOLS)
accepting = sum(1 for s in SCHOOLS if s["status"] == "تقبل طلاب جدد")
factory_count = sum(1 for s in SCHOOLS if s["factory"] == "نعم")
gov_count = len(set(s["gov"] for s in SCHOOLS))

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
  <div style="font-size:42px">🎓</div>
  <div>
    <h1>مساعد مدارس التكنولوجيا التطبيقية</h1>
    <p>اسألني عن أي مدرسة أو تخصص أو محافظة — {total} مدرسة في {gov_count} محافظة</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Stats row ────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
for col, num, lbl in [
    (c1, total, "إجمالي المدارس"),
    (c2, accepting, "تقبل طلاب جدد ✅"),
    (c3, factory_count, "داخل مصانع 🏭"),
    (c4, gov_count, "محافظة 🗺️"),
]:
    col.markdown(f"""
    <div class="stat-card">
      <div class="num">{num}</div>
      <div class="lbl">{lbl}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Layout: sidebar + chat ────────────────────────────────────────────────────
SUGGESTIONS = [
    "مدارس القاهرة",
    "مدارس الجيزة",
    "مدارس الإسكندرية",
    "تخصص البرمجة",
    "تخصص الاتصالات",
    "تخصص الذكاء الاصطناعي",
    "تخصص السيارات",
    "تخصص الفندقة",
    "تخصص الكهرباء",
    "مدارس تقبل طلاب",
    "شروط القبول",
    "الشهادات الثلاث",
    "كم عدد المدارس",
    "المحافظات والعدد",
    "مدارس داخل مصنع",
]

with st.sidebar:
    st.markdown("### 💡 أسئلة مقترحة")
    for s in SUGGESTIONS:
        if st.button(s, key=f"sug_{s}"):
            st.session_state.pending_query = s

    st.markdown("---")
    st.markdown("### 🏛️ أكثر المحافظات")
    gov_counts = Counter(s["gov"] for s in SCHOOLS)
    for gov, cnt in sorted(gov_counts.items(), key=lambda x: -x[1])[:10]:
        if st.button(f"{gov}  ({cnt})", key=f"gov_{gov}"):
            st.session_state.pending_query = f"مدارس {gov}"

    st.markdown("---")
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

# ─── Chat messages ─────────────────────────────────────────────────────────────
chat_placeholder = st.container()
with chat_placeholder:
    if not st.session_state.messages:
        st.markdown("""
        <div class="chat-wrapper" style="display:flex;align-items:center;justify-content:center;flex-direction:column;gap:12px;min-height:300px;">
          <div style="font-size:60px">🤖</div>
          <h3 style="color:#1e293b;margin:0">أهلاً بك في مساعد ATS</h3>
          <p style="color:#64748b;text-align:center;max-width:400px">
            يمكنني مساعدتك في البحث عن مدارس التكنولوجيا التطبيقية،<br>
            تخصصاتها، أماكنها، ونطاق قبولها.
          </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="msg-user-wrap"><div class="msg-user">👤 {msg["content"]}</div></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f'<div class="msg-bot">🤖&nbsp; {msg["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ─── Input area ───────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1])
with col_input:
    user_input = st.text_input(
        label="",
        placeholder="اكتب سؤالك هنا... مثال: مدارس القاهرة، تخصص البرمجة، شروط القبول",
        key="chat_input",
        label_visibility="collapsed",
    )
with col_btn:
    send_clicked = st.button("إرسال ➤", type="primary", use_container_width=True)

# ─── Process input ─────────────────────────────────────────────────────────────
query = ""
if send_clicked and user_input.strip():
    query = user_input.strip()
elif st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = ""

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.spinner("جاري البحث..."):
        response = process_query(query)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
