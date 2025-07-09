import dash
import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="iOutlet Education Sales Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    file_path = r"E:\MSc Business Analytics & Finance Jan25\Business Analytics Project\iOutlet_Internship\Clean_data\Merged_Data3.xlsx"
    sales_df = pd.read_excel(file_path, sheet_name="Sales")
    schools_df = pd.read_excel(file_path, sheet_name="Schools")
    sales_df.columns = sales_df.columns.str.strip()
    sales_df['Order Date'] = pd.to_datetime(sales_df['Order Date'], dayfirst=True, errors='coerce')
    return sales_df, schools_df

sales_df, schools_df = load_data()

# FILTER: Education Sector
edu_df = sales_df[sales_df['School Match'].str.lower() != "no match"]

# METRICS
total_revenue = sales_df['Item Total'].sum()
total_units = sales_df['Quantity'].sum()
edu_revenue = edu_df['Item Total'].sum()
edu_units = edu_df['Quantity'].sum()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Revenue", f"£{total_revenue:,.2f}")
col2.metric("🎓 Education Revenue", f"£{edu_revenue:,.2f}")
col3.metric("📦 Units Sold", f"{int(total_units):,}")

# Monthly Trends
st.markdown("### 📈 Monthly Sales Trends")
monthly_sales = sales_df.resample('MS', on='Order Date')['Item Total'].sum()
monthly_edu = edu_df.resample('MS', on='Order Date')['Item Total'].sum()

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(monthly_sales.index, monthly_sales.values, label="All Sales", marker='o')
ax.plot(monthly_edu.index, monthly_edu.values, label="Education Sector", marker='s')
ax.set_title("Monthly Sales Revenue")
ax.set_ylabel("Revenue (£)")
ax.set_xlabel("Month")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Product Sales by Type
st.markdown("### 🧾 Top Item Types Sold")
top_items = sales_df.groupby("Item Type")["Quantity"].sum().sort_values(ascending=False)

fig2, ax2 = plt.subplots()
top_items.plot(kind='bar', color='cornflowerblue', ax=ax2)
ax2.set_ylabel("Quantity Sold")
ax2.set_title("Units Sold by Item Type")
st.pyplot(fig2)

# Region-wise Sales
st.markdown("### 🌍 Regional Sales (Education Sector)")
edu_region_sales = edu_df.groupby("Region")["Item Total"].sum().sort_values(ascending=False)

fig3, ax3 = plt.subplots()
edu_region_sales.plot(kind='bar', color='seagreen', ax=ax3)
ax3.set_ylabel("Revenue (£)")
ax3.set_title("Education Sector Sales by Region")
st.pyplot(fig3)

# School Types
st.markdown("### 🏫 School Types Ordered")
school_types = edu_df["School Type"].dropna().value_counts()

fig4, ax4 = plt.subplots()
school_types.plot(kind='bar', color='orange', ax=ax4)
ax4.set_title("Orders by School Type")
ax4.set_ylabel("Number of Orders")
st.pyplot(fig4)

# Top Customers
st.markdown("### 👥 Top Customers in Education Sector")
top_customers = edu_df['Customer Name'].value_counts().head(5)

fig5, ax5 = plt.subplots()
top_customers.plot(kind='barh', color='teal', ax=ax5)
ax5.set_xlabel("Number of Purchases")
ax5.set_title("Top 5 Education Customers")
st.pyplot(fig5)

# Schools by Region
st.markdown("### 📚 Schools by Region")
region_counts = schools_df['Region'].astype(str).str.strip().value_counts()

fig6, ax6 = plt.subplots()
region_counts.plot(kind='barh', color='purple', ax=ax6)
ax6.set_xlabel("Number of Schools")
ax6.set_title("Number of Schools per Region")
st.pyplot(fig6)

# Clustering Segments (Optional if you've run KMeans)
st.markdown("### 🔍 Customer Segmentation (Cluster Summary)")
cluster_summary = pd.DataFrame({
    "Segment": ["High-Value Loyal Customers", "Mid-Value Repeat Buyers", "Low-Value Occasional Buyers"],
    "Avg Spend (£)": [715.13, 660.96, 259.65],
    "Order Freq": [2.61, 1.83, 1.0],
    "Regions Reached": [2.14, 1.0, 1.0]
})
st.dataframe(cluster_summary)

# Optional Filters
st.sidebar.markdown("## 🔎 Filters")
selected_region = st.sidebar.selectbox("Select Region", options=["All"] + list(sales_df['Region'].dropna().unique()))
if selected_region != "All":
    filtered = edu_df[edu_df['Region'] == selected_region]
    st.sidebar.metric("Filtered Region Sales", f"£{filtered['Item Total'].sum():,.2f}")
