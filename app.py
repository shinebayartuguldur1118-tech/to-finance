import streamlit as st
from datetime import datetime
import json
import os

# =====================
# SETTINGS
# =====================

st.set_page_config(
    page_title="T&O Finance",
    page_icon="💰",
    layout="wide"
)

# =====================
# MENU
# =====================

st.sidebar.title("💰 T&O Finance")

page = st.sidebar.selectbox(
    "Menu",
    [
        "🏠 Dashboard",
        "💵 Add Salary",
        "🎯 Goals",
        "📜 History",
        "✏️ Edit Funds",
        "⚙️ Settings"
    ]
)

# =====================
# FILE
# =====================

DATA_FILE = "finance_data.json"

# =====================
# FUNCTIONS
# =====================

def save_data():
    data = {
        "savings": st.session_state.savings,
        "education": st.session_state.education,
        "rent": st.session_state.rent,
        "history": st.session_state.history
    }

    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def load_data():

    if os.path.exists(DATA_FILE):

        with open(DATA_FILE, "r") as f:
            return json.load(f)

    return None

# =====================
# LOAD DATA
# =====================

loaded = load_data()

if "initialized" not in st.session_state:

    if loaded:

        st.session_state.savings = loaded.get(
            "savings", 0
        )

        st.session_state.education = loaded.get(
            "education", 0
        )

        st.session_state.rent = loaded.get(
            "rent", 0
        )

        st.session_state.history = loaded.get(
            "history", []
        )

    else:

        st.session_state.savings = 0
        st.session_state.education = 0
        st.session_state.rent = 0
        st.session_state.history = []

    st.session_state.initialized = True

# =====================
# DATE
# =====================

today = datetime.now()

salary_dates = [
    ("Oyuki", 1),
    ("Tuguldur", 10),
    ("Oyuki", 15),
    ("Tuguldur", 25)
]

next_salary = None

for person_name, day in salary_dates:

    salary_date = datetime(
        today.year,
        today.month,
        day
    )

    if salary_date > today:

        next_salary = (
            person_name,
            salary_date
        )
        break

if next_salary is None:

    next_salary = (
        "Oyuki",
        datetime(
            today.year + 1,
            1,
            1
        )
    )

person_name, payday = next_salary

days_left = (payday - today).days

# =====================
# DASHBOARD
# =====================

if page == "🏠 Dashboard":

    st.title("💰 Tuguldur & Oyuki Finance")
    st.markdown(
        f"### 📅 {today.strftime('%d %B %Y')}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🏦 Savings",
            f"{st.session_state.savings:,.0f} ₮"
        )

    with col2:
        st.metric(
            "🎓 Education Fund",
            f"{st.session_state.education:,.0f} ₮"
        )

    
    with col3:
        st.metric(
             "⏰ Next Salary",
            f"{person_name} ({days_left} days)"
        )


# =====================
# ADD SALARY
# =====================

elif page == "💵 Add Salary":

    st.title("💵 Add Salary")

    person = st.selectbox(
        "Person",
        ["Tuguldur", "Oyuki"]
    )

    salary = st.number_input(
        "Salary Amount (₮)",
        min_value=0,
        step=100000
    )

    if st.button("Add Salary"):

        original_salary = salary

        if person == "Oyuki":

            education = 500000

            savings = max(
                salary - 1000000,
                0
            )

            st.session_state.education += education
            st.session_state.savings += savings

            st.success(
                f"🎓 Education +500,000 ₮"
            )

            st.success(
                f"🏦 Savings +{savings:,.0f} ₮"
            )

        else:

            rent_needed = max(
                0,
                3200000 - st.session_state.rent
            )

            rent_add = min(
                salary,
                rent_needed
            )

            st.session_state.rent += rent_add

            salary -= rent_add

            st.session_state.savings += salary

            st.success(
                f"🏠 Rent Fund +{rent_add:,.0f} ₮"
            )

            st.success(
                f"🏦 Savings +{salary:,.0f} ₮"
            )

        st.session_state.history.append(
            {
                "date": today.strftime("%Y-%m-%d"),
                "person": person,
                "amount": original_salary
            }
        )

        save_data()

        st.rerun()

# =====================
# GOALS
# =====================

elif page == "🎯 Goals":

    st.title("🎯 Apartment Goal")

    goal = 50000000

    progress = st.session_state.savings / goal

    if progress > 1:
        progress = 1

    st.progress(progress)

    st.write(
        f"{st.session_state.savings:,.0f} ₮ / {goal:,.0f} ₮"
    )

# =====================
# HISTORY
# =====================

elif page == "📜 History":

    st.title("📜 Salary History")

    if len(st.session_state.history) == 0:

        st.info("No salary records yet.")

    else:

        for i in range(
            len(st.session_state.history) - 1,
            -1,
            -1
        ):

            row = st.session_state.history[i]

            col1, col2 = st.columns([8, 1])

            with col1:

                st.write(
                    f"📅 {row['date']} | "
                    f"👤 {row['person']} | "
                    f"💰 {row['amount']:,.0f} ₮"
                )

            with col2:

                if st.button(
                    "❌",
                    key=f"delete_{i}"
                ):

                    st.session_state.history.pop(i)

                    save_data()

                    st.rerun()

# =====================
# EDIT FUNDS
# =====================

elif page == "✏️ Edit Funds":

    st.title("✏️ Edit Funds")

    new_savings = st.number_input(
        "Savings",
        value=float(st.session_state.savings),
        step=100000.0
    )

    new_education = st.number_input(
        "Education Fund",
        value=float(st.session_state.education),
        step=100000.0
    )

    new_rent = st.number_input(
        "Rent Fund",
        value=float(st.session_state.rent),
        step=100000.0
    )

    if st.button("💾 Save Changes"):

        st.session_state.savings = new_savings
        st.session_state.education = new_education
        st.session_state.rent = new_rent

        save_data()

        st.success(
            "✅ Data updated successfully!"
        )

        st.rerun()

# =====================
# SETTINGS
# =====================

elif page == "⚙️ Settings":

    st.title("⚙️ Settings")

    st.warning(
        "This will delete all saved data."
    )

    if st.button("🗑 Reset All Data"):

        st.session_state.savings = 0
        st.session_state.education = 0
        st.session_state.rent = 0
        st.session_state.history = []

        save_data()

        st.success(
            "✅ All data has been reset."
        )

        st.rerun()