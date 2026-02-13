import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="HHI Strategic Decision Engine",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Password Protection
def check_password():
    """Returns `True` if the user has entered the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets.get("password", "HHI2026"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run, show password input
    if "password_correct" not in st.session_state:
        st.text_input(
            "🔐 Enter Client Access Code", type="password", on_change=password_entered, key="password"
        )
        st.info("This tool is password-protected for client use.")
        return False
    # Password incorrect, show error
    elif not st.session_state["password_correct"]:
        st.text_input(
            "🔐 Enter Client Access Code", type="password", on_change=password_entered, key="password"
        )
        st.error("❌ Incorrect password. Please try again.")
        return False
    # Password correct
    else:
        return True

if not check_password():
    st.stop()  # Don't continue if check_password is False

# Custom CSS for professional styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    h1 {
        color: #1f1f1f;
        font-weight: 600;
    }
    h3 {
        color: #4a4a4a;
        font-weight: 500;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🏢 HHI Strategic Decision Engine")
st.markdown("### Commercial Real Estate Decision Analysis")
st.markdown("---")

# Sidebar for inputs
with st.sidebar:
    st.header("HHI Team | Commercial Real Estate")

    # Industrial Mode Toggle
    industrial_mode = st.toggle("🏭 Industrial Mode", value=False,
                                help="Switch to industrial/warehouse analysis with machinery costs and operational downtime")

    st.subheader("Property Details")
    current_sf = st.number_input("Current Square Footage (Stay)", min_value=1000, value=20000, step=1000,
                                  help="Current space size for renewal scenario")
    target_sf = st.number_input("Target Square Footage (Go)", min_value=1000, value=20000, step=1000,
                                 help="Proposed space size for relocation scenario")

    st.subheader("Financial Parameters")
    escalation_rate = st.slider("Annual Rent Escalation (%)", min_value=0.0, max_value=5.0, value=3.0, step=0.25)
    discount_rate = st.slider("Discount Rate (%) for NPV", min_value=0.0, max_value=15.0, value=7.0, step=0.5,
                               help="Used to calculate present value of future cash flows")

    st.markdown("---")
    st.subheader("📍 Scenario A: Stay (Renewal)")
    renewal_base_rent = st.number_input("Renewal Base Rent ($/PSF)", min_value=0.0, value=35.0, step=0.50)
    renewal_free_rent = st.number_input("Renewal Free Rent (Months)", min_value=0, max_value=24, value=2)
    renewal_ti = st.number_input("Renewal TI Allowance ($/PSF)", min_value=0.0, value=5.0, step=1.0)

    st.markdown("---")
    st.subheader("🚀 Scenario B: Go (Relocate)")
    new_base_rent = st.number_input("New Base Rent ($/PSF)", min_value=0.0, value=30.0, step=0.50)
    new_free_rent = st.number_input("New Free Rent (Months)", min_value=0, max_value=24, value=6)
    new_ti = st.number_input("New TI Allowance ($/PSF)", min_value=0.0, value=60.0, step=1.0)
    moving_costs_psf = st.number_input("Moving/FF&E Costs ($/PSF)", min_value=0.0, value=25.0, step=1.0)

    st.markdown("---")

    # Conditional inputs based on mode
    if not industrial_mode:
        st.subheader("⚡ HHI Team Friction (Office)")
        productivity_loss_hours = st.slider("Productivity Loss per Employee (Hours)",
                                            min_value=0, max_value=80, value=8, step=1)
        headcount = st.number_input("Headcount", min_value=1, value=50, step=1)
        avg_salary = st.number_input("Average Salary ($)", min_value=0, value=150000, step=5000)
    else:
        st.subheader("🏭 HHI Team Friction (Industrial)")
        daily_revenue_loss = st.number_input("Daily Revenue/Production Value ($)",
                                             min_value=0, value=50000, step=5000,
                                             help="Average daily revenue or production value")
        machinery_rigging = st.number_input("Machinery Rigging & Electrical ($/SF)",
                                           min_value=0.0, value=15.0, step=1.0,
                                           help="One-time capital expense for moving machinery and electrical infrastructure")
        headcount = st.number_input("Headcount", min_value=1, value=50, step=1)
        avg_salary = st.number_input("Average Salary ($)", min_value=0, value=150000, step=5000)

    # HHI Team Strategic Drivers Section
    st.markdown("---")
    with st.expander("🎯 HHI Team Strategic Drivers", expanded=False):
        st.markdown("**Quantify the strategic impact of your real estate decision**")
        st.markdown("---")

        # Driver A: Workforce Stability Index
        st.markdown("**Driver A: Workforce Stability Index**")
        st.caption("The risk of losing talent in an inferior workplace")
        attrition_rate = st.slider("Projected Turnover Risk - Status Quo (%)",
                                   min_value=0.0, max_value=15.0, value=5.0, step=0.5,
                                   help="Estimated annual attrition rate in current/inferior space")

        st.markdown("---")

        # Driver B: Recruiting Velocity
        st.markdown("**Driver B: Recruiting Velocity**")
        st.caption("Revenue gained by filling roles faster in a premium asset")
        hiring_speed_boost = st.slider("Hiring Speed Boost (Days Saved)",
                                       min_value=0, max_value=30, value=15, step=1,
                                       help="Days saved in time-to-hire in better space")
        open_roles_per_year = st.number_input("Open Roles Per Year",
                                              min_value=0, value=10, step=1)
        revenue_per_employee = st.number_input("Revenue Per Employee ($)",
                                               min_value=0, value=500000, step=10000)

        st.markdown("---")

        # Driver C: Commute Dividend
        st.markdown("**Driver C: The Commute Dividend**")
        st.caption("The 'virtual raise' employees receive by recapturing time")
        commute_time_saved = st.slider("Commute Time Recaptured (Mins/Day)",
                                       min_value=0, max_value=60, value=20, step=5,
                                       help="Average daily commute time saved per employee")
        st.caption("💡 *Hourly wage calculated from average salary ÷ 2,080 hours/year*")

# Calculate Strategic Driver Values
def calculate_strategic_drivers():
    """Calculate the three HHI Strategic Drivers"""

    # Driver A: Workforce Stability Index (Turnover Risk)
    # One-time cost of losing talent in inferior space
    turnover_risk = headcount * (attrition_rate / 100) * avg_salary * 1.5

    # Driver B: Recruiting Velocity (Hiring Speed Benefit)
    # Annual benefit of filling roles faster
    recruiting_benefit = open_roles_per_year * (revenue_per_employee / 250) * hiring_speed_boost

    # Driver C: Commute Dividend (Time Value)
    # Annual benefit of time savings
    hourly_wage = avg_salary / 2080
    commute_benefit = headcount * commute_time_saved * 250 / 60 * hourly_wage

    return turnover_risk, recruiting_benefit, commute_benefit

# Calculate Net Effective Rent
def calculate_ner(base_rent, free_months, ti_allowance, sq_ft, term_years=10):
    """
    Calculate Net Effective Rent over the lease term.
    NER = (Total Rent - Free Rent - TI Allowance) / Total Months
    """
    total_months = term_years * 12

    # Calculate total base rent over term (with escalation)
    total_rent = 0
    current_rent = base_rent
    for year in range(term_years):
        total_rent += current_rent * 12 * sq_ft
        current_rent *= (1 + escalation_rate / 100)

    # Adjust for free rent months
    free_rent_value = base_rent * free_months * sq_ft

    # TI allowance is amortized over term
    ti_benefit = ti_allowance * sq_ft * term_years

    # Calculate NER per month
    net_effective = (total_rent - free_rent_value - ti_benefit) / total_months

    return net_effective

# Calculate year-over-year costs
def calculate_annual_costs(base_rent, free_months, ti_allowance, sq_ft, term_years=10):
    """Calculate annual occupancy costs with escalation."""
    annual_costs = []
    current_rent = base_rent

    # Calculate TI benefit per year (amortized)
    ti_per_year = ti_allowance

    for year in range(1, term_years + 1):
        if year == 1:
            # Year 1: Account for free rent
            effective_months = 12 - free_months
            year_cost = (current_rent * effective_months * sq_ft) - (ti_per_year * sq_ft)
        else:
            year_cost = current_rent * 12 * sq_ft - (ti_per_year * sq_ft)

        annual_costs.append(max(0, year_cost))
        current_rent *= (1 + escalation_rate / 100)

    return annual_costs

# Calculate HHI Team friction cost
def calculate_friction_cost():
    """Calculate one-time friction/moving penalty."""
    if not industrial_mode:
        # Office mode: Productivity loss
        hourly_cost = avg_salary / 2080
        friction = headcount * hourly_cost * productivity_loss_hours
    else:
        # Industrial mode: 2 weeks operational downtime + machinery costs
        downtime_cost = daily_revenue_loss * 14
        rigging_cost = machinery_rigging * target_sf
        friction = downtime_cost + rigging_cost

    return friction

# Calculate NPV
def calculate_npv(cash_flows, discount_rate):
    """Calculate Net Present Value of cash flows"""
    npv = 0
    for year, cf in enumerate(cash_flows, start=1):
        npv += cf / ((1 + discount_rate / 100) ** year)
    return npv

# Perform calculations
turnover_risk, recruiting_benefit, commute_benefit = calculate_strategic_drivers()

# Calculate base costs
renewal_costs = calculate_annual_costs(renewal_base_rent, renewal_free_rent, renewal_ti, current_sf)
relocation_costs = calculate_annual_costs(new_base_rent, new_free_rent, new_ti, target_sf)

# Apply Strategic Drivers to scenarios
# Stay scenario: Add turnover risk (one-time) + opportunity cost from poor recruiting/commute (annual)
opportunity_cost_annual = recruiting_benefit + commute_benefit
renewal_costs[0] += turnover_risk  # Add one-time turnover risk to Year 1
for i in range(len(renewal_costs)):
    renewal_costs[i] += opportunity_cost_annual  # Add annual opportunity cost

# Go scenario: Add friction cost + moving costs (one-time Year 1) - recruiting/commute benefits (annual)
friction_cost = calculate_friction_cost()
moving_cost = moving_costs_psf * target_sf
total_relocation_penalty = friction_cost + moving_cost + turnover_risk  # One-time costs including turnover
relocation_costs[0] += total_relocation_penalty

# Subtract strategic benefits from Go scenario (annual)
for i in range(len(relocation_costs)):
    relocation_costs[i] -= (recruiting_benefit + commute_benefit)

# Ensure no negative costs
renewal_costs = [max(0, c) for c in renewal_costs]
relocation_costs = [max(0, c) for c in relocation_costs]

# Calculate cumulative costs
renewal_cumulative = np.cumsum(renewal_costs)
relocation_cumulative = np.cumsum(relocation_costs)

# Calculate NPV
renewal_npv = calculate_npv(renewal_costs, discount_rate)
relocation_npv = calculate_npv(relocation_costs, discount_rate)

# Calculate annuities
renewal_annuity = renewal_cumulative[-1] / 10
relocation_annuity = relocation_cumulative[-1] / 10

# Find breakeven point
breakeven_month = None
for year in range(10):
    if relocation_cumulative[year] < renewal_cumulative[year]:
        # Interpolate to find the month
        if year == 0:
            breakeven_month = None
        else:
            if renewal_costs[year] != relocation_costs[year]:
                months_into_year = 12 * (renewal_cumulative[year-1] - relocation_cumulative[year-1]) / (renewal_costs[year] - relocation_costs[year])
                breakeven_month = year * 12 + months_into_year
        break

# Calculate total savings
total_10yr_savings = renewal_cumulative[-1] - relocation_cumulative[-1]
npv_savings = renewal_npv - relocation_npv

# Executive Summary - Key Insights (Option C)
st.subheader("💡 Executive Summary")
col1, col2, col3 = st.columns(3)

with col1:
    upfront_investment = friction_cost + moving_cost + max(0, relocation_costs[0] - renewal_costs[0])
    st.metric(
        label="Upfront Investment Required",
        value=f"${upfront_investment:,.0f}",
        help="Total one-time costs: Moving + Friction + Year 1 net cash"
    )

with col2:
    if breakeven_month:
        years = int(breakeven_month // 12)
        months = int(breakeven_month % 12)
        breakeven_display = f"{years}yr {months}mo"
    else:
        breakeven_display = "Never" if total_10yr_savings < 0 else "Immediate"

    st.metric(
        label="Breakeven Point",
        value=breakeven_display,
        help="When relocation becomes cheaper than staying"
    )

with col3:
    st.metric(
        label="NPV of Decision",
        value=f"${npv_savings:,.0f}",
        delta=f"Discount Rate: {discount_rate}%",
        help=f"Present value of 10-year savings at {discount_rate}% discount rate"
    )

st.markdown("---")

# Executive Summary - Waterfall Chart
st.subheader("📊 Strategic Impact Analysis (Annual Annuity)")

# Calculate components for waterfall
base_rent_savings_annual = (renewal_base_rent * current_sf * 12) - (new_base_rent * target_sf * 12)
moving_costs_annual = (moving_cost + friction_cost) / 10  # Amortize over 10 years
strategic_value_annual = (recruiting_benefit + commute_benefit - (turnover_risk / 10))  # Net strategic value

# Create waterfall chart
fig_waterfall = go.Figure(go.Waterfall(
    name="Strategic Impact",
    orientation="v",
    measure=["relative", "relative", "relative", "total"],
    x=["Base Rent\nSavings", "Moving &\nFriction Costs", "Strategic\nValue", "Net Annual\nBenefit"],
    y=[base_rent_savings_annual, -moving_costs_annual, strategic_value_annual,
       base_rent_savings_annual - moving_costs_annual + strategic_value_annual],
    text=[f"${base_rent_savings_annual:,.0f}", f"-${moving_costs_annual:,.0f}",
          f"${strategic_value_annual:,.0f}",
          f"${(base_rent_savings_annual - moving_costs_annual + strategic_value_annual):,.0f}"],
    textposition="outside",
    connector={"line": {"color": "rgb(63, 63, 63)"}},
    decreasing={"marker": {"color": "#d62728"}},
    increasing={"marker": {"color": "#2ca02c"}},
    totals={"marker": {"color": "#1f77b4"}}
))

fig_waterfall.update_layout(
    title="Annual Cost/Benefit Breakdown (Annualized over 10 years)",
    yaxis_title="Annual Impact ($)",
    height=500,
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white'
)

st.plotly_chart(fig_waterfall, use_container_width=True)

st.markdown("---")

# Visualization 1: Cumulative Cost Over Time
st.subheader("📈 Cumulative Occupancy Cost (10-Year Projection)")

years = list(range(1, 11))
fig_cumulative = go.Figure()

# Stay line
fig_cumulative.add_trace(go.Scatter(
    x=years,
    y=renewal_cumulative,
    name="Stay (Renewal)",
    mode='lines+markers',
    line=dict(color='#1f77b4', width=3),
    marker=dict(size=8)
))

# Go line
fig_cumulative.add_trace(go.Scatter(
    x=years,
    y=relocation_cumulative,
    name="Go (Relocate)",
    mode='lines+markers',
    line=dict(color='#ff7f0e', width=3),
    marker=dict(size=8)
))

# Add breakeven marker
if breakeven_month and breakeven_month <= 120:
    breakeven_year = breakeven_month / 12
    breakeven_cost = np.interp(breakeven_year, years, renewal_cumulative)
    fig_cumulative.add_trace(go.Scatter(
        x=[breakeven_year],
        y=[breakeven_cost],
        mode='markers+text',
        name='Breakeven',
        marker=dict(size=15, color='green', symbol='star'),
        text=['Breakeven'],
        textposition='top center',
        textfont=dict(size=12, color='green')
    ))

fig_cumulative.update_layout(
    xaxis_title="Year",
    yaxis_title="Cumulative Cost ($)",
    hovermode='x unified',
    height=500,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(size=12),
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

fig_cumulative.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e5e5e5')
fig_cumulative.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e5e5')

st.plotly_chart(fig_cumulative, use_container_width=True)

st.markdown("---")

# Visualization 2: Year 1 Cash Outflow Breakdown
st.subheader("💵 Year 1 Cash Outflow Breakdown")

# Calculate Year 1 components
renewal_year1_base = renewal_base_rent * current_sf * (12 - renewal_free_rent)
renewal_year1_ti_benefit = renewal_ti * current_sf

relocation_year1_base = new_base_rent * target_sf * (12 - new_free_rent)
relocation_year1_ti_benefit = new_ti * target_sf
relocation_year1_moving = moving_cost
relocation_year1_friction = friction_cost

# Create stacked bar chart data
fig_year1 = go.Figure()

# Stay scenario
fig_year1.add_trace(go.Bar(
    name='Base Rent',
    x=['Stay (Renewal)', 'Go (Relocate)'],
    y=[renewal_year1_base, relocation_year1_base],
    marker_color='#1f77b4',
    text=[f'${renewal_year1_base:,.0f}', f'${relocation_year1_base:,.0f}'],
    textposition='inside'
))

fig_year1.add_trace(go.Bar(
    name='Moving/FF&E',
    x=['Stay (Renewal)', 'Go (Relocate)'],
    y=[0, relocation_year1_moving],
    marker_color='#ff7f0e',
    text=['', f'${relocation_year1_moving:,.0f}'],
    textposition='inside'
))

fig_year1.add_trace(go.Bar(
    name='HHI Team Friction',
    x=['Stay (Renewal)', 'Go (Relocate)'],
    y=[0, relocation_year1_friction],
    marker_color='#d62728',
    text=['', f'${relocation_year1_friction:,.0f}'],
    textposition='inside'
))

fig_year1.add_trace(go.Bar(
    name='TI Allowance (Benefit)',
    x=['Stay (Renewal)', 'Go (Relocate)'],
    y=[-renewal_year1_ti_benefit, -relocation_year1_ti_benefit],
    marker_color='#2ca02c',
    text=[f'-${renewal_year1_ti_benefit:,.0f}', f'-${relocation_year1_ti_benefit:,.0f}'],
    textposition='inside'
))

fig_year1.update_layout(
    barmode='relative',
    xaxis_title="Scenario",
    yaxis_title="Year 1 Cash Outflow ($)",
    height=500,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(size=12),
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

fig_year1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e5e5')

st.plotly_chart(fig_year1, use_container_width=True)

st.markdown("---")

# HHI Strategic Drivers Summary
st.subheader("🎯 HHI Strategic Drivers Summary")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Talent Replacement Liability",
        value=f"${turnover_risk:,.0f}",
        help="One-time cost of turnover risk (Headcount × Attrition × Salary × 1.5x)"
    )

with col2:
    st.metric(
        label="Recruiting Efficiency Gain (Annual)",
        value=f"${recruiting_benefit:,.0f}",
        help="Annual benefit from faster hiring in premium space"
    )

with col3:
    st.metric(
        label="Employee Time Value Recaptured (Annual)",
        value=f"${commute_benefit:,.0f}",
        help="Annual value of time saved from improved commute"
    )

st.markdown("---")

# Summary table
st.subheader("📋 Detailed Year-by-Year Comparison")

df_comparison = pd.DataFrame({
    'Year': years,
    'Stay - Annual Cost': [f'${x:,.0f}' for x in renewal_costs],
    'Stay - Cumulative': [f'${x:,.0f}' for x in renewal_cumulative],
    'Go - Annual Cost': [f'${x:,.0f}' for x in relocation_costs],
    'Go - Cumulative': [f'${x:,.0f}' for x in relocation_cumulative],
    'Annual Difference': [f'${(relocation_costs[i] - renewal_costs[i]):,.0f}' for i in range(10)]
})

st.dataframe(df_comparison, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>HHI Strategic Decision Engine</strong> | Commercial Real Estate Intelligence</p>
    <p style='font-size: 0.9em;'>The HHI methodology quantifies strategic value beyond traditional occupancy cost analysis.</p>
</div>
""", unsafe_allow_html=True)