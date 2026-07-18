import streamlit as st
import pandas as pd
import pickle

# -------------------- PAGE SETTINGS --------------------

st.set_page_config(
    page_title="Hospital Readmission Prediction",
    page_icon="🏥",
    layout="centered"
)

st.title("🏥 Hospital Readmission Risk Prediction")
st.markdown("### Enter the patient details below")

# -------------------- LOAD FILES --------------------

with open("rf_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("label_encoders.pkl", "rb") as f:
    label_encoders = pickle.load(f)

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

# -------------------- INPUTS --------------------

season = st.selectbox(
    "Season",
    label_encoders["season"].classes_
)

age = st.number_input(
    "Age",
    min_value=1,
    max_value=120,
    value=45
)

gender = st.selectbox(
    "Gender",
    label_encoders["gender"].classes_
)

region = st.selectbox(
    "Region",
    label_encoders["region"].classes_
)

primary_diagnosis = st.selectbox(
    "Primary Diagnosis",
    label_encoders["primary_diagnosis"].classes_
)

comorbidities_count = st.number_input(
    "Comorbidities Count",
    min_value=0,
    value=2
)

length_of_stay = st.number_input(
    "Length of Stay (Days)",
    min_value=1,
    value=5
)

treatment_type = st.selectbox(
    "Treatment Type",
    label_encoders["treatment_type"].classes_
)

medications_count = st.number_input(
    "Medications Count",
    min_value=0,
    value=5
)

followup_visits_last_year = st.number_input(
    "Follow-up Visits Last Year",
    min_value=0,
    value=1
)

prev_readmissions = st.number_input(
    "Previous Readmissions",
    min_value=0,
    value=0
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
    "Readmission Risk Score",
    0.0,
    100.0,
    50.0
)
# -------------------- PREDICTION --------------------

if st.button("Predict Readmission Risk"):

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

    st.divider()

    st.subheader("Prediction Result")

    if prediction == 1:
        st.error("⚠️ High Risk of Hospital Readmission")
    else:
        st.success("✅ Low Risk of Hospital Readmission")

    st.write(f"**Probability of Low Risk:** {probability[0]*100:.2f}%")
    st.write(f"**Probability of High Risk:** {probability[1]*100:.2f}%")

    st.progress(float(max(probability)))