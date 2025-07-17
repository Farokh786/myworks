import streamlit as st
import pandas as pd
import requests
import io
import matplotlib.pyplot as plt

# --------------------------
# Page Setup
# --------------------------
st.set_page_config(page_title="The iOutlet Education Dashboard", layout="wide")
st.title("📊 The iOutlet Education Sector Dashboard")

# --------------------------
# Load Data
# --------------------------
@st.cache_data
def load_data():
    file_url = "https://dmail-my.sharepoint.com/:x:/g/personal/2619506_dundee_ac_uk/ETLrFWlAs81NpHPN3_nhayEBVPVFauwk8jQCcwEt-cuv4Q?download=1"
    response = requests.get(file_url)
    bytes_io = io.BytesIO(response.content)
    sales_df = pd.read_excel(bytes_io, sheet_name="Sales")
    schools_df = pd.read_excel(bytes_io, sheet_name="Schools")
    
    # Preprocess
    sales_df.columns = sales_df.columns.str.strip()
    sales_df['Order Date'] = pd.to_datetime(sales_df['Order Date'], errors='coerce', dayfirst=True)
    sales_df['Region'] = sales_df['Region'].astype(str).str.strip().str.title()
    sales_df['School Type'] = sales_df['School Type'].astype(str).str.strip().str.title()
    sales_df['Trust Matched'] = sales_df['Trust Matched'].astype(str).str.strip().str.title()

    return sales_df, schools_df

sales_df, schools_df = load_data()

# --------------------------
# Sidebar Filters
# --------------------------
st.sidebar.header("🔍 Filter by")

# Region Filter
region_options = sorted(sales_df['Region'].dropna().unique())
selected_region = st.sidebar.selectbox("Select Region", options=["All"] + region_options)

# School Type Filter
school_type_options = sorted(sales_df['School Type'].dropna().unique())
selected_type = st.sidebar.selectbox("Select School Type", options=["All"] + school_type_options)

# Trust Matched Filter
trust_options = sorted(sales_df['Trust Matched'].dropna().unique())
selected_trust = st.sidebar.selectbox("Select Trust Matched", options=["All"] + trust_options)

# --------------------------
# Filter Logic
# --------------------------
filtered_df = sales_df.copy()

if selected_region != "All":
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]

if selected_type != "All":
    filtered_df = filtered_df[filtered_df['School Type'] == selected_type]

if selected_trust != "All":
    filtered_df = filtered_df[filtered_df['Trust Matched'] == selected_trust]

edu_df = filtered_df[filtered_df['School Match'].str.lower() != "no match"]

# --------------------------
# KPIs
# --------------------------
total_revenue = filtered_df['Item Total'].sum()
edu_revenue = edu_df['Item Total'].sum()
total_units = filtered_df['Quantity'].sum()
schools_reached = edu_df['School Match'].nunique()
repeat_orders = edu_df.groupby('School Match')['Order ID'].nunique()
repeat_order_rate = (repeat_orders[repeat_orders > 1].count() / schools_reached * 100) if schools_reached > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Total Revenue", f"£{total_revenue:,.2f}")
col2.metric("🎓 Education Revenue", f"£{edu_revenue:,.2f}")
col3.metric("📦 Units Sold", f"{int(total_units):,}")
col4.metric("🏫 Schools Reached", f"{schools_reached}")
col5.metric("🔁 Repeat Order Rate", f"{repeat_order_rate:.1f}%")

# --------------------------
# Optional Visualization Placeholder
# --------------------------
st.subheader("📈 Sales Data Preview")
st.dataframe(filtered_df.head(20))

