# 🏢 Stay vs. Go: Commercial Real Estate Decision Tool

A professional Streamlit web application for commercial real estate brokers to analyze the financial impact of lease renewal vs. relocation for office and industrial tenants.

## Features

### Core Functionality
- **Dual Scenario Comparison**: Side-by-side analysis of "Stay (Renewal)" vs. "Go (Relocate)"
- **10-Year Financial Projection**: Year-over-year and cumulative cost tracking
- **Net Effective Rent (NER) Calculation**: Industry-standard methodology with TI amortization
- **Breakeven Analysis**: Identifies the exact month when relocation becomes cheaper
- **Interactive Visualizations**: Professional Plotly charts with clean, minimalist design

### The "Horowitz Friction" Methodology
Unlike traditional lease analyses that focus solely on rent, this tool accounts for **real-world transition costs**:

#### Office Mode
- **Productivity Loss**: Calculates the hidden cost of employee downtime during a move
- Formula: `(Headcount × Average Salary ÷ 2,080 hours) × Productivity Hours Lost`
- Captures the impact of packing, unpacking, IT setup, and adjustment period

#### Industrial Mode
- **Operational Downtime**: 2-week production shutdown cost
- Formula: `Daily Revenue Loss × 14 days`
- **Machinery Rigging & Electrical Infrastructure**: One-time capital expense for relocating equipment
- Designed for manufacturing, warehousing, and distribution facilities

### Key Metrics Dashboard
1. **10-Year Total Cost Delta**: Total difference between staying vs. relocating
2. **Breakeven Point**: When relocation becomes financially advantageous
3. **10-Year Savings**: Total savings (or premium) with percentage comparison

### Visualizations
1. **Cumulative Cost Line Chart**: Shows the intersection point where "Go" becomes cheaper than "Stay"
2. **Year 1 Cash Outflow Bar Chart**: Stacked breakdown of rent, moving costs, friction costs, and TI benefits

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run stay_vs_go_app.py
```

3. The app will open automatically in your browser at `http://localhost:8501`

## Usage

### Input Parameters

#### Property Details
- **Square Footage**: Total rentable square feet (default: 20,000)

#### Financial Parameters
- **Annual Rent Escalation**: Percentage increase per year (adjustable slider, default: 3%)

#### Scenario A: Stay (Renewal)
- **Renewal Base Rent ($/PSF)**: Base rent for staying at current location
- **Renewal Free Rent (Months)**: Concession period with no rent
- **Renewal TI Allowance ($/PSF)**: Tenant improvement allowance from landlord

#### Scenario B: Go (Relocate)
- **New Base Rent ($/PSF)**: Base rent at new location
- **New Free Rent (Months)**: Move-in concession period
- **New TI Allowance ($/PSF)**: Build-out allowance at new space
- **Moving/FF&E Costs ($/PSF)**: One-time moving and furniture costs (default: $25)

#### Horowitz Friction (Office Mode)
- **Productivity Loss per Employee**: Hours of lost productivity during transition (default: 8)
- **Headcount**: Number of employees affected by the move (default: 50)
- **Average Salary**: Company average salary for cost calculation (default: $150,000)

#### Horowitz Friction (Industrial Mode)
- **Daily Revenue/Production Value**: Average daily revenue for downtime calculation (default: $50,000)
- **Machinery Rigging & Electrical ($/SF)**: Cost to relocate equipment and infrastructure (default: $15)

### Example Scenarios

#### Scenario 1: Suburban Office Renewal
- **Context**: 20,000 SF suburban office, current rent $35/SF, potential move to newer building at $30/SF
- **Inputs**:
  - Renewal: $35/SF, 2 months free, $5/SF TI
  - New: $30/SF, 6 months free, $60/SF TI
  - 50 employees, $150K avg salary, 8 hours productivity loss
- **Expected Result**: Relocation breaks even around Year 2-3 due to lower base rent and higher TI allowance

#### Scenario 2: Industrial Facility Relocation
- **Context**: 100,000 SF warehouse considering move to modern distribution center
- **Inputs**:
  - Toggle "Industrial Mode" ON
  - Renewal: $12/SF, 0 months free, $0 TI
  - New: $10/SF, 3 months free, $5/SF TI
  - Daily revenue: $100K, Machinery rigging: $20/SF
- **Expected Result**: Higher upfront costs due to operational downtime, but long-term savings from rent differential

## Financial Methodology

### Net Effective Rent (NER) Calculation
The NER represents the true average monthly cost of occupancy:

```
NER = (Total Rent over Term - Free Rent Value - TI Allowance) ÷ Total Months
```

Where:
- **Total Rent** includes annual escalations
- **TI Allowance** is amortized over the 10-year lease term
- **Free Rent** is deducted at full base rent value

### Friction Cost Application
The friction cost (productivity loss or operational downtime) is a **one-time penalty** added to Year 1 of the relocation scenario. This reflects the reality that moving disrupts business operations in the short term.

### Breakeven Analysis
The breakeven point is calculated by finding when the **cumulative** cost of relocating drops below the cumulative cost of staying. This accounts for the fact that even with high upfront costs, lower ongoing rent eventually creates savings.

## Use Cases

### For Brokers
- **Tenant Representation**: Quantify the true cost of staying vs. relocating for your clients
- **Renewal Negotiations**: Show landlords the financial threshold they need to beat
- **Portfolio Strategy**: Help multi-location tenants prioritize which leases to renegotiate

### For Tenants
- **CFO Presentations**: Professional visualizations for board meetings
- **Budget Planning**: Understand cash flow impact of real estate decisions
- **Risk Assessment**: Quantify the hidden costs of moving (not just the rent)

### For Landlords
- **Retention Strategy**: Understand what it takes to keep a tenant vs. losing them
- **Competitive Positioning**: See how your renewal offer compares to market alternatives

## Technical Details

### Technology Stack
- **Streamlit**: Web application framework
- **Plotly**: Interactive charting library
- **Pandas**: Data manipulation and table display
- **NumPy**: Numerical calculations

### Performance
- Real-time recalculation on input changes
- Optimized for datasets up to 10 years
- Responsive design for desktop and tablet

### Customization
The app uses custom CSS for professional styling. To modify the color scheme or layout, edit the CSS block in the `st.markdown()` section near the top of the file.

## Tips for Accurate Analysis

1. **Use Market Data**: Base rent and TI allowances should reflect current market rates for comparable properties
2. **Be Conservative with Friction**: The default 8 hours of productivity loss is conservative; some moves cause significantly more disruption
3. **Consider Hidden Costs**: Moving/FF&E at $25/PSF is a starting point; actual costs vary by building type and distance
4. **Adjust Escalations**: 3% is typical for NJ office, but industrial may be 2-3%, and hot markets could be higher
5. **Industrial Downtime**: 2 weeks is aggressive for a well-planned move; complex machinery relocations may take 4-6 weeks

## Roadmap / Future Enhancements

Potential features for future versions:
- [ ] Operating expense (NNN) comparison
- [ ] Parking and amenity cost analysis
- [ ] Commute impact analysis (employee retention)
- [ ] Custom lease term (currently fixed at 10 years)
- [ ] PDF report export for client presentations
- [ ] Sensitivity analysis (best case / worst case scenarios)
- [ ] Multi-location comparison (3+ options)

## License

This tool is provided as-is for commercial real estate professionals. Feel free to customize for your specific market or use case.

## Support

For questions, customization requests, or feedback, contact:
**Sam Horowitz** | horowitz.sam@gmail.com

---

*Built with ❤️ for the NJ commercial real estate community*
