import pandas as pd
import numpy as np

np.random.seed(42)

def make_timeseries(start, end, freq="D"):
    """Generate daily date range for more granular data"""
    return pd.date_range(start, end, freq=freq)

# Generate 100 days of data across different periods
dates = make_timeseries("2023-01-01", "2023-04-10")  # 100 days

# Expand regions and product lines for more variety
regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
product_lines = ["Premium Line", "Standard Line", "Economy Line", "Enterprise Line"]
channels = ["Online", "Retail", "Wholesale", "Direct"]
customer_segments = ["SMB", "Enterprise", "Consumer", "Government"]

# Base budget trend with more realistic scaling
base_budget = 50_000  # Starting budget
growth_rate = 0.002   # Daily growth rate (about 70% annual)
budget_trend = base_budget * (1 + growth_rate) ** np.arange(len(dates))

# Add day-of-week seasonality (higher on weekdays, lower on weekends)
day_of_week = pd.to_datetime(dates).dayofweek
weekday_multiplier = np.where(day_of_week < 5, 1.2, 0.6)  # Higher on weekdays

# Add monthly seasonality
monthly_cycle = 1 + 0.15 * np.sin(2 * np.pi * np.arange(len(dates)) / 30)

# Create base dataframe with budget data
df = pd.DataFrame({
    "date": dates,
    "budget_sales": (budget_trend * monthly_cycle * weekday_multiplier).astype(int),
    "budget_volume": ((budget_trend * monthly_cycle * weekday_multiplier) / 45).astype(int),  # $45 avg price
    "budget_price": np.random.normal(45, 5, len(dates)).round(2),
    "budget_marketing": np.random.normal(5_000, 1_500, len(dates)).round(0).astype(int),
    "budget_cogs": (budget_trend * 0.65 * monthly_cycle).round(0).astype(int),  # 65% of sales
    "budget_labor": np.random.normal(8_000, 2_000, len(dates)).round(0).astype(int),
    "budget_overhead": np.random.normal(3_000, 800, len(dates)).round(0).astype(int),
})

# Simulate more realistic actuals with various factors
market_volatility = np.random.normal(1, 0.08, len(dates))  # Market conditions
competitor_impact = np.where(np.random.rand(len(dates)) < 0.15, 
                           np.random.uniform(0.85, 0.95, len(dates)), 1.0)  # Competitor events
supply_chain_issues = np.where(np.random.rand(len(dates)) < 0.05, 
                             np.random.uniform(0.7, 0.9, len(dates)), 1.0)  # Supply disruptions
promotional_boost = np.where(np.random.rand(len(dates)) < 0.1, 
                           np.random.uniform(1.15, 1.4, len(dates)), 1.0)  # Promotions

# Calculate actuals with realistic business variance
sales_variance = market_volatility * competitor_impact * supply_chain_issues * promotional_boost
df["actual_sales"] = (df.budget_sales * sales_variance).round(0).astype(int)

volume_variance = sales_variance * np.random.normal(1, 0.02, len(dates))  # Volume slightly different
df["actual_volume"] = (df.budget_volume * volume_variance).round(0).astype(int)

# Actual price based on sales/volume with some noise
df["actual_price"] = np.where(df.actual_volume > 0, 
                             (df.actual_sales / df.actual_volume).round(2), 
                             df.budget_price)

# Marketing spend variance (sometimes over/under budget)
df["actual_marketing"] = (df.budget_marketing * np.random.normal(1, 0.12, len(dates))).round(0).astype(int)

# COGS variance (supply chain affects costs)
cogs_variance = supply_chain_issues * np.random.normal(1, 0.06, len(dates))
df["actual_cogs"] = (df.budget_cogs * cogs_variance).round(0).astype(int)

# Labor variance (overtime, sick days, etc.)
df["actual_labor"] = (df.budget_labor * np.random.normal(1, 0.15, len(dates))).round(0).astype(int)

# Overhead variance (utilities, rent fluctuations)
df["actual_overhead"] = (df.budget_overhead * np.random.normal(1, 0.08, len(dates))).round(0).astype(int)

# Add calculated fields
df["sales_variance"] = df.actual_sales - df.budget_sales
df["sales_variance_pct"] = ((df.actual_sales / df.budget_sales - 1) * 100).round(2)
df["volume_variance"] = df.actual_volume - df.budget_volume
df["price_variance"] = df.actual_price - df.budget_price

# Add categorical dimensions with realistic distribution
np.random.seed(123)  # Different seed for categories
df["region"] = np.random.choice(regions, len(df), p=[0.35, 0.25, 0.20, 0.12, 0.08])
df["product_line"] = np.random.choice(product_lines, len(df), p=[0.15, 0.35, 0.35, 0.15])
df["channel"] = np.random.choice(channels, len(df), p=[0.40, 0.25, 0.20, 0.15])
df["customer_segment"] = np.random.choice(customer_segments, len(df), p=[0.30, 0.25, 0.30, 0.15])

# Add transaction-level details
df["transaction_id"] = [f"TXN_{i+1:05d}" for i in range(len(df))]
df["sales_rep"] = np.random.choice([f"Rep_{i:02d}" for i in range(1, 21)], len(df))
df["discount_pct"] = np.random.exponential(2, len(df)).round(2)
df["customer_satisfaction"] = np.random.choice([1, 2, 3, 4, 5], len(df), p=[0.05, 0.10, 0.20, 0.35, 0.30])

# Add some business events
business_events = ["Normal", "Product Launch", "Competitor Launch", "Economic Uncertainty", 
                  "Supply Disruption", "Marketing Campaign", "Price Promotion", "Holiday Season"]
event_probs = [0.70, 0.05, 0.05, 0.05, 0.03, 0.07, 0.03, 0.02]
df["business_event"] = np.random.choice(business_events, len(df), p=event_probs)

# Reorder columns for better readability
column_order = [
    "transaction_id", "date", "region", "product_line", "channel", "customer_segment",
    "budget_sales", "actual_sales", "sales_variance", "sales_variance_pct",
    "budget_volume", "actual_volume", "volume_variance",
    "budget_price", "actual_price", "price_variance", "discount_pct",
    "budget_marketing", "actual_marketing",
    "budget_cogs", "actual_cogs",
    "budget_labor", "actual_labor", 
    "budget_overhead", "actual_overhead",
    "sales_rep", "customer_satisfaction", "business_event"
]

df = df[column_order]

# Shuffle rows and reset index for more realistic data order
df = df.sample(frac=1, random_state=1).reset_index(drop=True)

# Show a sample
print(f"Generated comprehensive dataset with {len(df)} rows and {len(df.columns)} columns")
print(f"📅 Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
print("\n🔢 Key Metrics Summary:")
print(f"  • Average Daily Sales: ${df['actual_sales'].mean():,.0f}")
print(f"  • Total Sales Volume: {df['actual_volume'].sum():,} units")
print(f"  • Average Price: ${df['actual_price'].mean():.2f}")
print(f"  • Sales Variance Range: {df['sales_variance_pct'].min():.1f}% to {df['sales_variance_pct'].max():.1f}%")

print("\n📊 Sample data preview:")
print(df[['transaction_id', 'date', 'region', 'product_line', 'actual_sales', 'sales_variance_pct', 'business_event']].head(10))

# Save to CSV in sample_data directory
import os
os.makedirs("sample_data", exist_ok=True)
csv_path = os.path.join("sample_data", "comprehensive_sales_data.csv")
df.to_csv(csv_path, index=False)
print(f"\n✅ Enhanced dataset exported to: {csv_path}")

# Display detailed column information
print(f"\n� Complete Column Information:")
print("=" * 60)

# Group columns by category
budget_cols = [col for col in df.columns if col.startswith('budget_')]
actual_cols = [col for col in df.columns if col.startswith('actual_')]
variance_cols = [col for col in df.columns if 'variance' in col]
dimension_cols = ['region', 'product_line', 'channel', 'customer_segment', 'business_event', 'sales_rep']
other_cols = [col for col in df.columns if col not in budget_cols + actual_cols + variance_cols + dimension_cols]

print("\n🎯 BUDGET COLUMNS:")
for col in budget_cols:
    avg_val = df[col].mean()
    print(f"  • {col}: ${avg_val:,.0f} avg" if avg_val > 1000 else f"  • {col}: ${avg_val:.2f} avg")

print("\n� ACTUAL COLUMNS:")
for col in actual_cols:
    avg_val = df[col].mean()
    print(f"  • {col}: ${avg_val:,.0f} avg" if avg_val > 1000 else f"  • {col}: ${avg_val:.2f} avg")

print("\n📊 VARIANCE COLUMNS:")
for col in variance_cols:
    if df[col].dtype in ['int64', 'float64']:
        avg_val = df[col].mean()
        print(f"  • {col}: {avg_val:+.2f} avg")

print("\n🏷️ DIMENSION COLUMNS:")
for col in dimension_cols:
    unique_count = df[col].nunique()
    print(f"  • {col}: {unique_count} unique values")

print("\n🔧 OTHER COLUMNS:")
for col in other_cols:
    if df[col].dtype in ['int64', 'float64']:
        avg_val = df[col].mean()
        print(f"  • {col}: {avg_val:.2f} avg")
    else:
        print(f"  • {col}: {df[col].dtype}")

print(f"\n🎯 Perfect for testing LLM capabilities!")
print("=" * 60)
print("💡 Try these AI-powered questions:")
print("   • 'Analyze sales performance by region and product line'")
print("   • 'What factors are driving our sales variances?'")
print("   • 'Compare budget vs actual across all cost categories'")
print("   • 'Which sales reps are outperforming expectations?'")
print("   • 'How do business events impact our financial performance?'")
print("   • 'What's our pricing strategy effectiveness?'")
print("   • 'Identify patterns in customer satisfaction vs sales'")

print(f"\n📁 File location: {os.path.abspath(csv_path)}")