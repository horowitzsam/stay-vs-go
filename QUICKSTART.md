# ⚡ Quick Start Guide

Get your Stay vs. Go analysis tool running in under 2 minutes.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run stay_vs_go_app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## Quick Usage

### Default Scenario (Office)
The app loads with realistic defaults for a **20,000 SF suburban NJ office**:
- Current renewal: $35/SF with 2 months free
- New space: $30/SF with 6 months free and $60/SF TI
- 50 employees, $150K average salary

**Just adjust the sliders and see results in real-time!**

### Industrial Mode
Toggle **"🏭 Industrial Mode"** at the top of the sidebar to switch to:
- Operational downtime calculator (2 weeks of lost production)
- Machinery rigging & electrical infrastructure costs
- Revenue-based friction analysis

## Key Features

### What You'll See
1. **Top Metrics**: Total cost delta, breakeven point, 10-year savings
2. **Cumulative Cost Chart**: When does relocation pay off?
3. **Year 1 Breakdown**: Upfront costs vs. savings visualization
4. **Year-by-Year Table**: Detailed annual comparison

### The "Horowitz Friction" Factor
Unlike traditional analyses, this tool captures the **real cost of moving**:
- **Office**: Lost productivity during transition (hours × headcount × salary)
- **Industrial**: Production shutdown (daily revenue × 14 days) + equipment relocation

## Typical Workflow

1. **Input Current Lease Terms**: Enter your renewal offer in "Scenario A"
2. **Input Alternative Offer**: Enter the competing space details in "Scenario B"
3. **Adjust Friction Costs**: Be honest about downtime and moving costs
4. **Review Breakeven**: When does the move pay for itself?
5. **Export for Client**: Screenshot the charts or share your screen

## Pro Tips

- **Lower base rent isn't always better** - watch for high moving costs offsetting savings
- **Free rent is powerful** - 6 months free can offset a lot of Year 1 costs
- **TI allowance matters** - A high TI ($60/SF) can make relocation very attractive
- **Friction costs are real** - Don't underestimate the 8-hour productivity hit per employee
- **Industrial moves are expensive** - 2 weeks of downtime + rigging costs add up fast

## Common Questions

**Q: Can I change the lease term from 10 years?**
A: Currently fixed at 10 years. Future versions will support custom terms.

**Q: Does this include operating expenses (NNN)?**
A: Not yet - assumes similar OpEx between buildings. Focus is on base rent differential.

**Q: What escalation rate should I use?**
A: 3% is typical for NJ office, 2.5% for industrial. Hot markets may be 4%+.

**Q: Can I export the results?**
A: Use your browser's screenshot tool or "Print to PDF" for now. PDF export coming in v2.

## Example Output

For the default scenario, you'll typically see:
- **Breakeven**: Around Year 2-3
- **10-Year Savings**: $500K - $1M range
- **Year 1**: Higher cost for "Go" due to moving + friction
- **Year 2+**: "Go" becomes cheaper due to lower base rent

---

**Ready to go?** Run `streamlit run stay_vs_go_app.py` and start analyzing! 🚀
