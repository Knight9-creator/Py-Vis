import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. PAGE CONFIG
st.set_page_config(page_title="Game Industry KPI Dashboard", layout="wide")

st.title("Video Game Market Analysis Dashboard")
st.write("Exploring demand, performance, risk, and feasibility across game genres.")

# 2. LOAD DATA
def load_data():
    df = pd.read_csv('video_games_sales.csv')
    df.columns = df.columns.str.strip().str.lower()
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Couldn't find 'video_games_sales.csv'.")
    st.stop()


# 3. KPI LOGIC
genre_counts = df['genre'].value_counts()
total_games = len(df)
market_share = (genre_counts / total_games * 100).round(2)
avg_sales = df.groupby('genre')['global_sales'].mean().round(2)
hits = df[df['global_sales'] > 1.0].groupby('genre').size()
total_genre_games = df.groupby('genre').size()
hit_rate = ((hits / total_genre_games).fillna(0) * 100).round(2)

complexity_scores = {
    'Action': 4, 'Adventure': 3, 'Fighting': 4, 'Misc': 2, 'Platform': 2, 
    'Puzzle': 1, 'Racing': 3, 'Role-Playing': 5, 'Shooter': 3, 
    'Simulation': 3, 'Sports': 3, 'Strategy': 4
}

# Combine into a single KPI Table
kpi_table = pd.DataFrame({
    'Market Share (%)': market_share,
    'Avg Sales (M)': avg_sales,
    'Hit Rate (%)': hit_rate,
    'Complexity (1-5)': pd.Series(complexity_scores)
}).fillna(3)


# 4. DASHBOARD LAYOUT

# Top Row: High-Level Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Titles", f"{total_games:,}")
col2.metric("Best Seller (Avg)", f"{avg_sales.idxmax()}", f"{avg_sales.max()}M")
col3.metric("Highest Hit Rate", f"{hit_rate.idxmax()}", f"{hit_rate.max()}%")
col4.metric("Market Leader", f"{genre_counts.idxmax()}", f"{market_share.max()}% Share")
st.divider()

# Middle Row: The Charts
left_chart, right_chart = st.columns(2)
with left_chart:
    st.subheader("Performance: Avg Sales by Genre")
    fig1, ax1 = plt.subplots()
    avg_sales.sort_values(ascending=False).plot(kind='bar', color='skyblue', edgecolor='black', ax=ax1)
    ax1.set_ylabel("Global Sales (Millions)")
    st.pyplot(fig1)

with right_chart:
    st.subheader("Saturation: Number of Games")
    fig2, ax2 = plt.subplots()
    genre_counts.sort_values(ascending=False).plot(kind='bar', color='salmon', edgecolor='black', ax=ax2)
    ax2.set_ylabel("Titles Released")
    st.pyplot(fig2)

# Bottom Row: The Data Table
st.divider()
st.subheader("Genre Breakdown Deep-Dive")
st.dataframe(kpi_table.style.background_gradient(cmap='Blues'), use_container_width=True)

# Sidebar Filter (Bonus)
st.sidebar.header("Filter Results")
selected_genre = st.sidebar.multiselect("Select Genres to Compare", options=kpi_table.index.tolist(), default=kpi_table.index.tolist())