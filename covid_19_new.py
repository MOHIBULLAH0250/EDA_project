# ###########################
# # Include library
# ###########################

# import numpy as np 
# import pandas as pd
# import matplotlib.pyplot as plt 
# import seaborn as sns 
# from sklearn.pipeline import Pipeline,make_pipeline
# from sklearn.preprocessing import MinMaxScaler,StandardScaler
# from sklearn.impute import SimpleImputer
# from sklearn.model_selection import train_test_split
# from sklearn.compose import ColumnTransformer
# from sklearn.preprocessing import OneHotEncoder,OrdinalEncoder

# # =========================
# # STEP 1: LOAD DATA
# # =========================
# df = pd.read_csv("/home/ali/programing/EDA/time_series_covid19_confirmed_global.csv")
# print("Original Shape:", df.shape)
# print(df.head(5))
# # =========================
# # STEP 2: MELT (WIDE → LONG)
# # =========================
# df_long = df.melt(
#     id_vars=["Province/State", "Country/Region", "Lat", "Long"],
#     var_name="Date",
#     value_name="Cases"
# )

# print("After Melt:", df_long.shape)

# print(df_long.sample(5))


# ###########################
# # Load Dataset
# ###########################

# df = pd.read_csv(
#     "/home/ali/programing/EDA/covid19_long_format_filled.csv",
#     low_memory=False
# )

# ###########################
# # Missing Values Before Filling
# ###########################

# print("\nMissing Values Before Filling\n")

# print(df.isnull().sum())


# ###########################
# # Convert Cases to Numeric
# ###########################

# df["Cases"] = pd.to_numeric(
#     df["Cases"],
#     errors="coerce"
# )

# ###########################
# # Numerical Columns
# ###########################

# numerical_cols = [
#     "Lat",
#     "Long",
#     "Cases"
# ]

# ###########################
# # Categorical Columns
# ###########################

# categorical_cols = [
#     "Province/State",
#     "Country/Region",
#     "Date"
# ]

# ###########################
# # Numerical Missing Values Fill
# ###########################

# num_imputer = SimpleImputer(strategy="mean")

# df[numerical_cols] = num_imputer.fit_transform(
#     df[numerical_cols]
# )

# ###########################
# # Categorical Missing Values Fill
# ###########################

# cat_imputer = SimpleImputer(strategy="most_frequent")

# df[categorical_cols] = cat_imputer.fit_transform(
#     df[categorical_cols]
# )

# ###########################
# # Missing Values After Filling
# ###########################

# print("\nMissing Values After Filling\n")

# print(df.isnull().sum())




###########################################################
# 🌍 GLOBAL COVID-19 PROFESSIONAL DASHBOARD (FINAL VERSION)
###########################################################

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from ydata_profiling import ProfileReport

###########################################################
# PAGE CONFIG
###########################################################

st.set_page_config(
    page_title="COVID-19 Global Dashboard",
    page_icon="🦠",
    layout="wide"
)

###########################################################
# DARK THEME
###########################################################

st.markdown("""
<style>
.main { background-color: #0E1117; color: white; }
h1,h2,h3,h4 { color: white; }
[data-testid="stSidebar"] { background-color: #161A23; }
</style>
""", unsafe_allow_html=True)

st.title("🦠 GLOBAL COVID-19 ANALYTICS DASHBOARD")

###########################################################
# LOAD DATA
###########################################################

@st.cache_data
def load_data():
    df = pd.read_csv(
        "/home/ali/programing/EDA/covid_project/covid19_long_format_filled.csv",
        low_memory=False
    )
    return df

df = load_data()

###########################################################
# CLEANING
###########################################################

df["Cases"] = pd.to_numeric(df["Cases"], errors="coerce").fillna(0)
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

###########################################################
# SIDEBAR FILTERS
###########################################################

st.sidebar.header("🔍 Filters")

countries = sorted(df["Country/Region"].dropna().unique())

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    countries,
    default=["Pakistan", "India", "US"]
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["Date"].min(), df["Date"].max()]
)

###########################################################
# FILTERED DATA
###########################################################

filtered_df = df[
    (df["Country/Region"].isin(selected_countries)) &
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]

if filtered_df.empty:
    st.warning("No data found for selected filters")
    st.stop()

###########################################################
# KPI METRICS
###########################################################

col1, col2, col3 = st.columns(3)

col1.metric("🌍 Total Cases", f"{int(filtered_df['Cases'].sum()):,}")
col2.metric("🏳️ Countries", filtered_df["Country/Region"].nunique())
col3.metric("🏆 Top Country", filtered_df.groupby("Country/Region")["Cases"].sum().idxmax())

###########################################################
# 📈 TIME SERIES
###########################################################

st.subheader("📈 Global Trend Over Time")

ts = filtered_df.groupby("Date")["Cases"].sum().reset_index()

fig1 = px.line(ts, x="Date", y="Cases", markers=True,
               title="Global COVID Trend")

fig1.update_traces(
    mode="lines+markers",
    marker=dict(symbol="star", size=9),
    line=dict(width=3, color="#00FFCC")
)

st.plotly_chart(fig1, use_container_width=True)

st.info("This chart shows how total COVID-19 cases changed over time globally. It helps identify waves and peaks of the pandemic.")

###########################################################
# 🌍 COUNTRY COMPARISON
###########################################################

st.subheader("🌍 Country Comparison")

cc = filtered_df.groupby(["Date", "Country/Region"])["Cases"].sum().reset_index()

fig2 = px.line(cc, x="Date", y="Cases", color="Country/Region")

st.plotly_chart(fig2, use_container_width=True)

st.info("This visualization compares COVID-19 trends across selected countries, helping to analyze which countries were most affected over time.")

###########################################################
# 📊 TOP COUNTRIES
###########################################################

st.subheader("📊 Top Countries")

top = df.groupby("Country/Region")["Cases"].sum().reset_index().sort_values("Cases")

fig3 = px.bar(top, x="Cases", y="Country/Region",
              orientation="h", color="Cases",
              color_continuous_scale="Turbo")

st.plotly_chart(fig3, use_container_width=True)

st.info("This bar chart ranks countries based on total reported COVID-19 cases, highlighting the most impacted regions globally.")

###########################################################
# 🥧 PIE CHART
###########################################################

st.subheader("🥧 Global Share Distribution")

pie = df.groupby("Country/Region")["Cases"].sum().reset_index()

fig4 = px.pie(pie, names="Country/Region", values="Cases",
              hole=0.45, color_discrete_sequence=px.colors.qualitative.Bold)

st.plotly_chart(fig4, use_container_width=True)

st.info("This pie chart shows the percentage contribution of each country to total global COVID-19 cases.")

###########################################################
# 🗺️ WORLD MAP
###########################################################

st.subheader("🗺️ World Spread")

map_df = df.groupby(["Country/Region", "Lat", "Long"])["Cases"].sum().reset_index()

fig5 = px.scatter_geo(
    map_df,
    lat="Lat",
    lon="Long",
    size="Cases",
    color="Cases",
    hover_name="Country/Region",
    color_continuous_scale="Turbo"
)

st.plotly_chart(fig5, use_container_width=True)

st.info("This world map visualizes the geographical spread of COVID-19 cases across different countries.")

###########################################################
# 🌞 SUNBURST
###########################################################

st.subheader("🌞 Hierarchy View")

sun = filtered_df.copy()
sun["Province/State"] = sun["Province/State"].fillna("Unknown")

sun_data = sun.groupby(["Country/Region", "Province/State"])["Cases"].sum().reset_index()

fig6 = px.sunburst(
    sun_data,
    path=["Country/Region", "Province/State"],
    values="Cases",
    color="Cases",
    color_continuous_scale="RdBu"
)

st.plotly_chart(fig6, use_container_width=True)

st.info("This sunburst chart shows hierarchical distribution of cases from countries to provinces/states.")

###########################################################
# 🔥 HEATMAP
###########################################################

st.subheader("🔥 Heatmap")

corr = df[["Cases", "Lat", "Long"]].corr()

fig7 = px.imshow(corr, text_auto=True, color_continuous_scale="Viridis")

st.plotly_chart(fig7, use_container_width=True)

st.info("This heatmap shows correlation between cases and geographic coordinates (latitude and longitude).")

###########################################################
# 📅 MONTHLY
###########################################################

st.subheader("📅 Monthly Trend")

monthly = filtered_df.groupby(pd.Grouper(key="Date", freq="M"))["Cases"].sum().reset_index()

fig8 = px.area(monthly, x="Date", y="Cases", color_discrete_sequence=["#FF4B4B"])

st.plotly_chart(fig8, use_container_width=True)

st.info("This area chart shows monthly trends of COVID-19 cases, helping to identify long-term growth patterns.")

###########################################################
# 📊 DAILY
###########################################################

st.subheader("📊 Daily Cases")

daily = filtered_df.groupby("Date")["Cases"].sum().diff().reset_index()
daily.columns = ["Date", "Daily Cases"]
daily = daily.dropna()

fig9 = px.bar(daily, x="Date", y="Daily Cases", color="Daily Cases",
              color_continuous_scale="Turbo")

st.plotly_chart(fig9, use_container_width=True)

st.info("This chart shows daily new cases, helping to track short-term spikes and outbreaks.")

###########################################################
# ✨ SCATTER
###########################################################

st.subheader("✨ Scatter View")

scatter = df.groupby(["Country/Region", "Lat", "Long"])["Cases"].sum().reset_index()

fig10 = px.scatter(
    scatter,
    x="Lat",
    y="Long",
    size="Cases",
    color="Cases",
    hover_name="Country/Region",
    color_continuous_scale="Turbo"
)

st.plotly_chart(fig10, use_container_width=True)

st.info("This scatter plot shows global distribution of cases using latitude and longitude positions.")

###########################################################
# 📄 DATASET
###########################################################

st.subheader("📄 Dataset Preview (Colorful)")

st.dataframe(
    filtered_df.head(200).style.background_gradient(cmap="plasma"),
    use_container_width=True
)

st.info("This table shows a preview of the dataset with color gradients for better visual understanding.")

###########################################################
# 🤖 PANDAS PROFILING
###########################################################

st.subheader("🤖 Automated EDA Report")

if st.button("Generate Full EDA Report"):

    with st.spinner("Generating report..."):

        sample_df = filtered_df.sample(min(3000, len(filtered_df)))

        profile = ProfileReport(sample_df, explorative=True)

        profile.to_file("covid_report.html")

        with open("covid_report.html", "r", encoding="utf-8") as f:
            html = f.read()

        st.components.v1.html(html, height=1200, scrolling=True)

st.info("This automated report generates a full exploratory data analysis (EDA) including statistics, distributions, and correlations.")
