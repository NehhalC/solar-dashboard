import streamlit as st
import pandas as pd
import plotly.express as px

from analytics import (
    load_all_sites,
    monthly_energy_by_site,
    hourly_average_power,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Solar Power Analytics Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       MAIN APP
       ======================================================== */

    .stApp {
        background-color: #F7F9FC;
    }

    .main {
        background-color: #F7F9FC;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background-color: #172033;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }


    /* ========================================================
       DASHBOARD TITLE
       ======================================================== */

    .dashboard-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #172033;
        margin-bottom: 0.2rem;
    }

    .dashboard-subtitle {
        color: #667085;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }


    /* ========================================================
       KPI CARDS
       ======================================================== */

    .kpi-card {
        background-color: white;
        padding: 1.2rem 1.3rem;
        border-radius: 14px;
        border: 1px solid #E4E7EC;
        box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.04);
        height: 120px;
    }

    .kpi-title {
        color: #667085;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 0.4rem;
    }

    .kpi-value {
        color: #172033;
        font-size: 1.65rem;
        font-weight: 700;
    }


    /* ========================================================
       SECTION HEADINGS
       ======================================================== */

    .section-title {
        color: #172033;
        font-size: 1.25rem;
        font-weight: 650;
        margin-top: 1rem;
        margin-bottom: 0.7rem;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton button {
        border-radius: 8px;
        font-weight: 600;
    }


    /* ========================================================
       TABS
       ======================================================== */

    button[data-baseweb="tab"] {
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    master_df, site_metadata = load_all_sites("data")

    return master_df, site_metadata


master_df, site_metadata = load_data()


# ============================================================
# PREPARE SITE LIST
# ============================================================

all_sites = sorted(
    master_df["Site"]
    .dropna()
    .unique()
    .tolist()
)


# ============================================================
# SESSION STATE
# ============================================================

if "selected_sites" not in st.session_state:

    st.session_state.selected_sites = all_sites.copy()


def select_all_sites():

    st.session_state.selected_sites = all_sites.copy()


def clear_all_sites():

    st.session_state.selected_sites = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ☀️ Solar Analytics")

    st.markdown("### Site Selection")

    st.caption(
        "Choose one or multiple solar sites to analyze."
    )

    # --------------------------------------------------------
    # MULTI-SITE SELECTOR
    # --------------------------------------------------------

    selected_sites = st.multiselect(
        "Select Sites",
        options=all_sites,
        key="selected_sites"
    )

    # --------------------------------------------------------
    # SELECT ALL / CLEAR BUTTONS
    # --------------------------------------------------------

    button_col1, button_col2 = st.columns(2)

    with button_col1:

        st.button(
            "Select All",
            on_click=select_all_sites,
            use_container_width=True
        )

    with button_col2:

        st.button(
            "Clear",
            on_click=clear_all_sites,
            use_container_width=True
        )

    st.markdown("---")

    # --------------------------------------------------------
    # DATASET INFORMATION
    # --------------------------------------------------------

    st.markdown("### Dataset")

    st.write("📅 Year: **2006**")

    st.write("⏱ Resolution: **5 minutes**")

    st.write(
        f"🏭 Total Sites: **{len(all_sites)}**"
    )

    st.markdown("---")

    st.caption(
        "Solar Power Generation Analysis"
    )


# ============================================================
# VALIDATE SELECTION
# ============================================================

selected_sites = st.session_state.selected_sites


if len(selected_sites) == 0:

    st.warning(
        "Please select at least one site from the sidebar."
    )

    st.stop()


# ============================================================
# FILTER MASTER DATA
# ============================================================

filtered_df = master_df[
    master_df["Site"].isin(selected_sites)
].copy()


# ============================================================
# FILTER SITE METADATA
# ============================================================

selected_metadata = site_metadata[
    site_metadata["Site"].isin(selected_sites)
].copy()


# ============================================================
# SITE LABEL
# ============================================================

if len(selected_sites) == len(all_sites):

    site_label = "All Sites"

elif len(selected_sites) == 1:

    site_label = selected_sites[0]

else:

    site_label = f"{len(selected_sites)} Selected Sites"


# ============================================================
# BASIC KPI CALCULATIONS
# ============================================================

total_capacity = selected_metadata[
    "Capacity_MW"
].sum()


total_generation = filtered_df[
    "Energy_MWh"
].sum()


peak_power = filtered_df[
    "Power(MW)"
].max()


average_power = filtered_df[
    "Power(MW)"
].mean()


number_of_sites = len(selected_sites)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">'
    '☀️ Solar Power Analytics Dashboard'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="dashboard-subtitle">'
    f'Analyzing <b>{site_label}</b> · 2006 · 5-minute resolution'
    f'</div>',
    unsafe_allow_html=True
)


# ============================================================
# KPI CARDS
# ============================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)


with kpi1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                Selected Sites
            </div>

            <div class="kpi-value">
                {number_of_sites}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                Installed Capacity
            </div>

            <div class="kpi-value">
                {total_capacity:,.1f} MW
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                Total Generation
            </div>

            <div class="kpi-value">
                {total_generation:,.0f} MWh
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpi4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                Peak Power
            </div>

            <div class="kpi-value">
                {peak_power:,.2f} MW
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown("")


# ============================================================
# MONTH ORDER
# ============================================================

month_order = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Overview",
        "📈 Generation Trends",
        "☀️ Daily Profile",
        "🏭 Site Comparison"
    ]
)


# ============================================================
# TAB 1 — OVERVIEW
# ============================================================

with tab1:

    st.markdown(
        '<div class="section-title">'
        'Regional Generation Overview'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # MONTHLY GENERATION
    # --------------------------------------------------------

    monthly = monthly_energy_by_site(
        filtered_df
    )

    monthly_regional = (
        monthly
        .groupby(
            ["Month", "Month_Name"],
            as_index=False
        )["Energy_MWh"]
        .sum()
    )

    monthly_regional["Month_Name"] = pd.Categorical(
        monthly_regional["Month_Name"],
        categories=month_order,
        ordered=True
    )

    monthly_regional = monthly_regional.sort_values(
        "Month"
    )

    fig_generation = px.bar(
        monthly_regional,
        x="Month_Name",
        y="Energy_MWh",
        labels={
            "Month_Name": "Month",
            "Energy_MWh": "Energy Generated (MWh)"
        }
    )

    fig_generation.update_layout(
        height=430,
        template="plotly_white",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        ),
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_generation,
        use_container_width=True
    )


    # --------------------------------------------------------
    # TWO-COLUMN ANALYSIS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    # ========================================================
    # MONTHLY AVERAGE POWER
    # ========================================================

    with col1:

        st.markdown(
            '<div class="section-title">'
            'Monthly Average Power'
            '</div>',
            unsafe_allow_html=True
        )

        monthly_power = (
            filtered_df
            .groupby(
                ["Month", "Month_Name"],
                as_index=False
            )["Power(MW)"]
            .mean()
        )

        monthly_power["Month_Name"] = pd.Categorical(
            monthly_power["Month_Name"],
            categories=month_order,
            ordered=True
        )

        monthly_power = monthly_power.sort_values(
            "Month"
        )

        fig_power = px.line(
            monthly_power,
            x="Month_Name",
            y="Power(MW)",
            markers=True,
            labels={
                "Month_Name": "Month",
                "Power(MW)": "Average Power (MW)"
            }
        )

        fig_power.update_layout(
            height=380,
            template="plotly_white",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig_power,
            use_container_width=True
        )


    # ========================================================
    # MONTHLY CAPACITY FACTOR
    # ========================================================

    with col2:

        st.markdown(
            '<div class="section-title">'
            'Monthly Capacity Factor'
            '</div>',
            unsafe_allow_html=True
        )

        # Monthly energy
        cf_data = (
            filtered_df
            .groupby(
                ["Month", "Month_Name"],
                as_index=False
            )
            .agg(
                Energy_MWh=("Energy_MWh", "sum"),
                Days=("Date", "nunique")
            )
        )

        # Total installed capacity of selected sites
        selected_capacity = selected_metadata[
            "Capacity_MW"
        ].sum()

        # Capacity factor
        cf_data["Capacity_Factor_Pct"] = (
            cf_data["Energy_MWh"]
            /
            (
                selected_capacity
                * cf_data["Days"]
                * 24
            )
            * 100
        )

        cf_data["Month_Name"] = pd.Categorical(
            cf_data["Month_Name"],
            categories=month_order,
            ordered=True
        )

        cf_data = cf_data.sort_values(
            "Month"
        )

        fig_cf = px.line(
            cf_data,
            x="Month_Name",
            y="Capacity_Factor_Pct",
            markers=True,
            labels={
                "Month_Name": "Month",
                "Capacity_Factor_Pct":
                    "Capacity Factor (%)"
            }
        )

        fig_cf.update_layout(
            height=380,
            template="plotly_white",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig_cf,
            use_container_width=True
        )


# ============================================================
# TAB 2 — GENERATION TRENDS
# ============================================================

with tab2:

    st.markdown(
        '<div class="section-title">'
        'Site-Level Generation Trends'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Compare monthly energy generation across the selected sites."
    )


    # --------------------------------------------------------
    # MONTHLY ENERGY BY SITE
    # --------------------------------------------------------

    monthly = monthly_energy_by_site(
        filtered_df
    )

    monthly["Month_Name"] = pd.Categorical(
        monthly["Month_Name"],
        categories=month_order,
        ordered=True
    )

    monthly = monthly.sort_values(
        ["Month", "Site"]
    )


    fig_monthly = px.line(
        monthly,
        x="Month_Name",
        y="Energy_MWh",
        color="Site",
        markers=True,
        labels={
            "Month_Name": "Month",
            "Energy_MWh": "Energy Generated (MWh)",
            "Site": "Site"
        },
        category_orders={
            "Month_Name": month_order
        }
    )

    fig_monthly.update_layout(
        height=500,
        template="plotly_white",
        hovermode="x unified",
        legend_title="Site"
    )

    st.plotly_chart(
        fig_monthly,
        use_container_width=True
    )


    # --------------------------------------------------------
    # MONTHLY CAPACITY FACTOR BY SITE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Capacity Factor by Site'
        '</div>',
        unsafe_allow_html=True
    )

    site_cf = (
        filtered_df
        .groupby(
            [
                "Site",
                "Month",
                "Month_Name"
            ],
            as_index=False
        )
        .agg(
            Energy_MWh=("Energy_MWh", "sum"),
            Days=("Date", "nunique")
        )
    )

    # Add capacity to each site
    site_cf = site_cf.merge(
        selected_metadata[
            ["Site", "Capacity_MW"]
        ],
        on="Site",
        how="left"
    )

    site_cf["Capacity_Factor_Pct"] = (
        site_cf["Energy_MWh"]
        /
        (
            site_cf["Capacity_MW"]
            * site_cf["Days"]
            * 24
        )
        * 100
    )

    site_cf["Month_Name"] = pd.Categorical(
        site_cf["Month_Name"],
        categories=month_order,
        ordered=True
    )

    site_cf = site_cf.sort_values(
        ["Month", "Site"]
    )


    fig_site_cf = px.line(
        site_cf,
        x="Month_Name",
        y="Capacity_Factor_Pct",
        color="Site",
        markers=True,
        labels={
            "Month_Name": "Month",
            "Capacity_Factor_Pct":
                "Capacity Factor (%)",
            "Site": "Site"
        },
        category_orders={
            "Month_Name": month_order
        }
    )

    fig_site_cf.update_layout(
        height=500,
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_site_cf,
        use_container_width=True
    )


# ============================================================
# TAB 3 — DAILY PROFILE
# ============================================================

with tab3:

    st.markdown(
        '<div class="section-title">'
        'Average Daily Generation Profile'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Average power output at each hour of the day."
    )


    # --------------------------------------------------------
    # HOURLY PROFILE
    # --------------------------------------------------------

    hourly = hourly_average_power(
        filtered_df
    )


    fig_hourly = px.line(
        hourly,
        x="Hour",
        y="Power(MW)",
        color="Site",
        markers=True,
        labels={
            "Hour": "Hour of Day",
            "Power(MW)": "Average Power (MW)",
            "Site": "Site"
        }
    )

    fig_hourly.update_layout(
        height=500,
        template="plotly_white",
        hovermode="x unified",
        xaxis=dict(
            dtick=1,
            title="Hour of Day"
        ),
        yaxis_title="Average Power (MW)"
    )

    st.plotly_chart(
        fig_hourly,
        use_container_width=True
    )


    # --------------------------------------------------------
    # PEAK GENERATION HOUR
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Peak Generation Hour'
        '</div>',
        unsafe_allow_html=True
    )

    peak_hours = (
        hourly
        .loc[
            hourly.groupby("Site")[
                "Power(MW)"
            ].idxmax()
        ]
        .copy()
    )


    peak_hours = peak_hours[
        [
            "Site",
            "Hour",
            "Power(MW)"
        ]
    ]


    peak_hours = peak_hours.rename(
        columns={
            "Hour": "Peak Hour",
            "Power(MW)": "Peak Average Power (MW)"
        }
    )


    peak_hours["Peak Hour"] = (
        peak_hours["Peak Hour"]
        .astype(int)
        .astype(str)
        + ":00"
    )


    peak_hours[
        "Peak Average Power (MW)"
    ] = peak_hours[
        "Peak Average Power (MW)"
    ].round(2)


    st.dataframe(
        peak_hours,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 4 — SITE COMPARISON
# ============================================================

with tab4:

    st.markdown(
        '<div class="section-title">'
        'Site Performance Comparison'
        '</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Compare generation, capacity and performance across the selected sites."
    )


    # ========================================================
    # BUILD PERFORMANCE DATAFRAME
    # ========================================================

    performance = (
        filtered_df
        .groupby("Site")
        .agg(
            Total_Generation_MWh=(
                "Energy_MWh",
                "sum"
            ),

            Average_Power_MW=(
                "Power(MW)",
                "mean"
            ),

            Peak_Power_MW=(
                "Power(MW)",
                "max"
            )
        )
        .reset_index()
    )


    # --------------------------------------------------------
    # ADD CAPACITY
    # --------------------------------------------------------

    performance = performance.merge(
        selected_metadata[
            [
                "Site",
                "Capacity_MW"
            ]
        ],
        on="Site",
        how="left"
    )


    # --------------------------------------------------------
    # CAPACITY FACTOR
    # --------------------------------------------------------

    days_in_dataset = (
        filtered_df
        .groupby("Site")["Date"]
        .nunique()
        .reset_index(
            name="Days"
        )
    )


    performance = performance.merge(
        days_in_dataset,
        on="Site",
        how="left"
    )


    performance["Capacity_Factor_Pct"] = (
        performance["Total_Generation_MWh"]
        /
        (
            performance["Capacity_MW"]
            * performance["Days"]
            * 24
        )
        * 100
    )


    # --------------------------------------------------------
    # PEAK UTILIZATION
    # --------------------------------------------------------

    performance["Peak_Utilization_Pct"] = (
        performance["Peak_Power_MW"]
        /
        performance["Capacity_MW"]
        * 100
    )


    # ========================================================
    # TOTAL GENERATION
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        'Total Energy Generation'
        '</div>',
        unsafe_allow_html=True
    )


    generation_chart = performance.sort_values(
        "Total_Generation_MWh",
        ascending=False
    )


    fig_generation = px.bar(
        generation_chart,
        x="Site",
        y="Total_Generation_MWh",
        labels={
            "Total_Generation_MWh":
                "Total Generation (MWh)",

            "Site":
                "Site"
        },
        text_auto=".2s"
    )


    fig_generation.update_layout(
        height=430,
        template="plotly_white",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        )
    )


    st.plotly_chart(
        fig_generation,
        use_container_width=True
    )


    # ========================================================
    # CAPACITY + AVERAGE POWER
    # ========================================================

    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # INSTALLED CAPACITY
    # --------------------------------------------------------

    with col1:

        st.markdown(
            '<div class="section-title">'
            'Installed Capacity'
            '</div>',
            unsafe_allow_html=True
        )


        capacity_chart = performance.sort_values(
            "Capacity_MW",
            ascending=False
        )


        fig_capacity = px.bar(
            capacity_chart,
            x="Site",
            y="Capacity_MW",
            labels={
                "Capacity_MW":
                    "Installed Capacity (MW)",

                "Site":
                    "Site"
            },
            text_auto=".1f"
        )


        fig_capacity.update_layout(
            height=400,
            template="plotly_white",
            margin=dict(
                l=20,
                r=20,
                t=30,
                b=20
            )
        )


        st.plotly_chart(
            fig_capacity,
            use_container_width=True
        )


    # --------------------------------------------------------
    # AVERAGE POWER
    # --------------------------------------------------------

    with col2:

        st.markdown(
            '<div class="section-title">'
            'Average Power Output'
            '</div>',
            unsafe_allow_html=True
        )


        average_chart = performance.sort_values(
            "Average_Power_MW",
            ascending=False
        )


        fig_average = px.bar(
            average_chart,
            x="Site",
            y="Average_Power_MW",
            labels={
                "Average_Power_MW":
                    "Average Power (MW)",

                "Site":
                    "Site"
            },
            text_auto=".2f"
        )


        fig_average.update_layout(
            height=400,
            template="plotly_white",
            margin=dict(
                l=20,
                r=20,
                t=30,
                b=20
            )
        )


        st.plotly_chart(
            fig_average,
            use_container_width=True
        )


    # ========================================================
    # CAPACITY FACTOR + PEAK UTILIZATION
    # ========================================================

    col3, col4 = st.columns(2)


    # --------------------------------------------------------
    # CAPACITY FACTOR
    # --------------------------------------------------------

    with col3:

        st.markdown(
            '<div class="section-title">'
            'Capacity Factor'
            '</div>',
            unsafe_allow_html=True
        )


        cf_chart = performance.sort_values(
            "Capacity_Factor_Pct",
            ascending=False
        )


        fig_cf = px.bar(
            cf_chart,
            x="Site",
            y="Capacity_Factor_Pct",
            labels={
                "Capacity_Factor_Pct":
                    "Capacity Factor (%)",

                "Site":
                    "Site"
            },
            text_auto=".2f"
        )


        fig_cf.update_layout(
            height=400,
            template="plotly_white",
            margin=dict(
                l=20,
                r=20,
                t=30,
                b=20
            ),
            yaxis=dict(
                ticksuffix="%"
            )
        )


        st.plotly_chart(
            fig_cf,
            use_container_width=True
        )


    # --------------------------------------------------------
    # PEAK UTILIZATION
    # --------------------------------------------------------

    with col4:

        st.markdown(
            '<div class="section-title">'
            'Peak Utilization'
            '</div>',
            unsafe_allow_html=True
        )


        peak_chart = performance.sort_values(
            "Peak_Utilization_Pct",
            ascending=False
        )


        fig_peak = px.bar(
            peak_chart,
            x="Site",
            y="Peak_Utilization_Pct",
            labels={
                "Peak_Utilization_Pct":
                    "Peak Utilization (%)",

                "Site":
                    "Site"
            },
            text_auto=".2f"
        )


        fig_peak.update_layout(
            height=400,
            template="plotly_white",
            margin=dict(
                l=20,
                r=20,
                t=30,
                b=20
            ),
            yaxis=dict(
                ticksuffix="%"
            )
        )


        st.plotly_chart(
            fig_peak,
            use_container_width=True
        )


    # ========================================================
    # PERFORMANCE TABLE
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        'Performance Summary'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # CREATE PRESENTATION COPY
    # --------------------------------------------------------

    performance_display = performance.copy()


    performance_display = performance_display[
        [
            "Site",
            "Capacity_MW",
            "Total_Generation_MWh",
            "Average_Power_MW",
            "Peak_Power_MW",
            "Capacity_Factor_Pct",
            "Peak_Utilization_Pct"
        ]
    ]


    # Round numbers
    performance_display[
        "Capacity_MW"
    ] = performance_display[
        "Capacity_MW"
    ].round(1)


    performance_display[
        "Total_Generation_MWh"
    ] = performance_display[
        "Total_Generation_MWh"
    ].round(1)


    performance_display[
        "Average_Power_MW"
    ] = performance_display[
        "Average_Power_MW"
    ].round(2)


    performance_display[
        "Peak_Power_MW"
    ] = performance_display[
        "Peak_Power_MW"
    ].round(2)


    performance_display[
        "Capacity_Factor_Pct"
    ] = performance_display[
        "Capacity_Factor_Pct"
    ].round(2)


    performance_display[
        "Peak_Utilization_Pct"
    ] = performance_display[
        "Peak_Utilization_Pct"
    ].round(2)


    # --------------------------------------------------------
    # RENAME FOR DISPLAY
    # --------------------------------------------------------

    performance_display = performance_display.rename(
        columns={
            "Capacity_MW":
                "Capacity (MW)",

            "Total_Generation_MWh":
                "Total Generation (MWh)",

            "Average_Power_MW":
                "Average Power (MW)",

            "Peak_Power_MW":
                "Peak Power (MW)",

            "Capacity_Factor_Pct":
                "Capacity Factor (%)",

            "Peak_Utilization_Pct":
                "Peak Utilization (%)"
        }
    )


    st.dataframe(
        performance_display,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Solar Power Generation Analysis Dashboard · "
    "2006 Dataset · 5-Minute Resolution"
)