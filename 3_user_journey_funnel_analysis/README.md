# 🛒 User Journey Funnel Analysis

**Tools:** Python · Pandas · Matplotlib · Seaborn  
**Domain:** Product Analytics · E-commerce · Conversion Optimisation

---

## 📌 Problem Statement
Users are visiting the platform but not completing signup or purchase. This project maps the complete user journey funnel, calculates drop-off rates at each stage, and segments by device, city, and traffic source to identify exactly where — and why — users are abandoning.

---

## 🔻 Funnel Stages Tracked

```
Visit → Signup → Add to Cart → Purchase
```

Drop-off is calculated at every transition. The biggest friction point is surfaced automatically.

---

## 📊 Segments Analysed

| Segment | Why It Matters |
|---------|---------------|
| **Device** (Mobile/Desktop/Tablet) | Mobile users drop off 2x more at cart — critical UX insight |
| **Location** (City-wise) | Identify high-intent markets for targeted campaigns |
| **Traffic Source** | Know which channels bring buyers, not just browsers |
| **Monthly Cohort** | Track whether conversion is improving over time |

---

## 📁 Project Structure

```
3_user_journey_funnel_analysis/
│
├── funnel_analysis.py          # Main script (run this)
├── requirements.txt
├── README.md
│
├── data/
│   └── user_events.csv         # Auto-generated on first run
│
└── outputs/
    ├── funnel_analysis_dashboard.png   # Full 7-panel dashboard
    ├── device_funnel.csv               # Conversion by device
    ├── location_funnel.csv             # Conversion by city
    ├── monthly_trends.csv              # Monthly conversion trends
    └── source_funnel.csv               # Conversion by traffic source
```

---

## 🚀 How to Run

```bash
pip install -r requirements.txt
python funnel_analysis.py
```

---

## 📊 Dashboard Panels

1. **Overall Funnel** — Waterfall bar chart with user counts and conversion rates
2. **KPI Summary** — Key metrics (revenue, ARPU, conversion rate)
3. **Funnel by Device** — Side-by-side comparison across Mobile/Desktop/Tablet
4. **Conversion Rates by Device** — Signup %, Cart %, Purchase % per device
5. **Purchase Rate by City** — City-wise performance vs average
6. **Monthly Trend** — Conversion rate trends over 12 months
7. **Traffic Source Performance** — Best-performing acquisition channels

---

## 🔍 Key Insights (Simulated)

- **Mobile cart abandonment** is ~2x higher than Desktop — biggest revenue leak
- **Email traffic** converts at highest rate — most intent-driven channel
- Biggest funnel drop-off is typically at the **Signup stage**
- Metro cities (Mumbai, Bangalore, Delhi) drive highest purchase rates

---

## 🎯 Recommendations Generated Automatically

The script outputs specific, data-backed recommendations:
- Which stage needs UX improvement
- Which device needs checkout optimisation
- Which traffic source to increase budget for
- Which cities to target with campaigns

---

## 🧠 Skills Demonstrated
- Event-level funnel construction
- Multi-segment cohort analysis
- Drop-off identification & root cause framing
- Business recommendation generation from data
- Multi-panel dashboard design
