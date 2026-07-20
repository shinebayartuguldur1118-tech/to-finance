import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(
    page_title="T&O Finance",
    page_icon="💰",
    layout="wide"
)

DATA_FILE = "finance_data.json"

# -----------------
# SAVE / LOAD
# -----------------

def save_data():

    data = {
        "apartment_fund": st.session_state.apartment_fund,
        "education_fund": st.session_state.education_fund,
        "history": st.session_state.history,
        "rent_paid": st.session_state.rent_paid,
        "utilities_paid": st.session_state.utilities_paid
    }

    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def load_data():

    if os.path.exists(DATA_FILE):

        with open(DATA_FILE, "r") as f:
            return json.load(f)

    return None


# -----------------
# INIT
# -----------------

loaded = load_data()

if "initialized" not in st.session_state:

    if loaded:

        st.session_state.apartment_fund = loaded.get(
            "apartment_fund",
            0
        )

        st.session_state.education_fund = loaded.get(
            "education_fund",
            0
        )

        st.session_state.history = loaded.get(
            "history",
            []
        )

        st.session_state.rent_paid = loaded.get(
            "rent_paid",
            False
        )

        st.session_state.utilities_paid = loaded.get(
            "utilities_paid",
            False
        )

    else:

        st.session_state.apartment_fund = 0
        st.session_state.education_fund = 0
        st.session_state.history = []

        st.session_state.rent_paid = False
        st.session_state.utilities_paid = False

    st.session_state.initialized = True

# -----------------
# DATE
# -----------------

today = datetime.now()

salary_dates = [
    ("Oyuki", 1),
    ("Tuguldur", 10),
    ("Oyuki", 15),
    ("Tuguldur", 25)
]

next_salary = None

for person, day in salary_dates:

    salary_date = datetime(
        today.year,
        today.month,
        day
    )

    if salary_date > today:

        next_salary = (
            person,
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

# -----------------
# AUTO RESET
# -----------------

if today.day >= 5:
    st.session_state.utilities_paid = False

if today.month % 2 == 1 and today.day >= 10:
    st.session_state.rent_paid = False

# -----------------
# MENU
# -----------------

page = st.sidebar.selectbox(
    "Menu",
    [
        "🏠 Dashboard",
        "🏦 Savings",
        "💵 Add Salary",
        "📜 History",
        "⚙️ Settings"
    ]
)

# -----------------
# DASHBOARD
# -----------------

if page == "🏠 Dashboard":

    total_savings = (
        st.session_state.apartment_fund +
        st.session_state.education_fund
    )

    st.title("💰 T&O Finance")

    st.write(
        f"### 📅 {today.strftime('%d %B %Y')}"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "🏦 Total Savings",
            f"{total_savings:,.0f} ₮"
        )

    with col2:

        st.metric(
            "⏰ Next Salary",
            f"{person_name} ({days_left} days)"
        )

    st.divider()

    st.subheader(
        "✅ Checklist"
    )

    st.checkbox(
        "🏠 Rent Paid",
        key="rent_paid"
    )

    st.checkbox(
        "⚡ Utilities Paid",
        key="utilities_paid"
    )

    save_data()

# -----------------
# SAVINGS
# -----------------

elif page == "🏦 Savings":

    st.title("🏦 Savings")

    total_savings = (
        st.session_state.apartment_fund +
        st.session_state.education_fund
    )

    st.metric(
        "🏦 Total Savings",
        f"{total_savings:,.0f} ₮"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "🏠 Apartment Fund",
            f"{st.session_state.apartment_fund:,.0f} ₮"
        )

    with col2:

        st.metric(
            "🎓 Education Fund",
            f"{st.session_state.education_fund:,.0f} ₮"
        )

# -----------------
# ADD SALARY
# -----------------

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

    st.subheader("Allocation")

    apartment = st.number_input(
        "🏠 Apartment Fund",
        min_value=0,
        step=50000
    )

    education = st.number_input(
        "🎓 Education Fund",
        min_value=0,
        step=50000
    )

    food = st.number_input(
        "🍔 Food",
        min_value=0,
        step=50000
    )

    utilities = st.number_input(
        "⚡ Utilities & Internet",
        min_value=0,
        step=50000
    )

    fuel = st.number_input(
        "⛽ Fuel",
        min_value=0,
        step=50000
    )

    date_fund = st.number_input(
        "💕 Date",
        min_value=0,
        step=50000
    )

    other = st.number_input(
        "📦 Other",
        min_value=0,
        step=50000
    )

    allocated = (
        apartment +
        education +
        food +
        utilities +
        fuel +
        date_fund +
        other
    )

    remaining = salary - allocated

    st.write(
        f"### Allocated: {allocated:,.0f} ₮"
    )

    st.write(
        f"### Remaining: {remaining:,.0f} ₮"
    )

    if st.button("Save Salary"):

        st.session_state.apartment_fund += apartment
        st.session_state.education_fund += education

        st.session_state.history.append({

            "date":
            today.strftime("%Y-%m-%d"),

            "person":
            person,

            "salary":
            salary,

            "apartment":
            apartment,

            "education":
            education,

            "food":
            food,

            "utilities":
            utilities,

            "fuel":
            fuel,

            "date_fund":
            date_fund,

            "other":
            other

        })

        save_data()

        st.success(
            "✅ Salary saved"
        )

        st.rerun()

# -----------------
# HISTORY
# -----------------

elif page == "📜 History":

    st.title("📜 History")

    if len(st.session_state.history) == 0:

        st.info(
            "No history yet."
        )

    else:

        for row in reversed(
            st.session_state.history
        ):

            with st.expander(
                f"{row['date']} | {row['person']}"
            ):

                st.write(
                    f"Salary: {row['salary']:,.0f} ₮"
                )

                st.write(
                    f"🏠 Apartment: {row['apartment']:,.0f} ₮"
                )

                st.write(
                    f"🎓 Education: {row['education']:,.0f} ₮"
                )

                st.write(
                    f"🍔 Food: {row['food']:,.0f} ₮"
                )

                st.write(
                    f"⚡ Utilities: {row['utilities']:,.0f} ₮"
                )

                st.write(
                    f"⛽ Fuel: {row['fuel']:,.0f} ₮"
                )

                st.write(
                    f"💕 Date: {row['date_fund']:,.0f} ₮"
                )

                st.write(
                    f"📦 Other: {row['other']:,.0f} ₮"
                )

# -----------------
# SETTINGS
# -----------------

elif page == "⚙️ Settings":

    st.title("⚙️ Settings")

    if st.button(
        "🗑 Reset All Data"
    ):

        st.session_state.apartment_fund = 0
        st.session_state.education_fund = 0
        st.session_state.history = []
        st.session_state.rent_paid = False
        st.session_state.utilities_paid = False

        save_data()

        st.success(
            "All data reset."
        )

        st.rerun()