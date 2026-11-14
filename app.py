
import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry
from sqlalchemy import create_engine, URL, text, bindparam

# 1. PAGE SETTINGS

st.set_page_config(
    page_title="Global GDP Analytics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. DESIGN AND STYLING

st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
}

.block-container {
    max-width: 100%;
    padding: 1.2rem 1.5rem 0.5rem 1.5rem;
}

h1 {
    font-size: 2.3rem !important;
    color: #ffffff !important;
    margin-top: 0.5rem !important;
    margin-bottom: 0.4rem !important;
    line-height: 1.3 !important;
}

h2 {
    font-size: 1.65rem !important;
    color: #ffffff !important;
}

h3 {
    font-size: 1.35rem !important;
    color: #ffffff !important;
}

p, label, [data-testid="stMarkdownContainer"] {
    font-size: 1rem;
}

[data-testid="stMetric"] {
    background: #1b2738;
    border: 1px solid #354861;
    border-radius: 12px;
    padding: 16px;
    min-height: 120px;
}

[data-testid="stMetricLabel"] {
    color: #c0cede !important;
    font-size: 1rem !important;
}

[data-testid="stMetricValue"] {
    color: white !important;
    font-size: clamp(1.4rem, 2vw, 2rem) !important;
    font-weight: 700 !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.95rem !important;
}

[data-testid="stTabs"] button {
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    padding: 0.6rem !important;
}

[data-testid="stCaptionContainer"] {
    font-size: 0.95rem !important;
    color: #b0bdce !important;
}

hr {
    border-color: #354052 !important;
    margin: 0.7rem 0 !important;
}
</style>
""", unsafe_allow_html=True)


# 3. LOAD DATA FROM POSTGRESQL

@st.cache_resource
@st.cache_resource
def get_engine():
    database_url = st.secrets["postgres"]["url"]

    database_url = database_url.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )

    return create_engine(database_url)


@st.cache_data
def load_data():
    query = text("""
        SELECT
            "Country Name",
            "Country Code",
            "Year",
            "GDP"
        FROM gdp_data
    """)

    with get_engine().connect() as connection:
        df = pd.read_sql(query, connection)

    return df


df = load_data()


# 4. HELPER FUNCTION

def format_gdp(value):

    if value >= 1_000_000_000_000:
        return f"${value / 1e12:.2f}T"

    if value >= 1_000_000_000:
        return f"${value / 1e9:.2f}B"

    return f"${value / 1e6:.2f}M"


# 5. GET DATA

try:
    gdp_df = load_data()
except Exception as e:
    st.error(f"Unable to load data: {e}")
    st.stop()

if gdp_df.empty:
    st.error("No valid GDP data found.")
    st.stop()


# 6. DASHBOARD TITLE

st.title("🌍 Global GDP Analytics Dashboard")
st.divider()


# 7. FILTERS

st.subheader("Dashboard Filters")

min_year = int(gdp_df["Year"].min())
max_year = int(gdp_df["Year"].max())

countries = sorted(gdp_df["Country Name"].unique())

defaults = [
    c for c in ["India", "United States", "China", "Japan", "Germany"]
    if c in countries
]

col1, col2 = st.columns([1, 3])

with col1:
    from_year, to_year = st.select_slider(
        "Select year range",
        options=list(range(min_year, max_year + 1)),
        value=(min_year, max_year)
    )

with col2:
    selected = st.multiselect(
        "Select countries",
        countries,
        default=defaults
    )

if not selected:
    st.warning("Please select at least one country.")
    st.stop()


# 8. FILTER DATA

data = gdp_df[
    (gdp_df["Country Name"].isin(selected))
    & (gdp_df["Year"].between(from_year, to_year))
].copy()

if data.empty:
    st.warning("No data available for these filters.")
    st.stop()

# Find a common latest year for fair comparison
latest_year = int(
    data.groupby("Country Name")["Year"].max().min()
)

latest = data[data["Year"] == latest_year].copy()

if latest.empty:
    st.warning("No comparable GDP records found.")
    st.stop()


# 9. KPI CALCULATIONS

total_gdp = latest["GDP"].sum()

highest = latest.loc[latest["GDP"].idxmax()]
lowest = latest.loc[latest["GDP"].idxmin()]

start = data[data["Year"] == from_year][
    ["Country Name", "GDP"]
]

end = latest[["Country Name", "GDP"]]

growth_data = start.merge(
    end,
    on="Country Name",
    suffixes=("_start", "_end")
)

growth = "N/A"

if from_year < latest_year and not growth_data.empty:

    start_total = growth_data["GDP_start"].sum()
    end_total = growth_data["GDP_end"].sum()

    if start_total > 0:
        years = latest_year - from_year

        cagr = (
            (end_total / start_total) ** (1 / years) - 1
        ) * 100

        growth = f"{cagr:+.2f}%"


# 10. KPI CARDS

st.subheader("📊 Economic Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total GDP", format_gdp(total_gdp))

c2.metric(
    "Annualized GDP Growth",
    growth,
    delta_color="off"
)

c3.metric(
    "Highest GDP Country",
    highest["Country Name"],
    format_gdp(highest["GDP"]),
    delta_color="off"
)

c4.metric(
    "Lowest GDP Country",
    lowest["Country Name"],
    format_gdp(lowest["GDP"]),
    delta_color="off"
)

st.caption(
    f"GDP in current US dollars | Comparison year: {latest_year}"
)

st.divider()


# 11. DASHBOARD TABS

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "📈 GDP Trends",
    "🌍 World Map",
    "📋 Data Explorer",
    "📉 SQL Insights"
])

# TAB 1: OVERVIEW

with tab1:

    chart1, chart2 = st.columns(2)

    with chart1:

        st.subheader("🏆 Country Comparison")

        bar = px.bar(
            latest.sort_values("GDP"),
            x="GDP",
            y="Country Name",
            orientation="h",
            color="GDP",
            color_continuous_scale="Blues",
            title=f"GDP by Country - {latest_year}",
            template="plotly_dark",
            labels={
                "GDP": "GDP (US$)",
                "Country Name": "Country"
            }
        )

        bar.update_layout(
            height=330,
            font=dict(size=14),
            coloraxis_showscale=False,
            margin=dict(l=10, r=25, t=50, b=30),
            xaxis_tickformat="~s"
        )

        st.plotly_chart(bar, use_container_width=True)

    with chart2:

        st.subheader("📈 GDP Trends")

        line = px.line(
            data,
            x="Year",
            y="GDP",
            color="Country Name",
            title="GDP Over Time",
            template="plotly_dark",
            labels={"GDP": "GDP (US$)"}
        )

        line.update_layout(
            height=330,
            font=dict(size=14),
            margin=dict(l=10, r=10, t=50, b=30),
            hovermode="x unified",
            yaxis_tickformat="~s",
            legend=dict(
                orientation="h",
                y=-0.25
            )
        )

        st.plotly_chart(line, use_container_width=True)


# TAB 2: GDP TRENDS

with tab2:

    st.subheader("Historical GDP Analysis")

    trend = px.line(
        data,
        x="Year",
        y="GDP",
        color="Country Name",
        markers=True,
        template="plotly_dark",
        title="GDP Trends Across Selected Countries"
    )

    trend.update_layout(
        height=480,
        font=dict(size=15),
        hovermode="x unified",
        yaxis_tickformat="~s"
    )

    st.plotly_chart(trend, use_container_width=True)

    st.info("GDP is measured in current US dollars and is not adjusted for inflation.")


# TAB 3: WORLD MAP

with tab3:

    st.subheader("🌍 Global GDP Distribution")

    map_year = to_year

    map_data = gdp_df[gdp_df["Year"] == map_year].copy()

    valid_codes = {
        country.alpha_3 for country in pycountry.countries
    }

    map_data = map_data[
        map_data["Country Code"].isin(valid_codes)
    ]

    if map_data.empty:
        st.warning("No map data available for this year.")

    else:

        world_map = px.choropleth(
            map_data,
            locations="Country Code",
            locationmode="ISO-3",
            color="GDP",
            hover_name="Country Name",
            hover_data={"GDP": ":,.0f"},
            color_continuous_scale="Viridis",
            projection="natural earth",
            template="plotly_dark",
            title=f"World GDP Map - {map_year}"
        )

        world_map.update_layout(
            height=520,
            font=dict(size=14),
            margin=dict(l=0, r=0, t=50, b=0)
        )

        st.plotly_chart(world_map, use_container_width=True)

    st.caption("Map shows all available countries, not just selected countries.")


# TAB 4: DATA EXPLORER

with tab4:

    st.subheader("📋 GDP Data Explorer")

    st.write(f"Total records: {len(data):,}")

    st.dataframe(
        data.sort_values(["Country Name", "Year"]),
        use_container_width=True,
        height=420,
        hide_index=True,
        column_config={
            "GDP": st.column_config.NumberColumn(
                "GDP (Current US$)",
                format="$%.0f"
            )
        }
    )

    st.download_button(
        "⬇️ Download GDP Data",
        data=data.to_csv(index=False),
        file_name="GDP_data.csv",
        mime="text/csv"
    )

# TAB 5: SQL INSIGHTS

with tab5:

    st.subheader("📉 SQL-Based Economic Analysis")

    query = text("""
        WITH country_gdp AS (
            SELECT
                "Country Name",
                "Year",
                "GDP",
                LAG("GDP") OVER (
                    PARTITION BY "Country Name"
                    ORDER BY "Year"
                ) AS previous_gdp
            FROM gdp_data
            WHERE "Country Name" IN :countries
        )

        SELECT
            "Country Name",
            "Year",
            ROUND(("GDP" / 1000000000000.0)::numeric, 2)
                AS "GDP (Trillion USD)",
            ROUND(
                ((("GDP" - previous_gdp) / previous_gdp) * 100)::numeric,
                2
            ) AS "GDP Growth (%)"
        FROM country_gdp
        WHERE previous_gdp IS NOT NULL
          AND "Year" BETWEEN :from_year AND :to_year
        ORDER BY "Country Name", "Year" DESC
    """).bindparams(
        bindparam("countries", expanding=True)
    )

    with get_engine().connect() as connection:
        sql_data = pd.read_sql(
            query,
            connection,
            params={
                "countries": selected,
                "from_year": from_year,
                "to_year": to_year
            }
        )

        st.caption("Annual GDP growth calculated using the SQL LAG() window function.")

    st.dataframe(
        sql_data,
        use_container_width=True,
        hide_index=True
    )

    # GDP Growth Comparison Chart
    st.divider()

    st.subheader("📈 Annual GDP Growth Comparison")

    growth_chart = px.line(
        sql_data,
        x="Year",
        y="GDP Growth (%)",
        color="Country Name",
        markers=True,
        template="plotly_dark",
        title="Year-over-Year GDP Growth"
    )

    growth_chart.update_layout(
        height=450,
        font=dict(size=14),
        hovermode="x unified",
        yaxis_title="GDP Growth (%)",
        xaxis_title="Year"
    )

    st.plotly_chart(
        growth_chart,
        use_container_width=True
    )
        

# 12. FOOTER

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#b0bdce; font-size:15px;">
        <b>Global GDP Analytics Dashboard</b><br>
        Built using Python | Pandas | Plotly | Streamlit<br>
        Source: World Bank Open Data
    </div>
    """,
    unsafe_allow_html=True
)
