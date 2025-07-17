import streamlit as st
import pandas as pd
import altair as alt

# Page setup
st.set_page_config(page_title="LA Airbnb Dashboard", layout="wide")

st.title("📊 LA Airbnb Data Dashboard")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("listings(1).csv.gz", compression="gzip")
    df['price'] = df['price'].replace(r'[\$,]', '', regex=True).astype(float)
    df_clean = df[[
        'price', 'review_scores_rating', 'number_of_reviews',
        'room_type', 'neighbourhood_cleansed', 'availability_365'
    ]].dropna()
    df_clean = df_clean[df_clean['price'] <= 1000]
    if len(df_clean) > 5000:
        df_clean = df_clean.sample(5000, random_state=1)
    return df_clean

df_clean = load_data()

# Optional filter
room_filter = st.multiselect("Filter by Room Type", df_clean['room_type'].unique(), default=df_clean['room_type'].unique())

filtered_df = df_clean[df_clean['room_type'].isin(room_filter)]

# 1. Price vs Review Scores
scatter = alt.Chart(filtered_df).mark_circle(opacity=0.6).encode(
    x=alt.X('price:Q', title='Price'),
    y=alt.Y('review_scores_rating:Q', title='Review Score Rating'),
    color=alt.Color('room_type:N', title='Room Type'),
    tooltip=['room_type', 'price', 'review_scores_rating']
).properties(
    title='Price vs Review Scores in LA',
    width=600,
    height=400
)

# 2. Boxplot of Price by Neighborhood
top20 = filtered_df['neighbourhood_cleansed'].value_counts().nlargest(20).index
df_top20 = filtered_df[filtered_df['neighbourhood_cleansed'].isin(top20)]

boxplot = alt.Chart(df_top20).mark_boxplot().encode(
    y=alt.Y('neighbourhood_cleansed:N', sort='-x', title='Neighborhood'),
    x=alt.X('price:Q', title='Price (USD)')
).properties(
    title='Price Distribution in Top 20 LA Neighborhoods',
    width=600,
    height=500
)

# 3. Histogram of Availability
hist = alt.Chart(filtered_df).mark_bar().encode(
    x=alt.X('availability_365:Q', bin=alt.Bin(maxbins=30), title='Days Available per Year'),
    y=alt.Y('count():Q', title='Number of Listings')
).properties(
    title='Availability of Listings Across the Year in LA',
    width=600,
    height=400
)

# Layout
col1, col2 = st.columns(2)
with col1:
    st.altair_chart(scatter, use_container_width=True)
with col2:
    st.altair_chart(hist, use_container_width=True)

st.altair_chart(boxplot, use_container_width=True)

