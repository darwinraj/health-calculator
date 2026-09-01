import streamlit as st

# --- YOUR CORE FUNCTIONS ---
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)

def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def calculate_body_fat(bmi, age, gender):
    sex_factor = 1 if gender.lower() == 'male' else 0
    bf_percentage = (1.20 * bmi) + (0.23 * age) - (10.8 * sex_factor) - 5.4
    return round(bf_percentage, 1)

def calculate_bmr(weight_kg, height_cm, age, gender):
    if gender.lower() == 'male':
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

# --- STREAMLIT UI ---
st.title("💪 Health & 100-Day Goal Calculator")
st.write("Enter your metrics below to calculate your body composition and 100-day targets.")

with st.form("health_form"):
    col1, col2 = st.columns(2)
    with col1:
        weight_kg = st.number_input("Current Weight (kg)", min_value=30.0, max_value=300.0, value=70.0)
        height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0)
        age = st.number_input("Age", min_value=10, max_value=120, value=25)
    with col2:
        gender = st.selectbox("Gender", ["Male", "Female"])
        activity_label = st.selectbox("Activity Level", [
            "Sedentary (little or no exercise)",
            "Lightly active (1-3 days/week)",
            "Moderately active (3-5 days/week)",
            "Very active (6-7 days a week)"
        ])
        target_weight_kg = st.number_input("Target Weight for 100 Days (kg)", min_value=30.0, max_value=300.0, value=65.0)

    submitted = st.form_submit_button("Calculate Metrics")

if submitted:
    # Calculations
    gender_str = gender.lower()
    weight_lbs = weight_kg * 2.20462
    bmi = calculate_bmi(weight_kg, height_cm)
    bmi_category = get_bmi_category(bmi)
    body_fat = calculate_body_fat(bmi, age, gender_str)
    
    height_m = height_cm / 100
    min_ideal_weight = 18.5 * (height_m ** 2)
    max_ideal_weight = 24.9 * (height_m ** 2)
    
    bmr = calculate_bmr(weight_kg, height_cm, age, gender_str)
    multipliers = [1.2, 1.375, 1.55, 1.725]
    act_index = [
        "Sedentary (little or no exercise)",
        "Lightly active (1-3 days/week)",
        "Moderately active (3-5 days/week)",
        "Very active (6-7 days a week)"
    ].index(activity_label)
    tdee = bmr * multipliers[act_index]

    # Display Results
    st.subheader("📊 Health & Body Composition Metrics")
    m1, m2, m3 = st.columns(3)
    m1.metric("BMI", f"{bmi:.1f}", bmi_category)
    m2.metric("Body Fat", f"{body_fat}%")
    m3.metric("BMR", f"{bmr:.0f} kcal")
    
    st.info(f"**Maintenance Calories (TDEE):** {tdee:.0f} kcal/day | **Ideal Weight Range:** {min_ideal_weight:.1f} - {max_ideal_weight:.1f} kg")

    # 100-Day Strategy
    st.subheader("🎯 100-Day Mathematical Strategy")
    weight_diff_kg = target_weight_kg - weight_kg
    total_kcal_diff = weight_diff_kg * 7700
    daily_kcal_adjustment = total_kcal_diff / 100

    if abs(weight_diff_kg) < 0.1:
        st.success("You are already at your target weight! Focus on maintenance.")
    else:
        target_calories = tdee + daily_kcal_adjustment
        if weight_diff_kg < 0:
            st.write(f"**Goal:** Lose {abs(weight_diff_kg):.1f} kg in 100 days.")
            st.write(f"**Target Daily Calorie Intake:** {target_calories:.0f} kcal/day (Deficit of {abs(daily_kcal_adjustment):.0f} kcal/day)")
            if target_calories < bmr:
                st.warning("⚠️ Warning: Your target intake drops below your BMR. Consider a more modest target.")
        else:
            st.write(f"**Goal:** Gain {weight_diff_kg:.1f} kg in 100 days.")
            st.write(f"**Target Daily Calorie Intake:** {target_calories:.0f} kcal/day (Surplus of +{daily_kcal_adjustment:.0f} kcal/day)")