# investment_comparison_app.py

import streamlit as st
import numpy as np
import numpy_financial as npf  # Updated import
import seaborn as sns
import matplotlib.pyplot as plt  # Seaborn builds on top of matplotlib

# Set Seaborn style
sns.set_theme(context='notebook', style='darkgrid', palette='pastel', font='sans-serif', font_scale=1, color_codes=True, rc=None)

# Title and description
st.title("Real Estate vs. Stock Market Investment Comparison")
st.write("""
This app allows you to compare potential returns and financial metrics between a real estate investment and a stock market investment based on your input parameters.
""")

# Sidebar inputs
st.sidebar.header("Investment Parameters")

# Real Estate Inputs
st.sidebar.subheader("Real Estate Investment")
purchase_price = st.sidebar.number_input("Property Purchase Price ($)", value=300000, step=10000)
down_payment_percent = st.sidebar.slider("Down Payment (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
annual_interest_rate = st.sidebar.number_input("Mortgage Interest Rate (% per annum)", value=4.0, step=0.1)
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30, step=1)
monthly_rental_income = st.sidebar.number_input("Monthly Rental Income ($)", value=2000, step=100)
operating_expenses_percent = st.sidebar.slider("Operating Expenses (% of Rental Income)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
appreciation_rate = st.sidebar.number_input("Annual Property Appreciation Rate (%)", value=3.0, step=0.1)
closing_costs_percent = st.sidebar.number_input("Closing Costs (% of Purchase Price)", value=5.0, step=0.1)
selling_costs_percent = st.sidebar.number_input("Selling Costs (% of Future Sale Price)", value=6.0, step=0.1)
holding_period_years = st.sidebar.number_input("Holding Period (Years)", value=5, step=1)

# Stock Market Inputs
st.sidebar.subheader("Stock Market Investment")
initial_stock_investment = st.sidebar.number_input("Initial Investment Amount ($)", value=75000, step=1000)
expected_annual_return_rate = st.sidebar.number_input("Expected Annual Return Rate (%)", value=8.0, step=0.1)
std_dev_stocks = st.sidebar.number_input("Standard Deviation of Stock Returns (%)", value=15.0, step=0.1)
inflation_rate = st.sidebar.number_input("Inflation Rate (%)", value=2.0, step=0.1)

# Calculation Functions

def calculate_real_estate_investment():
    # Down payment and loan amount
    down_payment = purchase_price * down_payment_percent / 100
    loan_amount = purchase_price - down_payment

    # Monthly mortgage payment
    monthly_interest_rate = annual_interest_rate / 12 / 100
    number_of_payments = loan_term_years * 12
    M = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments) / \
        ((1 + monthly_interest_rate) ** number_of_payments - 1)
    annual_mortgage_payment = M * 12

    # Rental income and expenses
    annual_rental_income = monthly_rental_income * 12
    operating_expenses = annual_rental_income * operating_expenses_percent / 100
    NOI = annual_rental_income - operating_expenses
    annual_cash_flow = NOI - annual_mortgage_payment

    # Initial investment
    closing_costs = purchase_price * closing_costs_percent / 100
    initial_cash_investment = down_payment + closing_costs

    # Cash on Cash Return
    cash_on_cash_return = (annual_cash_flow / initial_cash_investment) * 100

    # Appreciation and equity gain
    property_value = purchase_price
    mortgage_balance = loan_amount
    equity_list = []
    property_value_list = []
    mortgage_balance_list = []
    annual_cash_flow_list = []
    for year in range(1, holding_period_years + 1):
        property_value *= (1 + appreciation_rate / 100)
        property_value_list.append(property_value)
        # Mortgage balance calculation
        mortgage_balance = mortgage_balance * (1 + monthly_interest_rate) ** 12 - M * 12
        mortgage_balance_list.append(mortgage_balance)
        equity = property_value - mortgage_balance
        equity_list.append(equity)
        annual_cash_flow_list.append(annual_cash_flow)

    # Sale proceeds at the end of holding period
    selling_costs = property_value * selling_costs_percent / 100
    equity_at_sale = property_value - mortgage_balance - selling_costs

    # Cash flows for NPV and IRR calculations
    cash_flows = [-initial_cash_investment] + annual_cash_flow_list[:-1] + [annual_cash_flow_list[-1] + equity_at_sale]

    # NPV and IRR
    discount_rate = expected_annual_return_rate / 100  # Using stock market return as discount rate
    NPV = npf.npv(discount_rate, cash_flows)
    IRR = npf.irr(cash_flows)

    results = {
        'annual_cash_flow': annual_cash_flow,
        'initial_cash_investment': initial_cash_investment,
        'cash_on_cash_return': cash_on_cash_return,
        'equity_at_sale': equity_at_sale,
        'NPV': NPV,
        'IRR': IRR,
        'equity_list': equity_list,
        'property_value_list': property_value_list,
        'mortgage_balance_list': mortgage_balance_list,
        'annual_cash_flow_list': annual_cash_flow_list,
        'cash_flows': cash_flows
    }

    return results

def calculate_stock_investment():
    years = holding_period_years
    portfolio_values = [initial_stock_investment]
    annual_returns = []
    for year in range(1, years + 1):
        annual_return = portfolio_values[-1] * expected_annual_return_rate / 100
        portfolio_values.append(portfolio_values[-1] + annual_return)
        annual_returns.append(annual_return)

    # NPV and IRR
    cash_flows = [-initial_stock_investment] + annual_returns
    discount_rate = expected_annual_return_rate / 100
    NPV = npf.npv(discount_rate, cash_flows)
    IRR = npf.irr(cash_flows)

    results = {
        'portfolio_values': portfolio_values,
        'annual_returns': annual_returns,
        'NPV': NPV,
        'IRR': IRR,
        'cash_flows': cash_flows
    }

    return results

# Perform Calculations
real_estate_results = calculate_real_estate_investment()
stock_results = calculate_stock_investment()

# Display Results

st.header("Investment Results Comparison")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Real Estate Investment")
    st.write(f"**Annual Cash Flow:** ${real_estate_results['annual_cash_flow']:,.2f}")
    st.write(f"**Initial Cash Investment:** ${real_estate_results['initial_cash_investment']:,.2f}")
    st.write(f"**Cash on Cash Return:** {real_estate_results['cash_on_cash_return']:.2f}%")
    st.write(f"**Equity at Sale (Year {holding_period_years}):** ${real_estate_results['equity_at_sale']:,.2f}")
    st.write(f"**Net Present Value (NPV):** ${real_estate_results['NPV']:,.2f}")
    st.write(f"**Internal Rate of Return (IRR):** {real_estate_results['IRR'] * 100:.2f}%")

with col2:
    st.subheader("Stock Market Investment")
    final_portfolio_value = stock_results['portfolio_values'][-1]
    total_return = final_portfolio_value - initial_stock_investment
    st.write(f"**Final Portfolio Value:** ${final_portfolio_value:,.2f}")
    st.write(f"**Total Return:** ${total_return:,.2f}")
    st.write(f"**Net Present Value (NPV):** ${stock_results['NPV']:,.2f}")
    st.write(f"**Internal Rate of Return (IRR):** {stock_results['IRR'] * 100:.2f}%")

# Visualizations

st.header("Investment Performance Over Time")

# Prepare DataFrames for Seaborn
years = np.arange(1, holding_period_years + 1)

import pandas as pd

# Real Estate DataFrame
real_estate_df = pd.DataFrame({
    'Year': years,
    'Property Value': real_estate_results['property_value_list'],
    'Mortgage Balance': real_estate_results['mortgage_balance_list'],
    'Equity': real_estate_results['equity_list'],
    'Annual Cash Flow': real_estate_results['annual_cash_flow_list']
})

# Stock Market DataFrame
stock_df = pd.DataFrame({
    'Year': years,
    'Portfolio Value': stock_results['portfolio_values'][1:],
    'Annual Return': stock_results['annual_returns']
})

# Equity and Property Value Over Time (Real Estate)
st.subheader("Real Estate Investment Over Time")

fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.lineplot(data=real_estate_df, x='Year', y='Property Value', marker='o', label='Property Value', ax=ax1)
sns.lineplot(data=real_estate_df, x='Year', y='Mortgage Balance', marker='o', label='Mortgage Balance', ax=ax1)
sns.lineplot(data=real_estate_df, x='Year', y='Equity', marker='o', label='Equity', ax=ax1)
ax1.set_title('Real Estate Investment Over Time')
ax1.set_ylabel('Amount ($)')
ax1.legend()
st.pyplot(fig1)

# Cash Flows Comparison
st.subheader("Annual Cash Flows Comparison")

combined_cash_flow_df = pd.DataFrame({
    'Year': years,
    'Real Estate Cash Flow': real_estate_results['annual_cash_flow_list'],
    'Stock Market Return': stock_results['annual_returns']
}).melt(id_vars='Year', var_name='Investment Type', value_name='Annual Cash Flow')

fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.barplot(data=combined_cash_flow_df, x='Year', y='Annual Cash Flow', hue='Investment Type', ax=ax2)
ax2.set_title('Annual Cash Flows: Real Estate vs. Stock Market')
st.pyplot(fig2)

# Portfolio Value Over Time (Stock Market)
st.subheader("Stock Market Investment Over Time")

fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.lineplot(data=stock_df, x='Year', y='Portfolio Value', marker='o', color='green', label='Portfolio Value', ax=ax3)
ax3.set_title('Stock Market Investment Over Time')
ax3.set_ylabel('Portfolio Value ($)')
ax3.legend()
st.pyplot(fig3)

# Risk Assessment
st.header("Risk Assessment")

# Coefficient of Variation
std_dev_real_estate = st.number_input("Standard Deviation of Real Estate Returns (%)", value=4.0, step=0.1)
expected_return_real_estate = real_estate_results['IRR'] * 100

CV_real_estate = std_dev_real_estate / expected_return_real_estate
CV_stocks = std_dev_stocks / expected_annual_return_rate

st.write(f"**Real Estate Coefficient of Variation (CV):** {CV_real_estate:.3f}")
st.write(f"**Stock Market Coefficient of Variation (CV):** {CV_stocks:.3f}")

# Inflation-Adjusted Returns
st.header("Inflation-Adjusted Returns")

real_return_real_estate = expected_return_real_estate - inflation_rate
real_return_stocks = expected_annual_return_rate - inflation_rate

st.write(f"**Real Estate Real Return:** {real_return_real_estate:.2f}%")
st.write(f"**Stock Market Real Return:** {real_return_stocks:.2f}%")

# Payback Period
st.header("Payback Period")

payback_period_real_estate = real_estate_results['initial_cash_investment'] / real_estate_results['annual_cash_flow']
annual_return_stock = initial_stock_investment * expected_annual_return_rate / 100
payback_period_stock = initial_stock_investment / annual_return_stock

st.write(f"**Real Estate Payback Period:** {payback_period_real_estate:.2f} years")
st.write(f"**Stock Market Payback Period:** {payback_period_stock:.2f} years")

# Conclusion
st.header("Conclusion")

st.write("""
Based on the input parameters and calculated metrics, you can compare the potential performance of a real estate investment versus a stock market investment over the specified holding period.

- **Real Estate Investment** may offer higher returns through leverage and property appreciation but requires substantial initial capital and ongoing management.
- **Stock Market Investment** provides liquidity and passive income but may be more volatile and offer lower leveraged returns.

Adjust the input parameters to see how changes in market conditions, investment amounts, and other factors impact the investment outcomes.
""")
