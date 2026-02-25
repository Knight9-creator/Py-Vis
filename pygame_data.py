import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. LOAD THE DATA
# ---------------------------------------------------------
df = pd.read_csv('video_games_sales.csv')

# Clean column names (strip spaces + lowercase)
df.columns = df.columns.str.strip().str.lower()

# ---------------------------------------------------------
# ✅ MC-01: COLUMN RENAME PROTECTION
# ---------------------------------------------------------
# If mutation renamed global_sales → global_sales_millions
if 'global_sales_millions' in df.columns:
    df = df.rename(columns={'global_sales_millions': 'global_sales'})

# ---------------------------------------------------------
# ✅ MC-02: HANDLE MISSING VALUES
# ---------------------------------------------------------
print("\nMissing values BEFORE cleaning:")
print(df[['genre', 'global_sales']].isna().sum())

# Fill missing sales with 0 (safe for KPIs)
df['global_sales'] = df['global_sales'].fillna(0)

# Fill missing genres with 'Unknown'
df['genre'] = df['genre'].fillna('Unknown')

print("\nMissing values AFTER cleaning:")
print(df[['genre', 'global_sales']].isna().sum())

# ---------------------------------------------------------
# ✅ MC-03: REMOVE DUPLICATE ROWS
# ---------------------------------------------------------
before_count = len(df)

df = df.drop_duplicates()

after_count = len(df)

print(f"\nRows BEFORE deduplication: {before_count}")
print(f"Rows AFTER deduplication: {after_count}")

# ---------------------------------------------------------
# PART 1: COMPUTE KPIs
# ---------------------------------------------------------

# KPI 1: Market Share (% of total games)
genre_counts = df['genre'].value_counts()
total_games = len(df)
market_share = (genre_counts / total_games * 100).round(2)

# KPI 2: Average Global Sales (Performance)
avg_sales = df.groupby('genre')['global_sales'].mean().round(2)

# KPI 3: Hit Rate (>1 Million Copies)
hits = df[df['global_sales'] > 1.0].groupby('genre').size()
total_genre_games = df.groupby('genre').size()
hit_rate = ((hits / total_genre_games).fillna(0) * 100).round(2)

# KPI 4: Feasibility (Manual Complexity Score)
complexity_scores = {
    'Action': 4, 'Adventure': 3, 'Fighting': 4, 'Misc': 2,
    'Platform': 2, 'Puzzle': 1, 'Racing': 3,
    'Role-Playing': 5, 'Shooter': 3,
    'Simulation': 3, 'Sports': 3, 'Strategy': 4,
    'Unknown': 3
}

# Combine KPIs
kpi_table = pd.DataFrame({
    'Market Share (%)': market_share,
    'Avg Sales (Millions)': avg_sales,
    'Hit Rate (>1M %)': hit_rate
})

kpi_table['Complexity (1-5)'] = (
    kpi_table.index.map(complexity_scores).fillna(3)
)

print("\n--- KPI DATA FOR YOUR WORKSHEET ---")
print(kpi_table)

# ---------------------------------------------------------
# PART 2: VISUALIZE RESULTS
# ---------------------------------------------------------

# Chart 1: Average Sales by Genre
plt.figure(figsize=(12, 6))
avg_sales.sort_values(ascending=False).plot(
    kind='bar', color='skyblue', edgecolor='black'
)
plt.title('Average Global Sales by Genre (Performance)')
plt.ylabel('Global Sales (Millions)')
plt.xlabel('Genre')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('chart1_avg_sales.png')
plt.show()

# Chart 2: Market Saturation
plt.figure(figsize=(12, 6))
genre_counts.sort_values(ascending=False).plot(
    kind='bar', color='salmon', edgecolor='black'
)
plt.title('Market Saturation: Number of Games by Genre')
plt.ylabel('Number of Titles Released')
plt.xlabel('Genre')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('chart2_saturation.png')
plt.show()