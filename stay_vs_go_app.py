import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Stay vs. Go Analysis",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Password Protection
def check_password():
    """Returns `True` if the user has entered the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets.get("password", "horowitz2026"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run, show password input
    if "password_correct" not in st.session_state:
        st.text_input(
            "🔐 Enter Access Code", type="password", on_change=password_entered, key="password"
        )
        st.info("This tool is password-protected for client use. Contact Sam Horowitz for access.")
        return False
    # Password incorrect, show error
    elif not st.session_state["password_correct"]:
        st.text_input(
            "🔐 Enter Access Code", type="password", on_change=password_entered, key="password"
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
st.title("🏢 Stay vs. Go: Commercial Real Estate Decision Tool")
st.markdown("### Financial Impact Analysis for Office Tenants")
st.markdown("---")

# Sidebar for inputs
with st.sidebar:
    st.header("📊 Scenario Inputs")

    # Industrial Mode Toggle
    industrial_mode = st.toggle("🏭 Industrial Mode", value=False,
                                help="Switch to industrial/warehouse analysis with machinery costs and operational downtime")

    st.subheader("Property Details")
    square_footage = st.number_input("Square Footage", min_value=1000, value=20000, step=1000)

    st.subheader("Financial Parameters")
    escalation_rate = st.slider("Annual Rent Escalation (%)", min_value=0.0, max_value=5.0, value=3.0, step=0.25)

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
        st.subheader("⚡ Horowitz Friction (Office)")
        productivity_loss_hours = st.slider("Productivity Loss per Employee (Hours)",
                                            min_value=0, max_value=80, value=8, step=1)
        headcount = st.number_input("Headcount", min_value=1, value=50, step=1)
        avg_salary = st.number_input("Average Salary ($)", min_value=0, value=150000, step=5000)
    else:
        st.subheader("🏭 Horowitz Friction (Industrial)")
        daily_revenue_loss = st.number_input("Daily Revenue/Production Value ($)",
                                             min_value=0, value=50000, step=5000,
                                             help="Average daily revenue or production value")
        machinery_rigging = st.number_input("Machinery Rigging & Electrical ($/SF)",
                                           min_value=0.0, value=15.0, step=1.0,
                                           help="One-time capital expense for moving machinery and electrical infrastructure")

# Calculate Net Effective Rent
def calculate_ner(base_rent, free_months, ti_allowance, term_years=10):
    """
    Calculate Net Effective Rent over the lease term.
    NER = (Total Rent - Free Rent - TI Allowance) / Total Months
    """
    total_months = term_years * 12

    # Calculate total base rent over term (with escalation)
    total_rent = 0
    current_rent = base_rent
    for year in range(term_years):
        total_rent += current_rent * 12
        current_rent *= (1 + escalation_rate / 100)

    # Adjust for free rent months
    free_rent_value = base_rent * free_months

    # TI allowance is amortized over term
    ti_benefit = ti_allowance * term_years  # TI benefit spread over term

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

        annual_costs.append(max(0, year_cost))  # Ensure no negative costs
        current_rent *= (1 + escalation_rate / 100)

    return annual_costs

# Calculate friction cost
def calculate_friction_cost():
    """Calculate one-time friction/moving penalty."""
    if not industrial_mode:
        # Office mode: Productivity loss
        hourly_cost = avg_salary / 2080
        friction = headcount * hourly_cost * productivity_loss_hours
    else:
        # Industrial mode: 2 weeks operational downtime + machinery costs
        downtime_cost = daily_revenue_loss * 14
        rigging_cost = machinery_rigging * square_footage
        friction = downtime_cost + rigging_cost

    return friction

# Perform calculations
renewal_ner = calculate_ner(renewal_base_rent, renewal_free_rent, renewal_ti)
relocation_ner = calculate_ner(new_base_rent, new_free_rent, new_ti)

renewal_costs = calculate_annual_costs(renewal_base_rent, renewal_free_rent, renewal_ti, square_footage)
relocation_costs = calculate_annual_costs(new_base_rent, new_free_rent, new_ti, square_footage)

# Add friction cost to Year 1 of relocation
friction_cost = calculate_friction_cost()
moving_cost = moving_costs_psf * square_footage
total_relocation_penalty = friction_cost + moving_cost

relocation_costs[0] += total_relocation_penalty

# Calculate cumulative costs
renewal_cumulative = np.cumsum(renewal_costs)
relocation_cumulative = np.cumsum(relocation_costs)

# Find breakeven point
breakeven_month = None
for year in range(10):
    if relocation_cumulative[year] < renewal_cumulative[year]:
        # Interpolate to find the month
        if year == 0:
            breakeven_month = None  # Doesn't break even in year 1
        else:
            months_into_year = 12 * (renewal_cumulative[year-1] - relocation_cumulative[year-1]) / (renewal_costs[year] - relocation_costs[year])
            breakeven_month = year * 12 + months_into_year
        break

# Calculate total savings
total_10yr_savings = renewal_cumulative[-1] - relocation_cumulative[-1]

# Display Key Metrics
st.subheader("💡 Key Insights")
col1, col2, col3 = st.columns(3)

with col1:
    delta_cost = relocation_cumulative[-1] - renewal_cumulative[-1]
    st.metric(
        label="10-Year Total Cost Delta",
        value=f"${delta_cost:,.0f}",
        delta=f"{'More' if delta_cost > 0 else 'Savings'}" if delta_cost != 0 else "Break Even",
        delta_color="inverse"
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
        label="10-Year Savings (Go vs. Stay)",
        value=f"${total_10yr_savings:,.0f}",
        delta=f"{(total_10yr_savings / renewal_cumulative[-1] * 100):.1f}% savings" if total_10yr_savings > 0 else f"{abs(total_10yr_savings / renewal_cumulative[-1] * 100):.1f}% premium",
        delta_color="normal" if total_10yr_savings > 0 else "inverse"
    )

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
renewal_year1_base = renewal_base_rent * square_footage * (12 - renewal_free_rent)
renewal_year1_ti_benefit = renewal_ti * square_footage

relocation_year1_base = new_base_rent * square_footage * (12 - new_free_rent)
relocation_year1_ti_benefit = new_ti * square_footage
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
    name='Friction Cost',
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
    <p><strong>Stay vs. Go Analysis Tool</strong> | Built for Commercial Real Estate Professionals</p>
    <p style='font-size: 0.9em;'>The "Horowitz Friction" methodology accounts for real-world transition costs often overlooked in traditional lease analyses.</p>
</div>
""", unsafe_allow_html=True)
