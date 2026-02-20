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
        st.subheader("⚡ HHI Team Friction (Office)",
                    help="Quantifies the hidden cost of business disruption. Moving requires packing, IT downtime, and employee acclimation, which temporarily reduces billable hours or overall productivity.")
        productivity_loss_hours = st.slider("Productivity Loss per Employee (Hours)",
                                           min_value=0, max_value=80, value=0, step=1)
        headcount = st.number_input("Headcount", min_value=1, value=1, step=1)
        avg_salary = st.number_input("Average Salary ($)", min_value=0, value=0, step=5000)
    else:
        st.subheader("🏭 HHI Team Friction (Industrial)",
                    help="Accounts for the hard operational downtime and the specialized capital expense of rigging and moving heavy machinery.")
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
            attrition_rate = st.slider("Estimated Attrition Rate (%)", min_value=0.0, max_value=50.0, value=0.0, step=1.0,
                                      help="The percentage of staff likely to resign due to the disruption of moving or a worsened commute.")

            st.markdown("**Driver B: Recruiting Velocity**")
            st.markdown("_Annual benefit from improved hiring speed_")
            open_roles_per_year = st.number_input("Open Roles Per Year", min_value=0, value=0, step=1)
            revenue_per_employee = st.number_input("Revenue Per Employee ($)", min_value=0, value=0, step=10000)
            hiring_speed_boost = st.slider("Hiring Speed Boost (Days Faster)", min_value=0, max_value=90, value=0, step=5,
                                          help="The number of days saved in filling open roles because a higher-quality, upgraded workspace is more attractive to top candidates.")

            st.markdown("**Driver C: Commute Dividend**")
            st.markdown("_Annual value of recaptured commute time_")
            commute_time_saved = st.slider("Avg Commute Time Saved (Minutes/Day)", min_value=0, max_value=120, value=0, step=5,
                                          help="The average round-trip minutes saved per employee, per day, by moving the office closer to your core talent pool's geographic center.")
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
    """
    Calculate annual occupancy costs with escalation.
    FIX 2: base_rent is $/PSF/year (annual), not monthly - removed * 12
    FIX 3: Free rent can spill into Year 2 if > 12 months
    """
    annual_costs = []
    current_rent = base_rent

    for year in range(1, term_years + 1):
        if year == 1:
            # Year 1: Prorate for free months + TI benefit (one-time)
            occupied_months_yr1 = max(0, 12 - free_months)
            year_cost = (current_rent * sq_ft) * (occupied_months_yr1 / 12) - (ti_allowance * sq_ft)
        elif year == 2 and free_months > 12:
            # Year 2: Handle free rent spillover
            spillover_months = free_months - 12
            occupied_months_yr2 = max(0, 12 - spillover_months)
            year_cost = (current_rent * sq_ft) * (occupied_months_yr2 / 12)
        else:
            # Years 2+ (or 3+ if spillover): Full year rent, no TI
            year_cost = current_rent * sq_ft

        annual_costs.append(year_cost)
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

# FIX 2: Strategic Drivers - Stay is pure baseline, Go gets benefits
# Stay: Pure baseline + turnover risk (Year 1 only)
renewal_costs[0] += turnover_risk  # Both scenarios get turnover penalty

# Go: Gets friction/moving/turnover (Year 1) - strategic benefits (annual savings)
friction_cost = calculate_friction_cost()
moving_cost = moving_costs_psf * target_sf
total_relocation_penalty = friction_cost + moving_cost + turnover_risk

relocation_costs[0] += total_relocation_penalty  # One-time costs in Year 1
for i in range(len(relocation_costs)):
    relocation_costs[i] -= (recruiting_benefit + commute_benefit)  # Annual benefits

# Calculate NPV for both scenarios
renewal_npv = calculate_npv(renewal_costs, discount_rate)
relocation_npv = calculate_npv(relocation_costs, discount_rate)
npv_savings = renewal_npv - relocation_npv

# Cumulative costs
renewal_cumulative = np.cumsum(renewal_costs)
relocation_cumulative = np.cumsum(relocation_costs)

# Breakeven - Fixed Logic
breakeven_month = None
breakeven_display = "Does Not Breakeven"  # Default

for year in range(lease_term):
    if relocation_cumulative[year] < renewal_cumulative[year]:
        # Found the year where Go becomes cheaper than Stay
        if year == 0:
            # Go is cheaper immediately
            breakeven_month = 0
            breakeven_display = "Immediate"
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
                # Format the display
                years = int(breakeven_month // 12)
                months = int(breakeven_month % 12)
                breakeven_display = f"{years}yr {months}mo"
            else:
                breakeven_month = year * 12
                years = int(breakeven_month // 12)
                months = int(breakeven_month % 12)
                breakeven_display = f"{years}yr {months}mo"
        break

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

# Waterfall Chart - Annual Annuity (Fixed: proper math and total bar)
st.subheader("💰 Executive Summary: Annual Annuity Waterfall",
            help="This chart bridges the financial gap between staying and relocating. It amortizes one-time costs (like moving and TI) and strategic benefits over the entire lease term to reveal the true annualized financial impact.")

# Calculate average annual costs (already includes all strategic drivers and costs)
avg_stay_cost = sum(renewal_costs) / lease_term
avg_go_cost = sum(relocation_costs) / lease_term

# FIX 2: Calculate average annual base rent (base_rent is already annual $/PSF, remove * 12)
stay_base_rent_total = 0
go_base_rent_total = 0
for year in range(lease_term):
    # Stay scenario base rent with escalation (base_rent is annual)
    stay_rent_this_year = renewal_base_rent * current_sf * ((1 + escalation_rate/100) ** year)
    stay_base_rent_total += stay_rent_this_year

    # Go scenario base rent with escalation (base_rent is annual)
    go_rent_this_year = new_base_rent * target_sf * ((1 + escalation_rate/100) ** year)
    go_base_rent_total += go_rent_this_year

avg_stay_base_rent = stay_base_rent_total / lease_term
avg_go_base_rent = go_base_rent_total / lease_term

# FIX 4: Calculate average annual TI benefit (annualized over lease term)
avg_ti_stay = (renewal_ti * current_sf) / lease_term
avg_ti_go = (new_ti * target_sf) / lease_term

# Build waterfall showing how we get from Stay to Go
# The math: avg_stay_cost + deltas = avg_go_cost
rent_delta = avg_go_base_rent - avg_stay_base_rent  # Positive = Go costs more
ti_delta = -(avg_ti_go - avg_ti_stay)  # Negative = Go gets more benefit (annualized)
strategic_benefit_delta = -(recruiting_benefit + commute_benefit)  # Negative = Go gets benefit
amortized_friction_delta = (friction_cost + moving_cost) / lease_term  # Positive = Go pays more
# Note: turnover_risk cancels out (both scenarios pay it)

waterfall_values = [
    avg_stay_cost,              # Starting point
    rent_delta,                 # Rent difference (positive if Go is more expensive)
    ti_delta,                   # TI benefit difference (negative if Go gets more)
    strategic_benefit_delta,    # Strategic benefits (negative = savings)
    amortized_friction_delta,   # One-time costs amortized (positive = cost)
    avg_go_cost                 # Ending point (TOTAL)
]

waterfall_labels = [
    "Stay Cost",
    "Rent Δ",
    "TI Benefit Δ",
    "Strategic Benefits",
    "Amortized Friction",
    "Go Cost"
]

waterfall_text = [f"${v:,.0f}" for v in waterfall_values]

# Set measure types: first is absolute, middle are relative, last is total
waterfall_measures = ["absolute", "relative", "relative", "relative", "relative", "total"]

fig_waterfall = go.Figure(go.Waterfall(
    x=waterfall_labels,
    y=waterfall_values,
    measure=waterfall_measures,  # FIX 1: Last bar is now "total" so it anchors to x-axis
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

# FIX 1 & 2 & 3: Remove opportunity_cost_annual, fix rent multiplier, handle free rent proration
renewal_year1_base = (renewal_base_rent * current_sf) * (max(0, 12 - renewal_free_rent) / 12)
renewal_year1_ti = renewal_ti * current_sf
renewal_year1_strategic = turnover_risk  # FIX 1: Removed opportunity_cost_annual

relocation_year1_base = (new_base_rent * target_sf) * (max(0, 12 - new_free_rent) / 12)
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

# FIX 1: Removed 'Opportunity Cost' bar (opportunity_cost_annual no longer exists)

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

# HHI Team Contact Footer
st.markdown("""
    <hr style="border-top: 1px solid #e2e8f0; margin-top: 60px; margin-bottom: 30px;">
    <div style="text-align: center; padding: 24px; font-family: sans-serif; color: #1e293b; background-color: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; max-width: 800px; margin: 0 auto;">
        <h3 style="margin-bottom: 4px; font-size: 18px; font-weight: bold; color: #1e293b;">Sam Horowitz & The HHI Team</h3>
        <p style="font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: bold; margin-bottom: 16px;">Colliers International</p>
        <p style="font-size: 14px; color: #64748b; font-style: italic; margin-bottom: 24px;">Need a custom financial model or alternative space analysis?</p>
        <div style="margin-bottom: 16px;">
            <a href="mailto:Sam.Horowitz@colliers.com?subject=Re: Stay vs. Go Analysis" style="display: inline-block; padding: 10px 24px; background-color: #1e293b; color: #ffffff; text-decoration: none; font-size: 14px; font-weight: bold; border-radius: 8px; margin-right: 12px; transition: background-color 0.2s;">Let's Talk</a>
            <a href="https://www.colliers.com/en-us/experts/sam-horowitz" target="_blank" style="display: inline-block; padding: 10px 24px; background-color: #ffffff; color: #334155; text-decoration: none; font-size: 14px; font-weight: bold; border-radius: 8px; border: 1px solid #cbd5e1; transition: background-color 0.2s;">View My Profile</a>
        </div>
        <p style="margin-top: 24px; font-size: 10px; color: #94a3b8; line-height: 1.6; text-align: justify;">
            <strong>Disclaimer:</strong> The financial modeling, NPV calculations, and comparative data provided by this logic engine are for informational and planning purposes only. While the information has been obtained from sources deemed reliable, Sam Horowitz, The HHI Team, and Colliers International make no guarantees, warranties, or representations, express or implied, regarding the accuracy, completeness, or current nature of the data. Users should conduct their own independent investigation and due diligence before making real estate decisions.
        </p>
    </div>
""", unsafe_allow_html=True)