import streamlit as st

# --- CORE FUNCTIONS ---
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
    return round(max(5.0, bf_percentage), 1)

def calculate_bmr(weight_kg, height_cm, age, gender):
    if gender.lower() == 'male':
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

def calculate_macros(target_calories, weight_kg, goal_type):
    protein_g = weight_kg * (2.0 if goal_type != "Maintain" else 1.6)
    protein_kcal = protein_g * 4
    fat_kcal = target_calories * 0.25
    fat_g = fat_kcal / 9
    carb_kcal = max(0, target_calories - (protein_kcal + fat_kcal))
    carb_g = carb_kcal / 4
    return round(protein_g), round(fat_g), round(carb_g)

def calculate_water_intake(weight_kg, activity_index):
    base_ml = weight_kg * 35
    activity_bonus = [0, 350, 500, 750]
    total_ml = base_ml + activity_bonus[activity_index]
    return round(total_ml / 1000, 2)

# --- STREAMLIT UI ---
st.title("💪 Advanced Health & 100-Day Goal Calculator")
st.write("Comprehensive body composition analysis, TDEE, macro split, water targets, and milestone tracking.")

with st.form("health_form"):
    col1, col2 = st.columns(2)
    with col1:
        weight_kg = st.number_input("Current Weight (kg)", min_value=0.0, max_value=300.0, value=None, placeholder="e.g., 70.0")
        height_cm = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, value=None, placeholder="e.g., 170.0")
        age = st.number_input("Age", min_value=0, max_value=120, value=None, placeholder="e.g., 25")
    with col2:
        gender = st.selectbox("Gender", ["Select Gender...", "Male", "Female"])
        activity_label = st.selectbox("Activity Level", [
            "Select Activity Level...",
            "Sedentary (little or no exercise)",
            "Lightly active (1-3 days/week)",
            "Moderately active (3-5 days/week)",
            "Very active (6-7 days a week)"
        ])
        target_weight_kg = st.number_input("Target Weight for 100 Days (kg)", min_value=0.0, max_value=300.0, value=None, placeholder="e.g., 65.0")

    submitted = st.form_submit_button("Calculate Advanced Metrics")

if submitted:
    # Validation checks for blank fields
    if not weight_kg or not height_cm or not age or gender == "Select Gender..." or activity_label == "Select Activity Level..." or not target_weight_kg:
        st.error("⚠️ Please fill in all required fields with valid values before calculating.")
    else:
        gender_str = gender.lower()
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

        # Display Core Metrics
        st.subheader("📊 Body Composition & Energy Expenditure")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("BMI", f"{bmi:.1f}", bmi_category)
        m2.metric("Body Fat", f"{body_fat}%")
        m3.metric("BMR", f"{bmr:.0f} kcal")
        m4.metric("TDEE", f"{tdee:.0f} kcal")
        
        st.info(f"**Ideal Weight Range for Height:** {min_ideal_weight:.1f} - {max_ideal_weight:.1f} kg")

        # 100-Day Strategy & Macros
        st.subheader("🎯 100-Day Strategy & Daily Targets")
        weight_diff_kg = target_weight_kg - weight_kg
        total_kcal_diff = weight_diff_kg * 7700
        daily_kcal_adjustment = total_kcal_diff / 100

        if abs(weight_diff_kg) < 0.1:
            goal_type = "Maintain"
            target_calories = tdee
            st.success("Target weight matches current weight. Focus on body recomp and maintenance.")
        elif weight_diff_kg < 0:
            goal_type = "Lose"
            target_calories = tdee + daily_kcal_adjustment
            st.write(f"**Goal:** Lose {abs(weight_diff_kg):.1f} kg over 100 days (Safe pace: ~{abs(weight_diff_kg)/14:.1f} kg/week).")
            st.write(f"**Target Calories:** {target_calories:.0f} kcal/day (Deficit of {abs(daily_kcal_adjustment):.0f} kcal/day)")
            if target_calories < bmr:
                st.warning("⚠️ Warning: Target daily intake is below your BMR. Adjust your 100-day target for safe weight loss.")
        else:
            goal_type = "Gain"
            target_calories = tdee + daily_kcal_adjustment
            st.write(f"**Goal:** Gain {weight_diff_kg:.1f} kg over 100 days.")
            st.write(f"**Target Calories:** {target_calories:.0f} kcal/day (Surplus of +{daily_kcal_adjustment:.0f} kcal/day)")

        # Macro & Water Breakdown
        protein, fat, carbs = calculate_macros(target_calories, weight_kg, goal_type)
        water_liters = calculate_water_intake(weight_kg, act_index)

        st.subheader("🍽️ Recommended Daily Nutrition & Hydration")
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Protein", f"{protein}g")
        col_b.metric("Fats", f"{fat}g")
        col_c.metric("Carbs", f"{carbs}g")
        col_d.metric("Water Intake", f"{water_liters} L/day")

        # 100-Day Milestone Checkpoints
        st.subheader("📈 100-Day Milestone Checkpoints")
        step = weight_diff_kg / 4
        st.markdown(
            f"* **Day 25:** {weight_kg + step:.1f} kg\n"
            f"* **Day 50:** {weight_kg + (step * 2):.1f} kg\n"
            f"* **Day 75:** {weight_kg + (step * 3):.1f} kg\n"
            f"* **Day 100:** {target_weight_kg:.1f} kg"
        )
