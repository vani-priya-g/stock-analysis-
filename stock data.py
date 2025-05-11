import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Config and Styling
st.set_page_config(page_title="Stock Analysis Dashboard", layout="wide")

# Custom CSS for colorful sidebar
st.markdown("""
    <style>
        /* Sidebar background */
        [data-testid="stSidebar"] {
            background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
            color: #000000;
        }

        /* Sidebar radio and font styles */
        .css-1aumxhk, .css-16huue1 {
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }

        /* Sidebar header */
        .css-1d391kg {
            color: #d63384;
        }

        /* Container padding */
        div.block-container {
            padding-top: 2rem;
        }

        /* Remove 0 and broken image spacing */
        img {
            display: block;
            margin: auto;
        }
    </style>
""", unsafe_allow_html=True)

# Database connection
engine = create_engine("mysql+pymysql://root:Vani%401234567@127.0.0.1:3306/stock_analysis")

# Sidebar Navigation
st.sidebar.title("📌 Navigation")
selection = st.sidebar.radio("Go to", [
    "Home",
    "Volatility Analysis",
    "Cumulative Returns",
    "Sector Performance",
    "Stock Correlation",
    "Gainers & Losers"
])

# Page: Home
def home():
    st.title("📊 Stock Analysis Dashboard")
    st.markdown("""
        Welcome to your interactive dashboard to:
        - Analyze **stock trends** 📈  
        - Discover **top performers**  
        - Explore **volatility & correlation**  
        - Compare **sector-wise returns**

    
    """)

# Page: Volatility
def volatility_analysis():
    st.header("🔄 Top 10 Most Volatile Stocks")
    query = "SELECT * FROM volatility_analysis ORDER BY volatility DESC LIMIT 10"
    df = pd.read_sql(query, engine)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("📌 Most Volatile", df.iloc[0]["symbol"], f'{df.iloc[0]["volatility"]:.2f}')
        st.dataframe(df)
    with col2:
        fig = px.bar(df, x='symbol', y='volatility', color='volatility', text='volatility',
                     title="Top 10 Volatile Stocks", template='plotly_dark', color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)

# Page: Cumulative Return
def cumulative_return():
    st.header("📈 Top 5 Cumulative Returns Over Time")
    query = "SELECT * FROM cumulative_return"
    df = pd.read_sql(query, engine)

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        final_returns = df.groupby('symbol')['cumulative_return'].last().reset_index()
        top5_symbols = final_returns.sort_values(by='cumulative_return', ascending=False).head(5)['symbol']
        top5_df = df[df['symbol'].isin(top5_symbols)]

        fig = px.line(top5_df, x='date', y='cumulative_return', color='symbol',
                      title="Top 5 Stocks by Cumulative Return", template='plotly')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("❌ 'date' column not found in cumulative_return.")

# Page: Sector Performance
def sector_performance():
    st.header("🏭 Sector-wise Average Yearly Return")
    query = "SELECT sector, AVG(yearly_return) AS avg_return FROM sectorwise_performance GROUP BY sector"
    df = pd.read_sql(query, engine)

    st.subheader("📊 Sector Performance")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(df)
    with col2:
        fig = px.bar(df, x='sector', y='avg_return', color='avg_return', text='avg_return',
                     title="Sector-wise Avg Return", template='ggplot2', color_continuous_scale='Purples')
        st.plotly_chart(fig, use_container_width=True)

# Page: Correlation
def stock_correlation():
    st.header("📊 Stock Price Correlation Heatmap")
    query = "SELECT * FROM correlation_matrix"
    df = pd.read_sql(query, engine)

    fig, ax = plt.subplots(figsize=(25, 20))
    sns.heatmap(df.set_index("symbol"), cmap="coolwarm", annot=True, fmt=".2f", linewidths=0.5, ax=ax)
    st.pyplot(fig)

# Page: Gainers & Losers
def gainers_losers():
    st.header("📅 Monthly Gainers & Losers")

    months_query = "SELECT DISTINCT month FROM top_5_gainers"
    months = pd.read_sql(months_query, engine)["month"].tolist()
    selected_month = st.selectbox("Select a Month", months)

    gainers = pd.read_sql(f"SELECT * FROM top_5_gainers WHERE month = '{selected_month}'", engine)
    losers = pd.read_sql(f"SELECT * FROM top_5_losers WHERE month = '{selected_month}'", engine)

    # Gainers
    st.subheader("📈 Top 5 Gainers")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(gainers)
    with col2:
        fig_gain = px.bar(gainers, x='symbol', y='monthly_return', color='monthly_return', text='monthly_return',
                          title="Top Gainers", template='seaborn', color_continuous_scale='Greens')
        st.plotly_chart(fig_gain, use_container_width=True)

    # Losers
    st.subheader("📉 Top 5 Losers")
    col3, col4 = st.columns([1, 2])
    with col3:
        st.dataframe(losers)
    with col4:
        fig_lose = px.bar(losers, x='symbol', y='monthly_return', color='monthly_return', text='monthly_return',
                          title="Top Losers", template='seaborn', color_continuous_scale='Reds')
        st.plotly_chart(fig_lose, use_container_width=True)

# Routing
pages = {
    "Home": home,
    "Volatility Analysis": volatility_analysis,
    "Cumulative Returns": cumulative_return,
    "Sector Performance": sector_performance,
    "Stock Correlation": stock_correlation,
    "Gainers & Losers": gainers_losers
}
pages[selection]()
