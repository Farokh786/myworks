import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import io
import seaborn as sns
import matplotlib.ticker as ticker

# --------------------------
# Responsive CSS for better display on all devices
# --------------------------
st.markdown(
    """
    <style>
    .dataframe, .stDataFrame div[data-testid="stTable"] > div {
        overflow-x: auto;
    }
    @media only screen and (max-width: 600px) {
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        .css-1v3fvcr {
            padding-left: 8px !important;
            padding-right: 8px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True
)

# --------------------------
# Project Overview
# --------------------------
st.set_page_config(page_title="iOutlet Education Expansion Dashboard", layout="wide")
st.title("The iOutlet Strategic Dashboard")
st.markdown("""
**Project Title:** *Maximising Impact: The iOutlet's Strategic Expansion in Education*

**Company:** The iOutlet  
**Website:** [theioutlet.com](https://www.theioutlet.com)

**Project Goal:**  
To develop a data-driven strategy for expanding refurbished tech sales in the education sector, based on analysis of sales trends, school segments, and regional opportunities.
""")

# --------------------------
# Load and Clean Data from SharePoint
# --------------------------
@st.cache_data
def load_data():
    file_url = "https://dmail-my.sharepoint.com/:x:/g/personal/2619506_dundee_ac_uk/ETLrFWlAs81NpHPN3_nhayEBVPVFauwk8jQCcwEt-cuv4Q?download=1"
    response = requests.get(file_url)
    bytes_io = io.BytesIO(response.content)
    sales_df = pd.read_excel(bytes_io, sheet_name="Sales")
    schools_df = pd.read_excel(bytes_io, sheet_name="Schools")

    # Clean column names
    sales_df.columns = sales_df.columns.str.strip().str.title()
    schools_df.columns = schools_df.columns.str.strip().str.title()

    # Clean important string columns to avoid KeyErrors and mismatches
    for col in ['School Match', 'Region', 'Trust Match']:
        if col in sales_df.columns:
            sales_df[col] = sales_df[col].astype(str).str.strip().str.title()

    # Convert order date
    sales_df['Order Date'] = pd.to_datetime(sales_df['Order Date'], errors='coerce', dayfirst=True)

    return sales_df, schools_df

sales_df, schools_df = load_data()
edu_df = sales_df[sales_df['School Match'].str.lower() != "no match"]

# --------------------------
# KPIs
# --------------------------
total_revenue = sales_df['Item Total'].sum()
edu_revenue = edu_df['Item Total'].sum()
total_units = sales_df['Quantity'].sum()
schools_reached = edu_df['School Match'].nunique()
repeat_orders = edu_df.groupby('School Match')['Order ID'].nunique()
repeat_order_rate = (repeat_orders[repeat_orders > 1].count() / schools_reached) * 100

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Total Revenue", f"£{total_revenue:,.2f}")
col2.metric("🎓 Education Revenue", f"£{edu_revenue:,.2f}")
col3.metric("📦 Units Sold", f"{int(total_units):,}")
col4.metric("🏫 Schools Reached", f"{schools_reached}")
col5.metric("⚖️ Repeat Orders %", f"{repeat_order_rate:.1f}%")

# ... rest of your dashboard code remains the same ...

# --------------------------
# Filters & Export
# --------------------------
st.sidebar.markdown("## 🔍 Filter Options")
region_filter = st.sidebar.selectbox("Select Region", options=['All'] + sorted(edu_df['Region'].dropna().unique()))
school_type_filter = st.sidebar.selectbox("Select School Type", options=['All'] + sorted(edu_df['School Type'].dropna().unique()))
trust_filter = st.sidebar.selectbox("Select Trust Match", options=['All'] + sorted(edu_df['Trust Match'].dropna().unique()))

filtered_df = edu_df.copy()
if region_filter != "All":
    filtered_df = filtered_df[filtered_df['Region'] == region_filter]
if school_type_filter != "All":
    filtered_df = filtered_df[filtered_df['School Type'] == school_type_filter]
if trust_filter != "All":
    filtered_df = filtered_df[filtered_df['Trust Match'] == trust_filter]

st.sidebar.metric("Filtered Sales", f"£{filtered_df['Item Total'].sum():,.2f}")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("⬇️ Download Filtered Data", csv, "filtered_education_sales.csv", "text/csv")
