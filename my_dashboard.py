
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

# --------------------------
# Project Overview
# --------------------------
st.set_page_config(page_title="iOutlet Education Expansion Dashboard", layout="wide")
st.title("The iOutlet Strategic Dashboard")
st.markdown("""
**Project Title:** *Maximising Impact: The iOutlet's Strategic Expansion in Education*

**Company:** The iOutlet  
**Contact Person:** Russell Jones  
**Location:** Unit 37A Sisna Park, Estover, Plymouth, PL6 7FH  
**Email:** russell@theioutlet.com  
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
    sales_df.columns = sales_df.columns.str.strip()
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

# --------------------------
# Monthly Sales Trends
# --------------------------
st.markdown("### 📈 Monthly Sales Trends")
monthly_sales = sales_df.resample('MS', on='Order Date')['Item Total'].sum()
monthly_edu = edu_df.resample('MS', on='Order Date')['Item Total'].sum()

fig1, ax1 = plt.subplots()
ax1.plot(monthly_sales.index, monthly_sales.values, label='All Sales', marker='o')
ax1.plot(monthly_edu.index, monthly_edu.values, label='Education Sales', marker='s')
ax1.set_title("Monthly Revenue")
ax1.set_ylabel("£")
ax1.legend()
ax1.grid(True)
st.pyplot(fig1)

# --------------------------
# School Segmentation
# --------------------------
st.markdown("### 🏫 Orders by School Type and Region")
school_types = edu_df["School Type"].dropna().value_counts()
regions = edu_df["Region"].dropna().value_counts()

colA, colB = st.columns(2)
with colA:
    fig2, ax2 = plt.subplots()
    school_types.plot(kind='bar', color='dodgerblue', ax=ax2)
    ax2.set_title("Orders by School Type")
    st.pyplot(fig2)

with colB:
    fig3, ax3 = plt.subplots()
    regions.plot(kind='pie', autopct='%1.1f%%', ax=ax3)
    ax3.set_title("Orders by Region")
    ax3.axis('equal')
    st.pyplot(fig3)

# --------------------------
# Regional Sales Insights
# --------------------------
st.markdown("### 🌍 Regional Sales Breakdown")
region_sales = edu_df.groupby('Region')['Item Total'].sum().sort_values(ascending=False)
top_schools = edu_df.groupby('School Match')['Item Total'].sum().sort_values(ascending=False).head(10)

st.bar_chart(region_sales)
st.markdown("**Top 10 Schools by Revenue:**")
st.dataframe(top_schools)

# --------------------------
# Product Insights
# --------------------------
st.markdown("### 📦 Top Items Sold in Education Sector")
top_items = edu_df.groupby("Item Type")["Quantity"].sum().sort_values(ascending=False)

fig4, ax4 = plt.subplots()
top_items.plot(kind='bar', color='seagreen', ax=ax4)
ax4.set_ylabel("Units")
ax4.set_title("Top Item Types Sold")
st.pyplot(fig4)

# --------------------------
# Strategic Recommendations
# --------------------------
st.markdown("### Strategic Recommendations")
st.markdown("""
- Focus marketing efforts on **Academies** and **Secondary Schools**.
- Prioritize high-performing regions like **London**, **West Midlands**, and **North West**.
- Bundle deals for iPads and MacBooks aimed at school tech refresh cycles.
- Implement loyalty programs to improve repeat orders from existing schools.
- Align offerings with sustainability and cost-efficiency goals in education procurement.
""")

# --------------------------
# Filters & Export
# --------------------------
st.sidebar.markdown("## 🔍 Filter Options")
region_filter = st.sidebar.selectbox("Select Region", options=['All'] + sorted(edu_df['Region'].dropna().unique()))
school_type_filter = st.sidebar.selectbox("Select School Type", options=['All'] + sorted(edu_df['School Type'].dropna().unique()))

filtered_df = edu_df.copy()
if region_filter != "All":
    filtered_df = filtered_df[filtered_df['Region'] == region_filter]
if school_type_filter != "All":
    filtered_df = filtered_df[filtered_df['School Type'] == school_type_filter]

st.sidebar.metric("Filtered Sales", f"£{filtered_df['Item Total'].sum():,.2f}")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("⬇️ Download Filtered Data", csv, "filtered_education_sales.csv", "text/csv")
