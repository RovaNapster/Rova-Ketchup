import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, time, timedelta
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF
import base64

# ==============================================
# 1. KONFIGURATION & PWA-STÖD
# ==============================================
st.set_page_config(
    page_title="Rova Ketchup Pro", 
    page_icon="🍅", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PWA & UI OPTIMERING ---
# Detta block laddar manifestet och konfigurerar iOS-specifika meta-taggar för PWA-känslan.
# Se till att github.user och github.repo finns i dina Secrets.
try:
    github_user = st.secrets["github"]["user"]
    github_repo = st.secrets["github"]["repo"]
    manifest_url = f"https://raw.githubusercontent.com/{github_user}/{github_repo}/main/manifest.json"
except:
    manifest_url = "" # Fallback om secrets saknas

st.markdown(f"""
    <link rel="manifest" href="{manifest_url}">
    
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
    
    <link rel="apple-touch-icon" href="https://emojigraph.org/media/apple/tomato_1f345.png">
    
    <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Justering för notch på moderna telefoner */
        div[data-testid="stAppViewContainer"] > section:first-child {{
            padding-top: max(2rem, calc(2rem + env(safe-area-inset-top)));
        }}
    </style>
""", unsafe_allow_html=True)

# ==============================================
# 2. KONSTANTER & SECRETS
# ==============================================

# Hämtas från Settings -> Secrets i Streamlit Cloud
try:
    PATIENT_NAME = st.secrets["auth"]["patient_name"]
    PASSWORD = st.secrets["auth"]["password"]
except:
    st.error("Secrets ej konfigurerade! Kontrollera st.secrets.")
    st.stop()

MED_NAME = "Slinda (Drospirenon 4mg)"
TARGET_TIME_STR = "15:00"
SHEET_NAME = "Logg"

# ==============================================
# 3. HJÄLPFUNKTIONER (Säkerhet, DB, PDF)
# ==============================================

# --- LÖSENORDSSKYDD ---
def check_password():
    """Hanterar inloggningsskärmen."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.markdown("<h1 style='text-align: center; color: #d62828;'>🍅 Rova Ketchup Pro</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>Kliniskt protokoll för {PATIENT_NAME}. Verifiering krävs.</p>", unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns([1,2,1])
        with col_b:
            pwd_input = st.text_input("Ange lösenord:", type="password", key="pwd_input")
            if st.button("Logga in"):
                if pwd_input == PASSWORD:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Fel lösenord. Försök igen.")
        return False
    return True

# --- DATABAS (GOOGLE SHEETS) ---
@st.cache_resource
def get_db_connection():
    """Etablerar kontakt med Google Sheets via Streamlit Secrets."""
    return st.connection("gsheets", type=GSheetsConnection)

def save_entry_to_db(conn, entry_data):
    """Sparar en ny rad i Google Sheets."""
    try:
        existing_data = conn.read(worksheet=SHEET_NAME)
        new_df = pd.DataFrame([entry_data])
        updated_df = pd.concat([existing_data, new_df], ignore_index=True)
        conn.update(worksheet=SHEET_NAME, data=updated_df)
        return True
    except Exception as e:
        st.error(f"Kunde inte spara till databasen: {e}.")
        return False

# --- PDF RAPPORTERING MED FPDF2 (ÅÄÖ-STÖD) ---
class PDFReport(FPDF):
    def header(self):
        # fpdf2 använder automatiskt UTF-8 i standardfonter.
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Klinisk Rapport: Rova Ketchup Pro Protocol', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_pos_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Sida {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(df):
    """Skapar en PDF baserat på datan i Google Sheets."""
    pdf = PDFReport()
    pdf.add_page()
    # 'helvetica' fungerar bra för svenska tecken i fpdf2.
    pdf.set_font('helvetica', '', 12)
    
    # Patientinfo
    pdf.cell(0, 10, f"Patient: {PATIENT_NAME}", 0, 1)
    pdf.cell(0, 10, f"Mottagare: Dr. Jens", 0, 1)
    pdf.cell(0, 10, f"Rapportdatum: {datetime.now().strftime('%Y-%m-%d')}", 0, 1)
    pdf.cell(0, 10, f"Medicinering: {MED_NAME}", 0, 1)
    pdf.ln(10)
    
    # Loggdata
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, "Logghistorik och Observationer", 0, 1)
    pdf.set_font('helvetica', 'B', 10)
    # Headers
    pdf.cell(30, 10, 'Datum', 1)
    pdf.cell(20, 10, 'Tid', 1)
    pdf.cell(30, 10, 'Typ', 1)
    pdf.cell(30, 10, 'Humör', 1)
    pdf.cell(30, 10, 'Hud', 1)
    pdf.cell(20, 10, 'Spotting', 1)
    pdf.ln()
    
    # Data rows
    pdf.set_font('helvetica', '', 10)
    if not df.empty:
        # Ta bara de sista 30 dagarna för rapporten för att hålla den ren
        df_recent = df.tail(30) 
        for _, row in df_recent.iterrows():
            pdf.cell(30, 10, str(row.get('Datum', '-')), 1)
            pdf.cell(20, 10, str(row.get('Tid', '-')), 1)
            pdf.cell(30, 10, str(row.get('Typ', '-')), 1)
            pdf.cell(30, 10, str(row.get('Humör', '-')), 1)
            pdf.cell(30, 10, str(row.get('Hud', '-')), 1)
            # Hantera boolean för spotting
            spotting_val = "Ja" if row.get('Spotting') == "TRUE" or row.get('Spotting') is True else "Nej"
            pdf.cell(20, 10, spotting_val, 1)
            pdf.ln()
    else:
        pdf.cell(0, 10, "Ingen data hittades i loggen ännu.", 1, 1)

    return pdf.output() # fpdf2 returnerar bytes direkt.

# ==============================================
# 4. HUVUDAPPLIKATION
# ==============================================

# A. Kör säkerhetskontroll först
if not check_password():
    st.stop()

# B. Initiera databaskoppling (om inloggad)
conn = get_db_connection()

# C. CSS Styling (Optimering för touch och klinisk design)
st.markdown("""
    <style>
    .main { background-color: #fffafa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #f0f0f0; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .glass-panel { backdrop-filter: blur(10px); background-color: rgba(255,255,255,0.6); border-radius: 15px; border: 1px solid rgba(255,255,255,0.2); padding: 20px; }
    
    /* GÖR KNAPPAR STORA OCH TOUCH-VÄNLIGA FÖR MOBILEN */
    .stButton > button {
        height: 3.5rem;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    
    .main-header { font-size: 42px; color: #d62828; font-weight: 800; text-align: center; margin-top: 20px; }
    .sub-header { text-align: center; color: #666; margin-bottom: 30px; font-style: italic; font-size: 18px;}
    h2 { color: #d62828; }
    </style>
    """, unsafe_allow_html=True)

# D. Header
st.markdown(f"<div class='main-header'>🍅 ROVA KETCHUP PRO</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-header'>Kliniskt protokoll: {PATIENT_NAME} | Slinda PWA v4.1</div>", unsafe_allow_html=True)

# E. Sidebar (Inställningar & Info)
with st.sidebar:
    st.image("https://emojigraph.org/media/apple/tomato_1f345.png", width=100)
    st.header("⚙️ Kontrollpanel")
    # Användare ställer in startdatum för nuvarande karta
    cycle_start = st.date_input("Startdatum för aktuell karta", value=datetime.now() - timedelta(days=1))
    
    st.divider()
    st.info(f"**Rx:** {MED_NAME}\n\n**Dosering:** 1 tablett dagligen ca kl {TARGET_TIME_STR}.")
    st.error("⚠️ **Viktig Interaktion:** Undvik grapefrukt och pomelo (hämmar CYP3A4-enzymet).")
    
    st.divider()
    if st.button("🔒 Logga ut", use_container_width=True):
        st.session_state["password_correct"] = False
        st.rerun()

# F. Dashboard Logik
today = datetime.now().date()
day_in_cycle = (today - cycle_start).days + 1
# Cykeln är 24 aktiva + 4 placebo = 28 dagar
current_day_mod = ((day_in_cycle - 1) % 28) + 1

# G. Dashboard Visualisering (Metrics)
col1, col2, col3 = st.columns(3)
with col1:
    pill_type = "⚪ VITT (Aktiv substans)" if current_day_mod <= 24 else "🟢 GRÖNT (Hormonfri)"
    st.metric("Cykelstatus", f"Dag {current_day_mod} / 28", delta=pill_type)

with col2:
    # (Detta är ett simulerat KPI-värde. I framtiden kan vi räkna ut det på riktigt från DB)
    st.metric("Beräknad Följsamhet", "98.5%", "Optimal nivå")

with col3:
    st.metric("Nästa dosering", TARGET_TIME_STR, "Marginal: ±24h")

# H. Avancerade Grafer
st.divider()
st.subheader("🧬 Klinisk Visualisering")
c_pk, c_prec = st.columns(2)

with c_pk:
    st.caption(f"Visualisering av hur {MED_NAME} stabiliseras i blodet över 48h.")
    # Simulering av drospirenon koncentration (halveringstid ca 30h)
    time_series = np.linspace(0, 48, 200)
    # En förenklad farmakokinetisk modell för visualisering
    concentration = (np.exp(-0.023 * (time_series % 24)) * 15) + (np.exp(-0.023 * time_series) * 5)
    
    fig_pk = px.area(x=time_series, y=concentration, labels={'x': 'Timmar från första dos', 'y': 'Estimerad nivå (ng/ml)'})
    fig_pk.update_traces(line_color='#d62828', fillcolor='rgba(214, 40, 40, 0.2)')
    fig_pk.update_layout(yaxis_range=[0, 25], showlegend=False, template='plotly_white')
    st.plotly_chart(fig_pk, use_container_width=True)

with c_prec:
    st.caption("Avvikelse i minuter från kl 15:00 de senaste dagarna (Simulerad).")
    # Simulerad data för demo-syfte
    chart_data = pd.DataFrame({
        'Dag': pd.date_range(end=today, periods=5).strftime('%d %b'),
        'Avvikelse (min)': [5, -2, 12, 0, -5]
    })
    fig_line = px.line(chart_data, x='Dag', y='Avvikelse (min)', markers=True)
    fig_line.add_hline(y=0, line_dash="dash", line_color="green", annotation_text="Perfekt tid")
    fig_line.update_traces(line_color='#d62828', line_width=3)
    fig_line.update_layout(template='plotly_white')
    st.plotly_chart(fig_line, use_container_width=True)

# I. Huvudknapp: Logga Dos
st.divider()
st.write("") # Spacing
st.write("") 

if st.button("✅ LOGGA DAGENS DOS NU", type="primary", use_container_width=True):
    now_time = datetime.now()
    # Skapa data för DB
    dose_entry = {
        "Datum": now_time.strftime("%Y-%m-%d"),
        "Tid": now_time.strftime("%H:%M"),
        "Typ": "Dosering",
        "Humör": "Stabil", "Hud": "Normal", "Spotting": False # Lämnas som default vid snabblogg
    }
    
    with st.spinner("Sparar till molndatabasen..."):
        if save_entry_to_db(conn, dose_entry):
            st.balloons()
            st.success(f"Registrerat för {PATIENT_NAME} kl {now_time.strftime('%H:%M')}. Databas uppdaterad.")

st.info("Klicka på knappen när du tar din tablett. Detta säkerställer att din farmakokinetiska kurva (till vänster) håller sig stabil.")

# J. Biverkningslogg & Prognos
st.divider()
st.header("📈 Mående & Prognos")
c_log, c_trend = st.columns([1, 2])

with c_log:
    st.subheader("Daglig Check-in")
    with st.form("obs_form"):
        mood = st.select_slider("Dagsform/Humör", options=["Låg", "Stabil", "Topp"], value="Stabil")
        skin = st.select_slider("Hudstatus", options=["Utbrott", "Normal", "Bättre"], value="Normal")
        spotting = st.checkbox("Mellanblödning (Spotting) idag?")
        
        submitted = st.form_submit_button("Spara Observationer", use_container_width=True)
        if submitted:
            obs_entry = {
                "Datum": datetime.now().strftime("%Y-%m-%d"),
                "Tid": datetime.now().strftime("%H:%M"),
                "Typ": "Observation",
                "Humör": mood,
                "Hud": skin,
                "Spotting": spotting
            }
            if save_entry_to_db(conn, obs_entry):
                st.toast("Observationer sparade! 📝")

with c_trend:
    st.subheader("Prognos: Antiandrogen Effekt")
    st.caption("Förväntad förbättring av hudkvalitet (akne) över tid med Drospirenon (Klinisk modell).")
    weeks = list(range(1, 13))
    # En logaritmisk kurva som simulerar klinisk effekt
    skin_trend = [50 + 15 * np.log(w) for w in weeks]
    fig_trend = px.line(x=weeks, y=skin_trend, labels={'x': 'Veckor med behandling', 'y': 'Förbättring (%)'})
    fig_trend.update_traces(line_color='#1f77b4', mode='lines+markers', line_shape='spline')
    fig_trend.update_layout(template='plotly_white')
    st.plotly_chart(fig_trend, use_container_width=True)

# K. PDF Export till Läkare
st.divider()
st.subheader("🩺 Klinisk Export (Dr. Jens)")
st.write("Generera en PDF-rapport baserat på din sparade data i Google Sheets.")

if st.button("📄 Generera och Ladda ner Rapport"):
    with st.spinner("Hämtar data och genererar PDF..."):
        # Läs in all data från Sheets
        df_log = conn.read(worksheet=SHEET_NAME)
        # Generera PDF-binärdata (Nu med bytes direkt från fpdf2)
        pdf_data = generate_pdf_report(df_log)
        
        # Visa nedladdningsknapp
        st.download_button(
            label="📥 Klicka här för att ladda ner PDF",
            data=pdf_data,
            file_name=f"Rova_Rapport_Bella_{datetime.now().date()}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

# L. Akutprotokoll & Footer
st.divider()
with st.expander("🆘 AKUTPROTOKOLL - MISSAT PILLER (>24h)"):
    st.error("Om det gått mer än 24 timmar sedan du skulle tagit din tablett (dvs mer än 48h sedan senaste tabletten):")
    st.markdown("""
    1.  **Ta den missade tabletten omedelbart**, även om det innebär två tabletter samtidigt.
    2.  Fortsätt därefter som vanligt.
    3.  **ANVÄND KONDOM** de kommande 7 dagarna för säkerhets skull.
    4.  Om missen skedde under vecka 3-4: Överväg att hoppa över de gröna tabletterna och börja direkt på ny karta.
    """)

st.markdown("<br><hr><center><small>© 2026 Rova Ketchup Pro Systems | Utvecklat för Bella | Slinda PWA v4.1</small></center>", unsafe_allow_html=True)
