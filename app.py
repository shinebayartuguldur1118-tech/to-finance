import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase import create_client
import plotly.graph_objects as go
# ==================================
# CONFIG
# ==================================

st.set_page_config(
    page_title="T&O Finance V3",
    page_icon="💰",
    layout="wide"
)

SUPABASE_URL = "https://urmfanouthddjwmizdfj.supabase.co"

SUPABASE_KEY = "sb_publishable_axHkrtfFuohZLrClJpfa6g_im0wZDTP"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ==================================
# FUNCTIONS
# ==================================

def get_next_utilities_due():

    today = datetime.now()

    if today.day <= 5:

        due_date = datetime(
            today.year,
            today.month,
            5
        )

    else:

        if today.month == 12:

            due_date = datetime(
                today.year + 1,
                1,
                5
            )

        else:

            due_date = datetime(
                today.year,
                today.month + 1,
                5
            )

    return due_date

def utilities_paid_this_month(df):

    if df.empty:
        return False

    current_month = datetime.now().month
    current_year = datetime.now().year

    for _, row in df.iterrows():

        row_date = row["date"]

        if pd.isna(row_date):
            continue

        if (
            row_date.month == current_month
            and
            row_date.year == current_year
            and
            float(row["utilities"] or 0) > 0
        ):
            return True

    return False
def get_rent_progress(df):

    if df.empty:
        return 0, 3200000, 0

    today = datetime.now()

    current_month = today.month

    if current_month % 2 == 1:
        cycle_start_month = current_month
    else:
        cycle_start_month = current_month - 1

    cycle_start = datetime(
        today.year,
        cycle_start_month,
        10
    )

    cycle_end_month = cycle_start_month + 2
    cycle_end_year = today.year

    if cycle_end_month > 12:
        cycle_end_month -= 12
        cycle_end_year += 1

    cycle_end = datetime(
        cycle_end_year,
        cycle_end_month,
        10
    )

    rent_total = 0

    for _, row in df.iterrows():

        row_date = row["date"]

        if cycle_start <= row_date < cycle_end:

            rent_total += float(
                row["rent"] or 0
            )

    progress = min(
        rent_total / 3200000,
        1
    )

    return rent_total, 3200000, progress

@st.cache_data(ttl=60)
def get_history():

    response = (
        supabase
        .table("salary_history")
        .select("*")
        .order("date", desc=True)
        .execute()
    )

    return response.data


@st.cache_data(ttl=60)
def get_savings():

    response = (
        supabase
        .table("savings")
        .select("*")
        .execute()
    )

    apartment = 0
    education = 0

    for row in response.data:

        if row["fund_name"] == "Apartment":
            apartment = float(row["amount"] or 0)

        elif row["fund_name"] == "Education":
            education = float(row["amount"] or 0)

    return apartment, education

def get_next_rent_due():

    today = datetime.now()

    month = today.month
    year = today.year

    due_months = [1, 3, 5, 7, 9, 11]

    for m in due_months:

        due_date = datetime(year, m, 10)

        if due_date > today:
            return due_date

    return datetime(year + 1, 1, 10)



# ==================================
# DATA
# ==================================

today = datetime.now()

records = get_history()

history_df = pd.DataFrame(records)

apartment_fund, education_fund = get_savings()

total_savings = (
    apartment_fund +
    education_fund
)

# ==================================
# NEXT SALARY
# ==================================

salary_schedule = [
    ("Oyuk", 1),
    ("Tuguldur", 10),
    ("Oyuk", 15),
    ("Tuguldur", 25),
]

next_person = "Unknown"
days_left = 0

for person, day in salary_schedule:

    payday = datetime(
        today.year,
        today.month,
        day
    )

    if payday > today:

        next_person = person

        days_left = (
            payday - today
        ).days

        break

# ==================================
# MENU
# ==================================

page = st.sidebar.selectbox(
    "Menu",
    [
        "🏠 Dashboard",
        "🏦 Savings",
        "💰 Income & Expenses",
        "📜 History",
        "📊 Reports",
        "⚙️ Settings"
    ]
)

# ==================================
# DASHBOARD
# ==================================

if page == "🏠 Dashboard":
    next_rent_due = get_next_rent_due()

    st.title("💰 T&O Finance")

    current_month_income = 0
    current_month_expense = 0

    if not history_df.empty:

        history_df["date"] = pd.to_datetime(
            history_df["date"]
        )

        current_month = today.month
        current_year = today.year

        month_df = history_df[
            (history_df["date"].dt.month == current_month)
            &
            (history_df["date"].dt.year == current_year)
        ]

        current_month_income = (
            month_df["salary"]
            .fillna(0)
            .sum()
        )

        expense_cols = [
            "rent",
            "utilities",
            "food",
            "snacks",
            "date_fund",
            "fuel",
            "other",
            "tuguldur_personal",
            "oyuk_personal"
        ]

        current_month_expense = (

            month_df[
                expense_cols
            ]

            .fillna(0)

            .sum()

            .sum()
        )

    rent_total, rent_target, rent_progress = (
        get_rent_progress(history_df)
    )
    
    utilities_paid = (
        utilities_paid_this_month(history_df)
    )
    
    next_utilities_due = (
        get_next_utilities_due()
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "🏦 Total Savings",
            f"{total_savings:,.0f} ₮"
        )

    with c2:

        st.metric(
            "💵 Income",
            f"{current_month_income:,.0f} ₮"
        )

    with c3:

        st.metric(
            "💸 Expenses",
            f"{current_month_expense:,.0f} ₮"
        )

    with c4:

        st.metric(
            "⏰ Next Salary",
            f"{next_person} ({days_left} days)"
        )
    st.divider()

    st.subheader("🏠 Rent Progress")

    st.write(
        f"{rent_total:,.0f} / {rent_target:,.0f} ₮"
    )

    st.progress(rent_progress)

    st.write(
        f"{rent_progress * 100:.1f}%"
    )
    
    st.caption(
        f"📅 Next Due: {next_rent_due.strftime('%Y-%m-%d')}"
    )

        
    st.divider()

    st.subheader("⚡ Utilities Status")

    if utilities_paid:

        st.success(
            "✅ Utilities Paid"
        )

    else:

        st.warning(
                "⚠️ Utilities Not Paid"
            )

    st.caption(
        f"📅 Due Date: {next_utilities_due.strftime('%Y-%m-%d')}"
        )

# ==================================
# SAVINGS
# ==================================

elif page == "🏦 Savings":
    
    if not history_df.empty:

        history_df["date"] = pd.to_datetime(
        history_df["date"]
        )

        monthly = (
            history_df
            .groupby(
                history_df["date"]
                .dt.to_period("M")
            )
            [["apartment", "education"]]
            .sum()
            .cumsum()
            .reset_index()
        )

        monthly["date"] = (
            monthly["date"]
            .astype(str)
            )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=monthly["date"],
                y=monthly["apartment"],
                mode="lines+markers",
                name="Apartment Fund",
                line=dict(
                    color="#23D329",
                    width=4
                )
            )
        )

        fig.add_trace(
            go.Scatter(
                x=monthly["date"],
                y=monthly["education"],
                mode="lines+markers",
                name="Education Fund",
                line=dict(
                    color="#C79B81",
                    width=4
                )
            )
        )

        fig.update_layout(
            title="Savings Growth",
            xaxis_title="Month",
            yaxis_title="Amount (₮)",
            hovermode="x unified",
            yaxis=dict(rangemode="tozero")
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    st.title("🏦 Savings")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "🏠 Apartment Fund",
            f"{apartment_fund:,.0f} ₮"
        )

    with c2:

        st.metric(
            "🎓 Education Fund",
            f"{education_fund:,.0f} ₮"
        )

    st.divider()

    st.metric(
        "🏦 Total Savings",
        f"{total_savings:,.0f} ₮"
    )

# ==================================
# INCOME & EXPENSES
# ==================================

elif page == "💰 Income & Expenses":

    st.title("💰 Income & Expenses")

    person = st.selectbox(
        "Person",
        [
            "Tuguldur",
            "Oyuk"
        ]
    )

    salary = st.number_input(
        "Salary",
        min_value=0
    )

    apartment = st.number_input(
        "🏠 Apartment",
        min_value=0
    )

    education = st.number_input(
        "🎓 Education",
        min_value=0
    )

    rent = st.number_input(
        "🏠 Rent",
        min_value=0
    )

    utilities = st.number_input(
        "⚡ Utilities",
        min_value=0
    )

    food = st.number_input(
        "🍔 Food",
        min_value=0
    )

    snacks = st.number_input(
        "🍫 Snacks",
        min_value=0
    )

    date_fund = st.number_input(
        "💕 Date",
        min_value=0
    )

    fuel = st.number_input(
        "⛽ Fuel",
        min_value=0
    )

    tuguldur_personal = st.number_input(
        "👨 Tuguldur Personal",
        min_value=0
    )

    oyuk_personal = st.number_input(
        "👩 Oyuk Personal",
        min_value=0
    )

    other = st.number_input(
        "📦 Other",
        min_value=0
    )

    allocated = (

        apartment +
        education +
        rent +
        utilities +
        food +
        snacks +
        date_fund +
        fuel +
        tuguldur_personal +
        oyuk_personal +
        other
    )

    remaining = salary - allocated

    st.info(
        f"Allocated: {allocated:,.0f} ₮"
    )

    st.info(
        f"Remaining: {remaining:,.0f} ₮"
    )

    if st.button("💾 Save"):

        if allocated > salary:

            st.error(
                "Expenses exceed salary."
            )

        else:

            (
                supabase
                .table("salary_history")
                .insert({
                    "date": today.strftime("%Y-%m-%d"),
                    "person": person,
                    "salary": salary,
                    "apartment": apartment,
                    "education": education,
                    "rent": rent,
                    "utilities": utilities,
                    "food": food,
                    "snacks": snacks,
                    "date_fund": date_fund,
                    "fuel": fuel,
                    "other": other,
                    "tuguldur_personal": tuguldur_personal,
                    "oyuk_personal": oyuk_personal
                })
                .execute()
            )

            (
                supabase
                .table("savings")
                .update({
                    "amount":
                    apartment_fund + apartment
                })
                .eq("fund_name", "Apartment")
                .execute()
            )

            (
                supabase
                .table("savings")
                .update({
                    "amount":
                    education_fund + education
                })
                .eq("fund_name", "Education")
                .execute()
            )

            st.success(
                "✅ Saved"
            )

            st.cache_data.clear()

            st.rerun()

# ==================================
# HISTORY
# ==================================

elif page == "📜 History":

    st.title("📜 History")

    if history_df.empty:

        st.info("No history")

    else:

        st.dataframe(
            history_df,
            use_container_width=True
        )

# ==================================
# REPORTS
# ==================================
elif page == "📊 Reports":
    st.title("📊 Reports")

    if history_df.empty:

        st.warning(
        "No data available."
        )

        st.stop()
    history_df["date"] = pd.to_datetime(
        history_df["date"],
        errors="coerce"
    )


    selected_year = st.selectbox(
        "Year",
        sorted(
            history_df["date"]
            .dt.year
            .unique(),
            reverse=True
        )
    )

    selected_month = st.selectbox(
        "Month",
        [
            1,2,3,4,5,6,
            7,8,9,10,11,12
        ]
    )

    report_df = history_df[

        (history_df["date"].dt.year == selected_year)

        &

        (history_df["date"].dt.month == selected_month)

    ]

    if report_df.empty:

        st.warning(
            "No data for this month."
        )

    else:

        income = (
            report_df["salary"]
            .fillna(0)
            .sum()
        )

        expenses = (

            report_df[[
                "rent",
                "utilities",
                "food",
                "snacks",
                "date_fund",
                "fuel",
                "other",
                "tuguldur_personal",
                "oyuk_personal"
            ]]
            .fillna(0)
            .sum()
            .sum()

        )

        savings = (
            report_df["apartment"]
            .fillna(0)
            .sum()
            +
            report_df["education"]
            .fillna(0)
            .sum()
        )

        savings_rate = 0

        if income > 0:

            savings_rate = (
                savings / income
            ) * 100

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "💵 Income",
                f"{income:,.0f} ₮"
            )

        with c2:

            st.metric(
                "💸 Expenses",
                f"{expenses:,.0f} ₮"
            )

        with c3:

            st.metric(
                "🏦 Savings",
                f"{savings:,.0f} ₮"
            )

        with c4:

            st.metric(
                "📈 Savings Rate",
                f"{savings_rate:.1f}%"
            )

        pie_data = {
            "Apartment": report_df["apartment"].fillna(0).sum(),
            "Education": report_df["education"].fillna(0).sum(),
            "Rent": report_df["rent"].fillna(0).sum(),
            "Utilities": report_df["utilities"].fillna(0).sum(),
            "Food": report_df["food"].fillna(0).sum(),
            "Snacks": report_df["snacks"].fillna(0).sum(),
            "Date": report_df["date_fund"].fillna(0).sum(),
            "Fuel": report_df["fuel"].fillna(0).sum(),
            "Tuguldur": report_df["tuguldur_personal"].fillna(0).sum(),
            "Oyuk": report_df["oyuk_personal"].fillna(0).sum(),
            "Other": report_df["other"].fillna(0).sum()
        }

        pie_df = pd.DataFrame(
            {
                "Category": pie_data.keys(),
                "Amount": pie_data.values()
            }
        )

        pie_df = pie_df[
            pie_df["Amount"] > 0
        ]

        color_map = {

            "Apartment":
            "#4CAF50",

            "Education":
            "#81C784",

            "Rent":
            "#EF9A9A",

            "Utilities":
            "#FFAB91",

            "Food":
            "#FFCC80",

            "Snacks":
            "#FFCDD2",

            "Date":
            "#F48FB1",

            "Fuel":
            "#BCAAA4",

            "Tuguldur":
            "#E57373",

            "Oyuk":
            "#EF5350",

            "Other":
            "#CFD8DC"
        }

        fig = px.pie(
            pie_df,
            values="Amount",
            names="Category",
            color="Category",
            color_discrete_map=color_map,
            hole=0.35
        )
        
        fig.update_traces(
            textinfo="label+percent",
            hovertemplate=
            "<b>%{label}</b><br>" +
            "Amount: %{value:,.0f} ₮<br>" +
            "Share: %{percent}<extra></extra>"
            )

        st.plotly_chart(
            fig,
            use_container_width=True)
# ==================================
# SETTINGS
# ==================================

elif page == "⚙️ Settings":

    st.title("⚙️ Settings")

    st.warning(
        "This will delete all history and reset savings."
    )

    code = st.text_input(
        "Enter Reset Code",
        type="password"
    )

    if st.button("🗑 Reset All Data"):

        if code == "1118":

            # Delete salary history

            (
                supabase
                .table("salary_history")
                .delete()
                .neq("id", 0)
                .execute()
            )

            # Reset savings

            (
                supabase
                .table("savings")
                .update({
                    "amount": 0
                })
                .neq("id", 0)
                .execute()
            )

            st.cache_data.clear()

            st.success(
                "✅ All data reset successfully"
            )

        else:

            st.error(
                "❌ Invalid reset code"
            )