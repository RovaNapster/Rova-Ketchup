import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF
import base64

# ==============================================
# 1. KONFIGURATION & SECRETS
# ==============================================
st.set_page_config(
    page_title="Rova Ketchup Pro", 
    page_icon="🍅", 
    layout="wide"
)

# Hämtas från Settings -> Secrets i Streamlit Cloud
try:
    PATIENT_NAME = st.secrets["auth"]["patient_name"]
    PASSWORD = st.secrets["auth"]["password"]
except:
    st.error("Secrets ej konfigurerade! Gå till Settings > Secrets i Streamlit Cloud.")
    st.stop()

MED_NAME = "Slinda (Drospirenon 4mg)"
TARGET_TIME_STR = "15:00"
SHEET_NAME = "Logg"

# ==============================================
# 2. HJÄLPFUNKTIONER
# ==============================================

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.markdown("<h1 style='text-align: center; color: #d62828;'>🍅 Rova Ketchup Pro</h1>", unsafe_allow_html=True)
        col_a, col_b, col_c = st.columns([1,2,1])
        with col_b:
            pwd_input = st.text_input("Lösenord:", type="password")
            if st.button("Logga in"):
                if pwd_input == PASSWORD:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Fel lösenord.")
        return False
    return True

@st.cache_resource
def get_db_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def save_entry_to_db(conn, entry_data):
    try:
        existing_data = conn.read(worksheet=SHEET_NAME)
        new_df = pd.DataFrame([entry_data])
        updated_df = pd.concat([existing_data, new_df], ignore_index=True)
        conn.update(worksheet=SHEET_NAME, data=updated_df)
        return True
    except Exception as e:
        st.error(f"Kunde inte spara: {e}")
        return False

def generate_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Klinisk Rapport: Rova Ketchup Pro", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", size=12)
    pdf.ln(5)
    pdf.cell(0, 10, f"Patient: {PATIENT_NAME}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, f"Datum: {datetime.now().strftime('%Y-%m-%d')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 10)
    cols = ["Datum", "Tid", "Typ", "Humör", "Hud"]
    for col in cols:
        pdf.cell(35, 10, col, border=1)
    pdf.ln()
    pdf.set_font("helvetica", size=10)
    if not df.empty:
        df_recent = df.tail(20)
        for _, row in df_recent.iterrows():
            pdf.cell(35, 10, str(row.get("Datum", "-")), border=1)
            pdf.cell(35, 10, str(row.get("Tid", "-")), border=1)
            pdf.cell(35, 10, str(row.get("Typ", "-")), border=1)
            pdf.cell(35, 10, str(row.get("Humör", "-")), border=1)
            pdf.cell(35, 10, str(row.get("Hud", "-")), border=1)
            pdf.ln()
    return pdf.output()

# ==============================================
# 3. GUI & STYLING (HÄR LÅG FELET TIDIGARE)
# ==============================================

if not check_password():
    st.stop()

conn = get_db_connection()

# Korrekt sätt att lägga in CSS i Python
st.markdown("""
    <style>
    .stApp {
        background-color: #fffafa;
    }
    .glass-panel {
        backdrop-filter: blur(24px);
        border: 1px solid rgba(0,0,0,0.1);
        border-radius: 15px;
        padding: 20px;
        background-color: rgba(255,255,255,0.5);
    }
    .main-header { 
        font-size: 42px; 
        color: #d62828; 
        font-weight: 800; 
        text-align: center; 
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<div class='main-header'>🍅 ROVA KETCHUP PRO</div>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>Kliniskt protokoll för {PATIENT_NAME}</p>", unsafe_allow_html=True)

# --- DASHBOARD ---
with st.sidebar:
    st.header("⚙️ Inställningar")
    cycle_start = st.date_input("Startdatum för karta", value=datetime.now() - timedelta(days=1))
    st.divider()
    if st.button("🔒 Logga ut"):
        st.session_state["password_correct"] = False
        st.rerun()

day_in_cycle = (datetime.now().date() - cycle_start).days + 1
current_day_mod = ((day_in_cycle - 1) % 28) + 1
pill_type = "⚪ VITT (Aktiv)" if current_day_mod <= 24 else "🟢 GRÖNT (Placebo)"

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Dag i cykeln", f"{current_day_mod} / 28", pill_type)
with c2:
    st.metric("Måltid", TARGET_TIME_STR, "Slinda Protocol")
with c3:
    st.metric("Status", "Stabil", "Optimal nivå")

st.divider()

# --- LOGGNING ---
if st.button("✅ LOGGA DAGENS DOS NU", type="primary", use_container_width=True):
    now = datetime.now()
    entry = {
        "Datum": now.strftime("%Y-%m-%d"),
        "Tid": now.strftime("%H:%M"),
        "Typ": "Dosering",
        "Humör": "Stabil", "Hud": "Normal", "Spotting": False
    }
    if save_entry_to_db(conn, entry):
        st.success(f"Dosen registrerad kl {now.strftime('%H:%M')}!")
        st.balloons()

# --- RAPPORT ---
st.divider()
st.subheader("📄 Rapport till läkare")
if st.button("Generera PDF-rapport"):
    with st.spinner("Hämtar data..."):
        df_log = conn.read(worksheet=SHEET_NAME)
        pdf_bytes = generate_pdf_report(df_log)
        st.download_button(
            label="📥 Ladda ner PDF",
            data=pdf_bytes,
            file_name=f"Rova_Rapport_{PATIENT_NAME}.pdf",
            mime="application/pdf"
        )

st.markdown("<br><hr><center><small>© 2026 Rova Ketchup Pro Systems</small></center>", unsafe_allow_html=True)
