"""
User Journey Funnel Analysis
=============================
Tools: Python, Pandas, Matplotlib, Seaborn
Funnel: Visit → Signup → Add to Cart → Purchase
Segments: Device, Location, Cohort
Author: Kartik Kumar
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os
warnings.filterwarnings('ignore')

os.makedirs('data', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

print("=" * 65)
print("  USER JOURNEY FUNNEL ANALYSIS")
print("=" * 65)

# ─────────────────────────────────────────
# 1. GENERATE EVENT-LEVEL DATA
# ─────────────────────────────────────────
np.random.seed(42)
N_VISITS = 15000

dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
devices = ['Mobile', 'Desktop', 'Tablet']
device_weights = [0.55, 0.35, 0.10]
locations = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Other']
loc_weights = [0.20, 0.18, 0.17, 0.10, 0.10, 0.10, 0.08, 0.07]
traffic_sources = ['Organic Search', 'Paid Ads', 'Social Media', 'Email', 'Direct', 'Referral']
source_weights = [0.30, 0.25, 0.20, 0.10, 0.10, 0.05]

df = pd.DataFrame({
    'user_id': [f'U{str(i).zfill(6)}' for i in range(1, N_VISITS + 1)],
    'visit_date': np.random.choice(dates, N_VISITS),
    'device': np.random.choice(devices, N_VISITS, p=device_weights),
    'location': np.random.choice(locations, N_VISITS, p=loc_weights),
    'traffic_source': np.random.choice(traffic_sources, N_VISITS, p=source_weights),
    'session_duration_sec': np.random.exponential(120, N_VISITS).astype(int).clip(5, 900),
    'pages_viewed': np.random.randint(1, 15, N_VISITS),
})
df['visit_date'] = pd.to_datetime(df['visit_date'])
df['month'] = df['visit_date'].dt.to_period('M')
df['week'] = df['visit_date'].dt.isocalendar().week

# Funnel conversion probabilities per device (Mobile intentionally lower)
device_conv = {'Mobile': 0.18, 'Desktop': 0.35, 'Tablet': 0.25}
signup_conv  = {'Mobile': 0.52, 'Desktop': 0.68, 'Tablet': 0.60}
cart_conv    = {'Mobile': 0.30, 'Desktop': 0.55, 'Tablet': 0.42}
purchase_conv= {'Mobile': 0.40, 'Desktop': 0.62, 'Tablet': 0.50}

df['signed_up'] = df.apply(
    lambda r: int(np.random.random() < device_conv[r['device']] *
                  (1.2 if r['traffic_source'] == 'Email' else 1.0) *
                  (0.8 if r['pages_viewed'] < 2 else 1.0)), axis=1)

df['added_to_cart'] = df.apply(
    lambda r: int(r['signed_up'] and np.random.random() < signup_conv[r['device']]), axis=1)

df['purchased'] = df.apply(
    lambda r: int(r['added_to_cart'] and np.random.random() < cart_conv[r['device']]), axis=1)

df['order_value'] = df.apply(
    lambda r: round(np.random.uniform(299, 4999), 2) if r['purchased'] else 0, axis=1)

df.to_csv('data/user_events.csv', index=False)
print(f"\n✅ Dataset: {len(df):,} users generated")

# ─────────────────────────────────────────
# 2. OVERALL FUNNEL METRICS
# ─────────────────────────────────────────
stages = {
    'Visit': len(df),
    'Signup': df['signed_up'].sum(),
    'Add to Cart': df['added_to_cart'].sum(),
    'Purchase': df['purchased'].sum()
}

funnel_df = pd.DataFrame(list(stages.items()), columns=['Stage', 'Users'])
funnel_df['Conv_from_visit'] = funnel_df['Users'] / funnel_df['Users'].iloc[0] * 100
funnel_df['Conv_from_prev'] = funnel_df['Users'].pct_change() * 100
funnel_df['Dropoff'] = funnel_df['Users'].shift(1) - funnel_df['Users']

print(f"\n📊 OVERALL FUNNEL")
print(f"   {'Stage':<15} {'Users':>8} {'Conv%':>8} {'Drop-off':>10}")
print("   " + "-" * 45)
for _, row in funnel_df.iterrows():
    drop = f"{row['Dropoff']:,.0f}" if not pd.isna(row['Dropoff']) else '—'
    print(f"   {row['Stage']:<15} {row['Users']:>8,} {row['Conv_from_visit']:>7.1f}% {drop:>10}")

revenue = df['order_value'].sum()
arpu = revenue / len(df)
print(f"\n   💰 Total Revenue : ₹{revenue:,.0f}")
print(f"   📈 ARPU          : ₹{arpu:.2f} per visitor")

# ─────────────────────────────────────────
# 3. FUNNEL BY DEVICE
# ─────────────────────────────────────────
device_funnel = df.groupby('device').agg(
    Visits=('user_id', 'count'),
    Signups=('signed_up', 'sum'),
    Carts=('added_to_cart', 'sum'),
    Purchases=('purchased', 'sum'),
    Revenue=('order_value', 'sum')
).reset_index()

device_funnel['Signup_Rate']  = device_funnel['Signups'] / device_funnel['Visits'] * 100
device_funnel['Cart_Rate']    = device_funnel['Carts'] / device_funnel['Visits'] * 100
device_funnel['Purchase_Rate']= device_funnel['Purchases'] / device_funnel['Visits'] * 100

print(f"\n📱 FUNNEL BY DEVICE")
print(f"   {'Device':<10} {'Visits':>8} {'Signup%':>9} {'Cart%':>7} {'Purchase%':>11} {'Revenue':>12}")
print("   " + "-" * 60)
for _, row in device_funnel.iterrows():
    print(f"   {row['device']:<10} {row['Visits']:>8,} {row['Signup_Rate']:>8.1f}% "
          f"{row['Cart_Rate']:>6.1f}% {row['Purchase_Rate']:>10.1f}% ₹{row['Revenue']:>10,.0f}")

mob = device_funnel[device_funnel['device'] == 'Mobile']['Cart_Rate'].values[0]
desk = device_funnel[device_funnel['device'] == 'Desktop']['Cart_Rate'].values[0]
print(f"\n   ⚠️  Mobile cart rate is {desk/mob:.1f}x lower than Desktop — key friction point!")

# ─────────────────────────────────────────
# 4. FUNNEL BY LOCATION
# ─────────────────────────────────────────
loc_funnel = df.groupby('location').agg(
    Visits=('user_id', 'count'),
    Purchases=('purchased', 'sum'),
    Revenue=('order_value', 'sum')
).reset_index()
loc_funnel['Purchase_Rate'] = loc_funnel['Purchases'] / loc_funnel['Visits'] * 100
loc_funnel = loc_funnel.sort_values('Purchase_Rate', ascending=False)

print(f"\n📍 PURCHASE RATE BY CITY")
for _, row in loc_funnel.iterrows():
    bar = '█' * int(row['Purchase_Rate'] * 2)
    print(f"   {row['location']:<12} {bar:<20} {row['Purchase_Rate']:.1f}%  (₹{row['Revenue']:,.0f})")

# ─────────────────────────────────────────
# 5. FUNNEL BY TRAFFIC SOURCE
# ─────────────────────────────────────────
source_funnel = df.groupby('traffic_source').agg(
    Visits=('user_id', 'count'),
    Signups=('signed_up', 'sum'),
    Purchases=('purchased', 'sum'),
    Revenue=('order_value', 'sum')
).reset_index()
source_funnel['Purchase_Rate'] = source_funnel['Purchases'] / source_funnel['Visits'] * 100
source_funnel = source_funnel.sort_values('Purchase_Rate', ascending=False)

print(f"\n🔗 PURCHASE RATE BY TRAFFIC SOURCE")
for _, row in source_funnel.iterrows():
    print(f"   {row['traffic_source']:<18} {row['Purchase_Rate']:>5.1f}%  ({row['Visits']:,} visits)")

# ─────────────────────────────────────────
# 6. MONTHLY COHORT FUNNEL TRENDS
# ─────────────────────────────────────────
monthly = df.groupby('month').agg(
    Visits=('user_id', 'count'),
    Signups=('signed_up', 'sum'),
    Carts=('added_to_cart', 'sum'),
    Purchases=('purchased', 'sum'),
    Revenue=('order_value', 'sum')
).reset_index()
monthly['Signup_Rate']   = monthly['Signups'] / monthly['Visits'] * 100
monthly['Cart_Rate']     = monthly['Carts'] / monthly['Visits'] * 100
monthly['Purchase_Rate'] = monthly['Purchases'] / monthly['Visits'] * 100
monthly['month_str']     = monthly['month'].astype(str)

# ─────────────────────────────────────────
# 7. FULL DASHBOARD VISUALISATION
# ─────────────────────────────────────────
fig = plt.figure(figsize=(20, 18))
fig.patch.set_facecolor('#F8F9FA')
fig.suptitle('🛒 User Journey Funnel Analysis Dashboard', fontsize=22,
             fontweight='bold', y=0.98, color='#1A1A2E')
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.5, wspace=0.38)

COLORS = ['#2196F3', '#4CAF50', '#FF9800', '#F44336']
DEVICE_COLORS = {'Mobile': '#FF6B6B', 'Desktop': '#4ECDC4', 'Tablet': '#45B7D1'}

# Plot 1: Funnel waterfall
ax1 = fig.add_subplot(gs[0, :2])
bars = ax1.bar(funnel_df['Stage'], funnel_df['Users'],
               color=COLORS, edgecolor='white', linewidth=1.5, width=0.55)
ax1.set_title('Overall Conversion Funnel', fontweight='bold', fontsize=14)
ax1.set_ylabel('Number of Users')
for bar, row in zip(bars, funnel_df.itertuples()):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 80,
             f'{row.Users:,}\n({row.Conv_from_visit:.1f}%)',
             ha='center', fontsize=10, fontweight='bold')
    if not pd.isna(row.Dropoff) and row.Dropoff > 0:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                 f'↓{row.Dropoff:,.0f}\nlost', ha='center', fontsize=8,
                 color='white', fontweight='bold')
ax1.set_facecolor('#FAFAFA')
ax1.grid(axis='y', alpha=0.3)

# Plot 2: KPI summary
ax2 = fig.add_subplot(gs[0, 2])
ax2.axis('off')
kpis = [
    ('Total Visitors', f'{len(df):,}', '#2196F3'),
    ('Total Purchases', f'{df["purchased"].sum():,}', '#4CAF50'),
    ('Overall Conv. Rate', f'{df["purchased"].mean()*100:.1f}%', '#FF9800'),
    ('Total Revenue', f'₹{revenue/1e5:.1f}L', '#9C27B0'),
    ('ARPU', f'₹{arpu:.0f}', '#F44336'),
    ('Avg Order Value', f'₹{df[df["purchased"]==1]["order_value"].mean():.0f}', '#009688'),
]
for i, (label, val, color) in enumerate(kpis):
    y = 0.9 - i * 0.15
    ax2.add_patch(plt.Rectangle((0.05, y-0.06), 0.9, 0.12,
                                 facecolor=color, alpha=0.1, transform=ax2.transAxes))
    ax2.text(0.5, y+0.01, val, transform=ax2.transAxes,
             ha='center', fontsize=14, fontweight='bold', color=color)
    ax2.text(0.5, y-0.04, label, transform=ax2.transAxes,
             ha='center', fontsize=9, color='#555555')
ax2.set_title('Key Metrics', fontweight='bold', fontsize=14)

# Plot 3: Funnel by device — grouped bar
ax3 = fig.add_subplot(gs[1, 0])
x = np.arange(4)
width = 0.25
stage_cols = ['Visits', 'Signups', 'Carts', 'Purchases']
for i, (dev, color) in enumerate(DEVICE_COLORS.items()):
    vals = device_funnel[device_funnel['device'] == dev][stage_cols].values[0]
    ax3.bar(x + i*width, vals, width, label=dev, color=color, alpha=0.85, edgecolor='white')
ax3.set_xticks(x + width)
ax3.set_xticklabels(['Visits', 'Signups', 'Carts', 'Purchases'], fontsize=9)
ax3.set_title('Funnel by Device Type', fontweight='bold', fontsize=13)
ax3.set_ylabel('Users')
ax3.legend(fontsize=9)
ax3.set_facecolor('#FAFAFA')

# Plot 4: Conversion rates by device
ax4 = fig.add_subplot(gs[1, 1])
rate_cols = ['Signup_Rate', 'Cart_Rate', 'Purchase_Rate']
x4 = np.arange(len(rate_cols))
for i, (dev, color) in enumerate(DEVICE_COLORS.items()):
    vals = device_funnel[device_funnel['device'] == dev][rate_cols].values[0]
    ax4.bar(x4 + i*0.25, vals, 0.25, label=dev, color=color, alpha=0.85, edgecolor='white')
ax4.set_xticks(x4 + 0.25)
ax4.set_xticklabels(['Signup\nRate', 'Cart\nRate', 'Purchase\nRate'], fontsize=9)
ax4.set_title('Conversion Rates by Device (%)', fontweight='bold', fontsize=13)
ax4.set_ylabel('Conversion Rate (%)')
ax4.legend(fontsize=9)
ax4.set_facecolor('#FAFAFA')

# Plot 5: Purchase rate by city
ax5 = fig.add_subplot(gs[1, 2])
loc_sorted = loc_funnel.sort_values('Purchase_Rate')
colors5 = ['#E74C3C' if v < loc_funnel['Purchase_Rate'].mean() else '#2ECC71'
           for v in loc_sorted['Purchase_Rate']]
ax5.barh(loc_sorted['location'], loc_sorted['Purchase_Rate'],
         color=colors5, edgecolor='white', alpha=0.85)
ax5.axvline(x=loc_funnel['Purchase_Rate'].mean(), color='gray',
            linestyle='--', alpha=0.7, label='Average')
ax5.set_title('Purchase Rate by City (%)', fontweight='bold', fontsize=13)
ax5.set_xlabel('Purchase Rate (%)')
ax5.legend(fontsize=9)
ax5.set_facecolor('#FAFAFA')

# Plot 6: Monthly trend — conversion rates
ax6 = fig.add_subplot(gs[2, :2])
ax6.plot(monthly['month_str'], monthly['Signup_Rate'], 'o-',
         color='#2196F3', linewidth=2, markersize=5, label='Signup Rate')
ax6.plot(monthly['month_str'], monthly['Cart_Rate'], 's-',
         color='#FF9800', linewidth=2, markersize=5, label='Cart Rate')
ax6.plot(monthly['month_str'], monthly['Purchase_Rate'], '^-',
         color='#4CAF50', linewidth=2, markersize=5, label='Purchase Rate')
ax6.set_title('Monthly Conversion Rate Trends', fontweight='bold', fontsize=13)
ax6.set_ylabel('Conversion Rate (%)')
ax6.set_xticklabels(monthly['month_str'], rotation=45, ha='right', fontsize=8)
ax6.legend(fontsize=10)
ax6.grid(alpha=0.3)
ax6.set_facecolor('#FAFAFA')

# Plot 7: Traffic source performance
ax7 = fig.add_subplot(gs[2, 2])
source_sorted = source_funnel.sort_values('Purchase_Rate', ascending=True)
colors7 = plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(source_sorted)))
bars7 = ax7.barh(source_sorted['traffic_source'], source_sorted['Purchase_Rate'],
                  color=colors7, edgecolor='white', alpha=0.9)
ax7.set_title('Purchase Rate by Traffic Source (%)', fontweight='bold', fontsize=13)
ax7.set_xlabel('Purchase Rate (%)')
for bar, val in zip(bars7, source_sorted['Purchase_Rate']):
    ax7.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
             f'{val:.1f}%', va='center', fontsize=9, fontweight='bold')
ax7.set_facecolor('#FAFAFA')

plt.savefig('outputs/funnel_analysis_dashboard.png', dpi=150, bbox_inches='tight',
            facecolor='#F8F9FA')
plt.close()
print(f"\n✅ Dashboard saved: outputs/funnel_analysis_dashboard.png")

# ─────────────────────────────────────────
# 8. RECOMMENDATIONS
# ─────────────────────────────────────────
print("\n🎯 ACTIONABLE RECOMMENDATIONS")
print("=" * 65)
biggest_drop_stage = funnel_df.loc[funnel_df['Dropoff'].idxmax(), 'Stage']
print(f"\n   1. BIGGEST DROP-OFF: {biggest_drop_stage}")
print(f"      → Investigate UX friction at this stage — simplify the flow")
print(f"\n   2. MOBILE OPTIMISATION (Cart rate {mob:.1f}% vs Desktop {desk:.1f}%)")
print(f"      → Mobile users drop off {desk/mob:.1f}x more at cart — fix mobile checkout UX")
best_source = source_funnel.iloc[0]['traffic_source']
print(f"\n   3. INVEST MORE IN: {best_source}")
print(f"      → Highest purchase rate channel — increase budget allocation")
best_city = loc_funnel.iloc[0]['location']
print(f"\n   4. TOP CITY: {best_city} has highest purchase rate")
print(f"      → Run city-targeted campaigns to capture more high-intent users")

# Save outputs
device_funnel.to_csv('outputs/device_funnel.csv', index=False)
loc_funnel.to_csv('outputs/location_funnel.csv', index=False)
monthly.to_csv('outputs/monthly_trends.csv', index=False)
source_funnel.to_csv('outputs/source_funnel.csv', index=False)

print(f"\n✅ All CSVs saved in outputs/")
print("\n" + "=" * 65)
print("  ANALYSIS COMPLETE — Check /outputs folder")
print("=" * 65)
