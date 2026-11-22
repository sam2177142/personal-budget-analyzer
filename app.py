# Personal Budget Analyzer
# AIM111 Streamlit Independent Project
# This app uses pandas to explore income and spending from a CSV file.

import pandas as pd
import streamlit as st

# Give the web page a title and a short explanation.
st.title("💰 Personal Budget Analyzer")
st.write("Explore your income, expenses, and spending habits.")
st.write("Upload a CSV file or use the included sample transactions.")

# Let users upload their own data. The sample data is used if no file is uploaded.
# CSV files need four columns: date, description, category, amount.
uploaded_file = st.file_uploader("Upload a transaction CSV", type="csv")

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
else:
    data = pd.read_csv("data/sample_transactions.csv")

# Check that the uploaded CSV has the columns the app needs.
required_columns = ["date", "description", "category", "amount"]
if not all(column in data.columns for column in required_columns):
    st.error("The CSV must contain: date, description, category, amount")
    st.stop()

# Convert dates and amounts into types that pandas can analyze.
# Positive amounts represent income; negative amounts represent expenses.
data["date"] = pd.to_datetime(data["date"], errors="coerce")
data["amount"] = pd.to_numeric(data["amount"], errors="coerce")
data = data.dropna(subset=["date", "amount"])

if data.empty:
    st.warning("There are no valid transactions to display.")
    st.stop()

# Make a month column so users can explore one month at a time.
data["month"] = data["date"].dt.strftime("%Y-%m")

# Interactive widgets in the sidebar.
st.sidebar.header("Filters")
months = sorted(data["month"].unique(), reverse=True)
selected_month = st.sidebar.selectbox("Choose a month", months)

categories = sorted(data["category"].dropna().unique())
selected_categories = st.sidebar.multiselect(
    "Choose categories", categories, default=categories
)

monthly_budget = st.sidebar.slider(
    "Monthly spending budget ($)", 100, 5000, 1500, 100
)

# Only show transactions matching the user's selections.
filtered_data = data[
    (data["month"] == selected_month)
    & (data["category"].isin(selected_categories))
]

# Stop here if the filters don't match any transactions.
if filtered_data.empty:
    st.warning("No transactions match your filters.")
    st.stop()

# Calculate income, expenses, and the amount left over for the selected month.
income = filtered_data[filtered_data["amount"] > 0]["amount"].sum()
expenses = -filtered_data[filtered_data["amount"] < 0]["amount"].sum()
remaining = income - expenses

st.header("Monthly Overview")
st.write("Selected month:", selected_month)

# Display the results across three columns.
col1, col2, col3 = st.columns(3)
col1.metric("Income", f"${income:,.2f}")
col2.metric("Expenses", f"${expenses:,.2f}")
col3.metric("Money Left Over", f"${remaining:,.2f}")

# Compare expenses with the budget chosen using the slider.
st.subheader("Budget Comparison")
if expenses > monthly_budget:
    st.warning(f"You are ${expenses - monthly_budget:,.2f} over your budget.")
else:
    st.success(f"You are ${monthly_budget - expenses:,.2f} under your budget.")

# Create a bar chart showing spending by category.
# Expenses are stored as negative numbers, so multiply by -1 for the chart.
st.subheader("📊 Spending by Category")
expense_data = filtered_data[filtered_data["amount"] < 0]
spending_by_category = expense_data.groupby("category")["amount"].sum() * -1

if spending_by_category.empty:
    st.info("No expenses to chart for these filters.")
else:
    st.bar_chart(spending_by_category)

# Show a line chart of spending by date within the selected month.
st.subheader("Daily Spending Trend")
daily_spending = expense_data.groupby("date")["amount"].sum() * -1
if not daily_spending.empty:
    st.line_chart(daily_spending)

# Display the transactions used to make the charts.
st.subheader("Transactions")
st.dataframe(
    filtered_data[["date", "description", "category", "amount"]],
    hide_index=True
)

# Let users download the currently filtered transactions as a CSV.
csv_data = filtered_data.to_csv(index=False)
st.download_button(
    "Download Filtered Transactions",
    data=csv_data,
    file_name="filtered_transactions.csv",
    mime="text/csv",
)

st.caption("Sample transactions are fictional. Do not upload private banking details.")
