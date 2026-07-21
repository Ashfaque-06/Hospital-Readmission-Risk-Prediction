import streamlit as st
import pandas as pd
import pickle
import os

# Try importing plotly for enhanced charts, with graceful fallback
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# -------------------- PAGE SETTINGS --------------------

st.set_page_config(
    page_title="PulseGuard AI | Hospital Readmission Risk",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- CUSTOM CSS (DARK/CYAN MODERN THEME) --------------------

st.markdown("""
<style>
    /* Global Styles & Font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Background gradient */
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0f172a 100%);
        color: #e2e8f0;
    }
    
    /* Main container padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    /* Custom Glassmorphic Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.55);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(56, 189, 248, 0.3);
        box-shadow: 0 12px 35px rgba(14, 165, 233, 0.15);
    }
    
    /* Header Banner */
    .hero-header {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.15) 0%, rgba(20, 184, 166, 0.1) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #2dd4bf, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 6px 0;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
    }

    .status-badge {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #34d399;
        border-radius: 50%;
        box-shadow: 0 0 10px #34d399;
    }
    
    /* Section Headings */
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        padding-bottom: 8px;
    }
    
    /* Streamlit Input Customization */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: rgba(15, 23, 42, 0.7) !important;
        border-color: rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
    }

    div[data-baseweb="select"]:hover > div, div[data-baseweb="input"]:hover > div {
        border-color: #38bdf8 !important;
    }

    /* Primary Button Style */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 20px rgba(14, 165, 233, 0.4) !important;
        transition: all 0.3s ease !important;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(14, 165, 233, 0.6) !important;
        background: linear-gradient(135deg, #0369a1 0%, #0f766e 100%) !important;
    }

    /* Result Card Alerts */
    .high-risk-box {
        background: linear-gradient(135deg, rgba(225, 29, 72, 0.2) 0%, rgba(159, 18, 57, 0.3) 100%);
        border: 1px solid rgba(244, 63, 94, 0.4);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }

    .low-risk-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(6, 95, 70, 0.3) 100%);
        border: 1px solid rgba(52, 211, 153, 0.4);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Metric pill */
    .metric-pill {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 18px;
        text-align: center;
    }

    .metric-val {
        font-size: 1.6rem;
        font-weight: 800;
        color: #f8fafc;
    }

    .metric-lbl {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* Hide default footer */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -------------------- LOAD MODEL & ENCODERS --------------------

@st.cache_resource
def load_ml_assets():
    model_path = "rf_model.pkl"
    encoders_path = "label_encoders.pkl"
    scaler_path = "scaler.pkl"
    
    if not (os.path.exists(model_path) and os.path.exists(encoders_path) and os.path.exists(scaler_path)):
        st.error("⚠️ Model files (`rf_model.pkl`, `label_encoders.pkl`, `scaler.pkl`) missing in working directory.")
        st.stop()
        
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(encoders_path, "rb") as f:
        label_encoders = pickle.load(f)
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
        
    return model, label_encoders, scaler

model, label_encoders, scaler = load_ml_assets()

# -------------------- HERO HEADER --------------------

st.markdown("""
<div class="hero-header">
    <div>
        <h1 class="hero-title">🏥 Hospital Readmission Risk Predictor</h1>
        <p class="hero-subtitle">Advanced Clinical AI Analytics & Predictive Risk Assessment Engine</p>
    </div>
    <div class="status-badge">
        <span class="pulse-dot"></span> Random Forest Model Active
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR PRESETS & INFO --------------------

with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    st.markdown("Load pre-configured clinical profiles for quick testing.")
    
    col_p1, col_p2 = st.columns(2)
    
    if col_p1.button("🔴 High Risk Case"):
        st.session_state["age"] = 78
        st.session_state["comorbidities"] = 5
        st.session_state["los"] = 12
        st.session_state["meds"] = 14
        st.session_state["followup"] = 0
        st.session_state["prev_readmissions"] = 3
        st.session_state["risk_score"] = 88.0
        st.toast("Loaded High Risk Patient Preset", icon="🚨")
        
    if col_p2.button("🟢 Low Risk Case"):
        st.session_state["age"] = 32
        st.session_state["comorbidities"] = 0
        st.session_state["los"] = 2
        st.session_state["meds"] = 3
        st.session_state["followup"] = 2
        st.session_state["prev_readmissions"] = 0
        st.session_state["risk_score"] = 20.0
        st.toast("Loaded Low Risk Patient Preset", icon="✅")

    st.divider()
    
    st.markdown("### 📊 Model Info")
    st.info("""
    **Model Architecture:** Random Forest Classifier  
    **Preprocessing:** Label Encoding & StandardScaler  
    **Target:** 30-Day Hospital Readmission
    """)

    st.markdown("---")
    st.caption("🔒 HIPAA Compliant Simulation Environment")

# Initialize default session state values if not set
if "age" not in st.session_state: st.session_state["age"] = 55
if "comorbidities" not in st.session_state: st.session_state["comorbidities"] = 2
if "los" not in st.session_state: st.session_state["los"] = 5
if "meds" not in st.session_state: st.session_state["meds"] = 6
if "followup" not in st.session_state: st.session_state["followup"] = 1
if "prev_readmissions" not in st.session_state: st.session_state["prev_readmissions"] = 0
if "risk_score" not in st.session_state: st.session_state["risk_score"] = 50.0

# -------------------- MAIN INPUT FORM (3 COLUMN GLASS CARDS) --------------------

st.markdown("### 📝 Enter Patient Clinical Profile")

col1, col2, col3 = st.columns(3)

# --- COLUMN 1: DEMOGRAPHICS ---
with col1:
    st.markdown("""
    <div class="glass-card">
        <div class="section-title">👤 Patient Demographics</div>
    """, unsafe_allow_html=True)
    
    season = st.selectbox(
        "Admission Season",
        label_encoders["season"].classes_,
        help="Season during patient admission"
    )
    
    age = st.number_input(
        "Age (Years)",
        min_value=1,
        max_value=120,
        key="age"
    )
    
    gender = st.selectbox(
        "Gender",
        label_encoders["gender"].classes_
    )
    
    region = st.selectbox(
        "Geographic Region",
        label_encoders["region"].classes_
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- COLUMN 2: CLINICAL DETAILS ---
with col2:
    st.markdown("""
    <div class="glass-card">
        <div class="section-title">🩺 Clinical & Diagnosis</div>
    """, unsafe_allow_html=True)
    
    primary_diagnosis = st.selectbox(
        "Primary Diagnosis",
        label_encoders["primary_diagnosis"].classes_
    )
    
    treatment_type = st.selectbox(
        "Treatment Type",
        label_encoders["treatment_type"].classes_
    )
    
    length_of_stay = st.number_input(
        "Length of Stay (Days)",
        min_value=1,
        key="los"
    )
    
    comorbidities_count = st.number_input(
        "Comorbidities Count",
        min_value=0,
        key="comorbidities"
    )
    
    medications_count = st.number_input(
        "Prescribed Medications",
        min_value=0,
        key="meds"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- COLUMN 3: MEDICAL HISTORY & DISPOSITION ---
with col3:
    st.markdown("""
    <div class="glass-card">
        <div class="section-title">📊 History & Discharge</div>
    """, unsafe_allow_html=True)
    
    followup_visits_last_year = st.number_input(
        "Follow-up Visits (Last Year)",
        min_value=0,
        key="followup"
    )
    
    prev_readmissions = st.number_input(
        "Previous Readmissions",
        min_value=0,
        key="prev_readmissions"
    )
    
    insurance_type = st.selectbox(
        "Insurance Type",
        label_encoders["insurance_type"].classes_
    )
    
    discharge_disposition = st.selectbox(
        "Discharge Disposition",
        label_encoders["discharge_disposition"].classes_
    )
    
    readmission_risk_score = st.slider(
        "Clinical Readmission Risk Index",
        min_value=0.0,
        max_value=100.0,
        key="risk_score",
        help="Initial screening risk assessment score (0-100)"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- PREDICTION LOGIC & DASHBOARD --------------------

st.markdown("<br>", unsafe_allow_html=True)
predict_clicked = st.button("⚡ Calculate Readmission Risk Score", use_container_width=True)

if predict_clicked:
    # Encode categorical inputs
    season_encoded = label_encoders["season"].transform([season])[0]
    gender_encoded = label_encoders["gender"].transform([gender])[0]
    region_encoded = label_encoders["region"].transform([region])[0]
    diagnosis_encoded = label_encoders["primary_diagnosis"].transform([primary_diagnosis])[0]
    treatment_encoded = label_encoders["treatment_type"].transform([treatment_type])[0]
    insurance_encoded = label_encoders["insurance_type"].transform([insurance_type])[0]
    discharge_encoded = label_encoders["discharge_disposition"].transform([discharge_disposition])[0]

    # Create DataFrame with EXACT feature order
    input_data = pd.DataFrame([{
        "season": season_encoded,
        "age": age,
        "gender": gender_encoded,
        "region": region_encoded,
        "primary_diagnosis": diagnosis_encoded,
        "comorbidities_count": comorbidities_count,
        "length_of_stay": length_of_stay,
        "treatment_type": treatment_encoded,
        "medications_count": medications_count,
        "followup_visits_last_year": followup_visits_last_year,
        "prev_readmissions": prev_readmissions,
        "insurance_type": insurance_encoded,
        "discharge_disposition": discharge_encoded,
        "readmission_risk_score": readmission_risk_score
    }])

    # Scale input
    input_scaled = scaler.transform(input_data)

    # Predict
    prediction = model.predict(input_scaled)[0]
    probability = model.predict_proba(input_scaled)[0]
    
    prob_low = probability[0] * 100
    prob_high = probability[1] * 100

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 📈 Patient Risk Analytics Dashboard")
    
    res_col1, res_col2 = st.columns([1.2, 1])

    with res_col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        if prediction == 1:
            st.markdown(f"""
            <div class="high-risk-box">
                <h2 style="color: #f43f5e; margin:0 0 10px 0; font-size: 1.8rem; font-weight:800;">
                    ⚠️ HIGH RISK OF READMISSION
                </h2>
                <p style="color: #fecdd3; margin:0; font-size: 1rem;">
                    Patient exhibits elevated clinical readmission markers within 30 days of discharge.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="low-risk-box">
                <h2 style="color: #34d399; margin:0 0 10px 0; font-size: 1.8rem; font-weight:800;">
                    ✅ LOW RISK OF READMISSION
                </h2>
                <p style="color: #a7f3d0; margin:0; font-size: 1rem;">
                    Standard post-discharge follow-up protocol is recommended for this patient profile.
                </p>
            </div>
            """, unsafe_allow_html=True)

        # Dual Metric Indicators
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown(f"""
            <div class="metric-pill">
                <div class="metric-lbl">Low Risk Probability</div>
                <div class="metric-val" style="color: #34d399;">{prob_low:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""
            <div class="metric-pill">
                <div class="metric-lbl">High Risk Probability</div>
                <div class="metric-val" style="color: #f43f5e;">{prob_high:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Risk Distribution Gauge")
        st.progress(float(prob_high / 100))
        st.caption(f"Confidence Level: **{max(prob_low, prob_high):.1f}%**")

        st.markdown("</div>", unsafe_allow_html=True)

    with res_col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        if HAS_PLOTLY:
            # Interactive Donut Chart using Plotly
            fig = go.Figure(data=[go.Pie(
                labels=['Low Risk', 'High Risk'],
                values=[prob_low, prob_high],
                hole=.6,
                marker_colors=['#10b981', '#f43f5e'],
                textinfo='label+percent',
                insidetextorientation='radial'
            )])
            fig.update_layout(
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0', family='Plus Jakarta Sans'),
                height=240
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("#### Key Clinical Recommendations")

        if prediction == 1:
            st.markdown("""
            **📋 High Risk Action Plan:**
            - 🗓️ Schedule post-discharge follow-up within **48-72 hours**.
            - 💊 Perform comprehensive **medication reconciliation** prior to discharge.
            - 📞 Assign a dedicated **care coordinator** for 30-day monitoring.
            - 🏡 Evaluate home healthcare support eligibility.
            """)
        else:
            st.markdown("""
            **📋 Routine Care Protocol:**
            - 🗓️ Schedule standard follow-up appointment within **10-14 days**.
            - 📑 Provide clear discharge medication instructions.
            - 📱 Ensure patient access to telehealth portal for non-emergency inquiries.
            """)

        st.markdown("</div>", unsafe_allow_html=True)
