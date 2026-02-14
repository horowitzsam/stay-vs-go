import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Password protection
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 HHI Strategic Decision Engine")
    st.markdown("### Access Required")
    password_input = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        if password_input == st.secrets.get("password", "HHI2026"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="HHI Strategic Decision Engine",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
</style>
""", unsafe_allow_html=True)

# Title
st.title("🏢 HHI Strategic Decision Engine")
st.markdown("### Commercial Real Estate Decision Analysis")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("HHI Team | Commercial Real Estate")
    st.markdown("---")

    # Industrial Mode Toggle
    industrial_mode = st.toggle("🏭 Industrial Mode", value=False,
                                help="Switch to industrial/warehouse analysis with machinery costs and operational downtime")

    st.markdown("---")
    st.subheader("⚙️ Lease Parameters")
    lease_term = st.number_input("Lease Term (Years)", min_value=1, max_value=20, value=10, step=1,
                                 help="Length of the lease term for analysis")
    discount_rate = st.slider("Discount Rate (%)", min_value=0.0, max_value=15.0, value=7.0, step=0.5,
                              help="Cost of capital for NPV calculation")
    escalation_rate = st.slider("Annual Rent Escalation (%)", min_value=0.0, max_value=5.0, value=3.0, step=0.25)

    st.markdown("---")
    st.subheader("📏 Space Requirements")
    current_sf = st.number_input("Current Square Footage (Stay Scenario)", min_value=1000, value=20000, step=1000)
    target_sf = st.number_input("Target Square Footage (Go Scenario)", min_value=1000, value=20000, step=1000,
                                help="Square footage for relocation (can be different for expansion/contraction)")

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
                                           min_value=0, max_value=80, value=0, step=1)
        headcount = st.number_input("Headcount", min_value=1, value=1, step=1)
        avg_salary = st.number_input("Average Salary ($)", min_value=0, value=0, step=5000)
    else:
        st.subheader("🏭 HHI Team Friction (Industrial)")
        daily_revenue_loss = st.number_input("Daily Revenue/Production Value ($)",
                                             min_value=0, value=0, step=5000,
                                             help="Average daily revenue or production value")
        machinery_rigging = st.number_input("Machinery Rigging & Electrical ($/SF)",
                                           min_value=0.0, value=0.0, step=1.0,
                                           help="One-time capital expense for moving machinery and electrical infrastructure")

    st.markdown("---")

    # Strategic Drivers (Office Mode Only)
    if not industrial_mode:
        with st.expander("🎯 HHI Team Strategic Drivers", expanded=False):
            st.markdown("**Driver A: Workforce Stability Index**")
            st.markdown("_One-time turnover risk from relocation_")
            attrition_rate = st.slider("Estimated Attrition Rate (%)", min_value=0.0, max_value=50.0, value=10.0, step=1.0)

            st.markdown("**Driver B: Recruiting Velocity**")
            st.markdown("_Annual benefit from improved hiring speed_")
            open_roles_per_year = st.number_input("Open Roles Per Year", min_value=0, value=5, step=1)
            revenue_per_employee = st.number_input("Revenue Per Employee ($)", min_value=0, value=500000, step=10000)
            hiring_speed_boost = st.slider("Hiring Speed Boost (Days Faster)", min_value=0, max_value=90, value=30, step=5)

            st.markdown("**Driver C: Commute Dividend**")
            st.markdown("_Annual value of recaptured commute time_")
            commute_time_saved = st.slider("Avg Commute Time Saved (Minutes/Day)", min_value=0, max_value=120, value=20, step=5)
            st.caption("💡 Hourly wage calculated as: Annual Salary ÷ 2,080 hours")

# Calculate Strategic Drivers
def calculate_strategic_drivers():
    """Calculate the three HHI Strategic Drivers"""
    # Driver A: Workforce Stability Index (one-time cost)
    turnover_risk = headcount * (attrition_rate / 100) * avg_salary * 1.5

    # Driver B: Recruiting Velocity (annual benefit)
    days_revenue_per_role = revenue_per_employee / 250
    recruiting_benefit = open_roles_per_year * days_revenue_per_role * hiring_speed_boost

    # Driver C: Commute Dividend (annual benefit)
    hourly_wage = avg_salary / 2080
    annual_work_days = 250
    commute_benefit = headcount * (commute_time_saved / 60) * annual_work_days * hourly_wage

    return turnover_risk, recruiting_benefit, commute_benefit

# Calculate friction cost
def calculate_friction_cost():
    """Calculate one-time HHI Team Friction penalty"""
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

# Calculate annual costs
def calculate_annual_costs(base_rent, free_months, ti_allowance, sq_ft, term_years):
    """Calculate annual occupancy costs with escalation"""
    annual_costs = []
    current_rent = base_rent
    ti_per_year = ti_allowance

    for year in range(1, term_years + 1):
        if year == 1:
            effective_months = 12 - free_months
            year_cost = (current_rent * effective_months * sq_ft) - (ti_per_year * sq_ft)
        else:
            year_cost = current_rent * 12 * sq_ft - (ti_per_year * sq_ft)

        annual_costs.append(max(0, year_cost))
        current_rent *= (1 + escalation_rate / 100)

    return annual_costs

# Calculate NPV
def calculate_npv(cash_flows, discount_rate):
    """Calculate Net Present Value of cash flows"""
    npv = 0
    for year, cf in enumerate(cash_flows, start=1):
        npv += cf / ((1 + discount_rate / 100) ** year)
    return npv

# Perform calculations
if not industrial_mode:
    turnover_risk, recruiting_benefit, commute_benefit = calculate_strategic_drivers()
else:
    # Industrial mode: No strategic drivers
    turnover_risk, recruiting_benefit, commute_benefit = 0, 0, 0

# Base costs
renewal_costs = calculate_annual_costs(renewal_base_rent, renewal_free_rent, renewal_ti, current_sf, lease_term)
relocation_costs = calculate_annual_costs(new_base_rent, new_free_rent, new_ti, target_sf, lease_term)

# Apply Strategic Drivers to Stay scenario
# Stay: Gets turnover risk (one-time Year 1) + opportunity cost from poor recruiting/commute (annual)
opportunity_cost_annual = recruiting_benefit + commute_benefit
renewal_costs[0] += turnover_risk
for i in range(len(renewal_costs)):
    renewal_costs[i] += opportunity_cost_annual

# Apply Strategic Drivers and friction to Go scenario
friction_cost = calculate_friction_cost()
moving_cost = moving_costs_psf * target_sf
total_relocation_penalty = friction_cost + moving_cost + turnover_risk

relocation_costs[0] += total_relocation_penalty
for i in range(len(relocation_costs)):
    relocation_costs[i] -= (recruiting_benefit + commute_benefit)

# Calculate NPV for both scenarios
renewal_npv = calculate_npv(renewal_costs, discount_rate)
relocation_npv = calculate_npv(relocation_costs, discount_rate)
npv_savings = renewal_npv - relocation_npv

# Cumulative costs
renewal_cumulative = np.cumsum(renewal_costs)
relocation_cumulative = np.cumsum(relocation_costs)

# Breakeven - Fixed Logic
breakeven_month = None
for year in range(lease_term):
    if relocation_cumulative[year] < renewal_cumulative[year]:
        # Found the year where Go becomes cheaper than Stay
        if year == 0:
            # Go is cheaper immediately
            breakeven_month = 0
        else:
            # Interpolate to find the exact month within the year
            # At end of year-1: Go was more expensive
            # At end of year: Go is less expensive
            # Find the crossover point
            gap_at_start = renewal_cumulative[year-1] - relocation_cumulative[year-1]  # Negative (Go is losing)
            gap_at_end = renewal_cumulative[year] - relocation_cumulative[year]  # Positive (Go is winning)

            # How much did Go gain during this year?
            go_gain = renewal_costs[year] - relocation_costs[year]

            if go_gain > 0:
                # Calculate what fraction of the year it took to close the gap
                fraction_of_year = abs(gap_at_start) / go_gain
                breakeven_month = (year - 1) * 12 + (fraction_of_year * 12)
            else:
                breakeven_month = year * 12
        break

# If we never found a breakeven, check if Go ever becomes cheaper
if breakeven_month is None and relocation_cumulative[-1] >= renewal_cumulative[-1]:
    # Go never becomes cheaper
    breakeven_display = "Does Not Breakeven"
else:
    if breakeven_month is None:
        breakeven_display = "Does Not Breakeven"

# Key Insights - Option C
st.subheader("💡 Executive Summary")
col1, col2, col3 = st.columns(3)

with col1:
    upfront_investment = friction_cost + moving_cost + max(0, relocation_costs[0] - renewal_costs[0])
    st.metric(
        label="Upfront Investment Required",
        value=f"${upfront_investment:,.0f}",
        help="Initial cash outlay for relocation (friction + moving + Year 1 delta)"
    )

with col2:
    if breakeven_month is not None and breakeven_display != "Does Not Breakeven":
        if breakeven_month == 0:
            breakeven_display = "Immediate"
        else:
            years = int(breakeven_month // 12)
            months = int(breakeven_month % 12)
            breakeven_display = f"{years}yr {months}mo"

    st.metric(
        label="Breakeven Point",
        value=breakeven_display,
        help="When cumulative relocation costs equal cumulative renewal costs"
    )

with col3:
    st.metric(
        label=f"NPV of Decision ({lease_term}yr)",
        value=f"${npv_savings:,.0f}",
        delta=f"{'Savings' if npv_savings > 0 else 'Premium'}",
        delta_color="normal" if npv_savings > 0 else "inverse",
        help=f"Net Present Value at {discount_rate}% discount rate"
    )

st.markdown("---")

# Waterfall Chart - Annual Annuity (Fixed to show true average annual costs)
st.subheader("💰 Executive Summary: Annual Annuity Waterfall")

# Calculate average annual costs (already includes all strategic drivers and costs)
avg_stay_cost = sum(renewal_costs) / lease_term
avg_go_cost = sum(relocation_costs) / lease_term

# Calculate average annual base rent for each scenario (with escalation)
stay_base_rent_total = 0
go_base_rent_total = 0
for year in range(lease_term):
    # Stay scenario base rent with escalation
    stay_rent_this_year = renewal_base_rent * current_sf * 12 * ((1 + escalation_rate/100) ** year)
    stay_base_rent_total += stay_rent_this_year

    # Go scenario base rent with escalation
    go_rent_this_year = new_base_rent * target_sf * 12 * ((1 + escalation_rate/100) ** year)
    go_base_rent_total += go_rent_this_year

avg_stay_base_rent = stay_base_rent_total / lease_term
avg_go_base_rent = go_base_rent_total / lease_term
avg_rent_savings = avg_stay_base_rent - avg_go_base_rent

# Calculate average annual TI benefit
avg_ti_stay = renewal_ti * current_sf
avg_ti_go = new_ti * target_sf
avg_ti_benefit = avg_ti_go - avg_ti_stay

waterfall_values = [
    avg_stay_cost,
    -avg_rent_savings,  # Rent savings (annual average with escalation)
    -avg_ti_benefit,    # Additional TI benefit (annual average)
    -recruiting_benefit,  # Recruiting velocity (annual)
    -commute_benefit,     # Commute dividend (annual)
    (friction_cost + moving_cost + turnover_risk) / lease_term,  # Amortized one-time costs
    opportunity_cost_annual,  # Opportunity cost (annual)
    avg_go_cost
]

waterfall_labels = [
    "Stay Cost",
    "Rent Savings",
    "TI Benefit",
    "Recruiting Velocity",
    "Commute Dividend",
    "Amortized Friction",
    "Opportunity Cost",
    "Go Cost"
]

waterfall_text = [f"${v:,.0f}" for v in waterfall_values]

fig_waterfall = go.Figure(go.Waterfall(
    x=waterfall_labels,
    y=waterfall_values,
    text=waterfall_text,
    textposition="outside",
    connector={"line": {"color": "rgb(63, 63, 63)"}},
    decreasing={"marker": {"color": "#2ca02c"}},
    increasing={"marker": {"color": "#d62728"}},
    totals={"marker": {"color": "#1f77b4"}}
))

fig_waterfall.update_layout(
    title=f"Average Annual Cost Breakdown ({lease_term}-Year Annuity)",
    yaxis_title="Annual Cost ($)",
    height=500,
    showlegend=False
)

st.plotly_chart(fig_waterfall, use_container_width=True)

st.markdown("---")

# Cumulative Cost Chart
st.subheader(f"📈 Cumulative Occupancy Cost ({lease_term}-Year Projection)")

years = list(range(1, lease_term + 1))
fig_cumulative = go.Figure()

fig_cumulative.add_trace(go.Scatter(
    x=years,
    y=renewal_cumulative,
    name="Stay (Renewal)",
    mode='lines+markers',
    line=dict(color='#1f77b4', width=3),
    marker=dict(size=8)
))

fig_cumulative.add_trace(go.Scatter(
    x=years,
    y=relocation_cumulative,
    name="Go (Relocate)",
    mode='lines+markers',
    line=dict(color='#ff7f0e', width=3),
    marker=dict(size=8)
))

if breakeven_month and breakeven_month <= (lease_term * 12):
    breakeven_year = breakeven_month / 12
    breakeven_cost = np.interp(breakeven_year, years, renewal_cumulative)
    fig_cumulative.add_trace(go.Scatter(
        x=[breakeven_year],
        y=[breakeven_cost],
        mode='markers+text',
        name='Breakeven',
        marker=dict(size=15, color='green', symbol='star'),
        text=['Breakeven'],
        textposition='top center'
    ))

fig_cumulative.update_layout(
    xaxis_title="Year",
    yaxis_title="Cumulative Cost ($)",
    hovermode='x unified',
    height=500,
    showlegend=True
)

fig_cumulative.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e5e5e5')
fig_cumulative.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e5e5')

st.plotly_chart(fig_cumulative, use_container_width=True)

st.markdown("---")

# Year 1 Breakdown
st.subheader("💵 Year 1 Cash Outflow Breakdown")

renewal_year1_base = renewal_base_rent * current_sf * (12 - renewal_free_rent)
renewal_year1_ti = renewal_ti * current_sf
renewal_year1_strategic = turnover_risk + opportunity_cost_annual

relocation_year1_base = new_base_rent * target_sf * (12 - new_free_rent)
relocation_year1_ti = new_ti * target_sf
relocation_year1_moving = moving_cost
relocation_year1_friction = friction_cost
relocation_year1_turnover = turnover_risk
relocation_year1_benefits = recruiting_benefit + commute_benefit

fig_year1 = go.Figure()

fig_year1.add_trace(go.Bar(
    name='Base Rent',
    x=['Stay (Renewal)', 'Go (Relocate)'],
    y=[renewal_year1_base, relocation_year1_base],
    marker_color='#1f77b4'
))

fig_year1.add_trace(go.Bar(
    name='Moving/FF&E',
    x=['Stay (Renewal)', 'Go (Relocate)'],
    y=[0, relocation_year1_moving],
    marker_color='#ff7f0e'
))

fig_year1.add_trace(go.Bar(
    name='Friction + Turnover',
    x=['Stay (Renewal)', 'Go (Relocate)'],
    y=[turnover_risk, relocation_year1_friction + relocation_year1_turnover],
    marker_color='#d62728'
))

fig_year1.add_trace(go.Bar(
    name='Opportunity Cost',
    x=['Stay (Renewal)', 'Go (Relocate)'],
    y=[opportunity_cost_annual, 0],
    marker_color='#9467bd'
))

fig_year1.add_trace(go.Bar(
    name='TI Allowance (Benefit)',
    x=['Stay (Renewal)', 'Go (Relocate)'],
    y=[-renewal_year1_ti, -relocation_year1_ti],
    marker_color='#2ca02c'
))

fig_year1.add_trace(go.Bar(
    name='Strategic Benefits',
    x=['Stay (Renewal)', 'Go (Relocate)'],
    y=[0, -relocation_year1_benefits],
    marker_color='#17becf'
))

fig_year1.update_layout(
    barmode='relative',
    xaxis_title="Scenario",
    yaxis_title="Year 1 Cash Outflow ($)",
    height=500,
    showlegend=True
)

fig_year1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e5e5')

st.plotly_chart(fig_year1, use_container_width=True)

st.markdown("---")

# Detailed Table
st.subheader(f"📋 Detailed Year-by-Year Comparison ({lease_term} Years)")

df_comparison = pd.DataFrame({
    'Year': years,
    'Stay - Annual': [f'${x:,.0f}' for x in renewal_costs],
    'Stay - Cumulative': [f'${x:,.0f}' for x in renewal_cumulative],
    'Go - Annual': [f'${x:,.0f}' for x in relocation_costs],
    'Go - Cumulative': [f'${x:,.0f}' for x in relocation_cumulative],
    'Annual Δ': [f'${(relocation_costs[i] - renewal_costs[i]):,.0f}' for i in range(lease_term)]
})

st.dataframe(df_comparison, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>HHI Strategic Decision Engine</strong> | Commercial Real Estate Decision Intelligence</p>
    <p style='font-size: 0.9em;'>Quantifying the strategic and operational impact of real estate decisions</p>
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 1rem; font-size: 0.85em; max-width: 800px; margin: 0 auto;'>
    <p><strong>⚠️ Disclaimer</strong></p>
    <p style='line-height: 1.6;'>
    This tool is provided for informational and analytical purposes only. The projections, calculations, and insights
    generated are based on user-provided inputs and assumptions, and should be used as guidance in the decision-making
    process. This analysis does not constitute professional real estate, financial, legal, or tax advice.
    Users should consult with qualified professionals and conduct their own due diligence before making any
    real estate decisions. HHI and the tool creators assume no liability for decisions made based on this analysis.
    </p>
</div>
""", unsafe_allow_html=True)