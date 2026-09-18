import streamlit as st
import pandas as pd
import numpy as np
import pickle

# --- 1. SET UP THE PAGE ---
st.set_page_config(page_title="HR Attrition Predictor", page_icon="🏢", layout="centered")
st.title("🏢 Employee Attrition Prediction App")
st.write("Enter the employee's details below to predict their likelihood of leaving the company.")

# --- 2. LOAD THE MODEL ---
@st.cache_resource
def load_model():
    with open('rf_attrition_model.pkl', 'rb') as file:
        model = pickle.load(file)
    return model

model = load_model()

# --- 3. GATHER USER INPUTS ---
st.header("Employee Profile")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age", min_value=18, max_value=65, value=30)
    monthly_income = st.number_input("Monthly Income ($)", min_value=1000, max_value=20000, value=5000, step=500)
    distance_from_home = st.number_input("Distance From Home (miles)", min_value=1, max_value=50, value=10)
    years_at_company = st.number_input("Years at Company", min_value=0, max_value=40, value=5)
    over_time = st.selectbox("Works Overtime?", ["Yes", "No"])

with col2:
    job_satisfaction = st.slider("Job Satisfaction (1=Low, 4=High)", 1, 4, 3)
    environment_satisfaction = st.slider("Environment Satisfaction (1=Low, 4=High)", 1, 4, 3)
    work_life_balance = st.slider("Work-Life Balance (1=Bad, 4=Excellent)", 1, 4, 3)
    business_travel = st.selectbox("Business Travel Frequency", ["Travel_Rarely", "Travel_Frequently", "Non-Travel"])
    department = st.selectbox("Department", ["Research & Development", "Sales", "Human Resources"])

# --- 4. PREPROCESS INPUTS TO MATCH MODEL EXPECTATIONS ---
# Create a dictionary of the inputs
input_dict = {
    'Age': age,
    'MonthlyIncome': monthly_income,
    'DistanceFromHome': distance_from_home,
    'YearsAtCompany': years_at_company,
    'JobSatisfaction': job_satisfaction,
    'EnvironmentSatisfaction': environment_satisfaction,
    'WorkLifeBalance': work_life_balance,
    'OverTime': over_time,
    'BusinessTravel': business_travel,
    'Department': department
    # Note: Add any other features here that your model was trained on
}

# Convert to DataFrame
input_df = pd.DataFrame([input_dict])

# Convert categorical variables into dummy variables just like in training
input_encoded = pd.get_dummies(input_df)

# IMPORTANT: Ensure the web app columns perfectly match the training columns
# Extract the expected feature names directly from the loaded model
expected_features = model.feature_names_in_

# Add missing columns (features present in training but missing in this single user input)
for col in expected_features:
    if col not in input_encoded.columns:
        input_encoded[col] = 0

# Ensure the column order perfectly matches the training data
input_encoded = input_encoded[expected_features]


# --- 5. MAKE PREDICTION ---
st.markdown("---")
if st.button("Predict Attrition Risk", type="primary"):
    
    # Get prediction and probability
    prediction = model.predict(input_encoded)[0]
    probability = model.predict_proba(input_encoded)[0][1] # Probability of 'Yes' (1)
    
    st.subheader("Prediction Results:")
    
    if prediction == 1:
        st.error(f"⚠️ **High Risk of Attrition**")
        st.write(f"The model predicts this employee is likely to leave. (Risk Score: {probability*100:.1f}%)")
    else:
        st.success(f"✅ **Low Risk of Attrition**")
        st.write(f"The model predicts this employee is likely to stay. (Risk Score: {probability*100:.1f}%)")