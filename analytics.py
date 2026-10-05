import pandas as pd
import numpy as np
import glob
import os
import re


# ============================================================
# 1. FIND DATA FILES
# ============================================================

def get_csv_files(data_folder="data"):
    """
    Find all CSV files inside the data folder.
    """

    files = glob.glob(
        os.path.join(data_folder, "*.csv")
    )

    return sorted(files)


# ============================================================
# 2. EXTRACT SITE METADATA FROM FILENAME
# ============================================================

def extract_metadata(filepath):
    """
    Extract latitude, longitude and installed capacity
    from the filename.
    """

    filename = os.path.basename(filepath)

    pattern = (
        r"Actual_([-0-9.]+)_"
        r"([-0-9.]+)_2006_UPV_"
        r"([0-9.]+)MW_5_Min\.csv"
    )

    match = re.search(pattern, filename)

    if match:

        latitude = float(match.group(1))
        longitude = float(match.group(2))
        capacity = float(match.group(3))

        return latitude, longitude, capacity

    return None, None, None


# ============================================================
# 3. CREATE SITE METADATA TABLE
# ============================================================

def create_site_metadata(files):

    site_metadata = []

    for i, file in enumerate(files, start=1):

        latitude, longitude, capacity = (
            extract_metadata(file)
        )

        site_metadata.append({
            "Site": f"Site {i}",
            "File": file,
            "Latitude": latitude,
            "Longitude": longitude,
            "Capacity_MW": capacity
        })

    return pd.DataFrame(site_metadata)


# ============================================================
# 4. PROCESS ONE SITE
# ============================================================

def process_site(
    filepath,
    site_name,
    latitude,
    longitude,
    capacity
):
    """
    Load and preprocess one site's 5-minute dataset.
    """

    data = pd.read_csv(filepath)

    # Convert timestamp
    data["LocalTime"] = pd.to_datetime(
        data["LocalTime"]
    )

    # Site metadata
    data["Site"] = site_name
    data["Latitude"] = latitude
    data["Longitude"] = longitude
    data["Capacity_MW"] = capacity

    # Time features
    data["Date"] = data["LocalTime"].dt.date
    data["Year"] = data["LocalTime"].dt.year
    data["Month"] = data["LocalTime"].dt.month
    data["Month_Name"] = (
        data["LocalTime"].dt.month_name()
    )
    data["Day"] = data["LocalTime"].dt.day
    data["Hour"] = data["LocalTime"].dt.hour
    data["Minute"] = data["LocalTime"].dt.minute
    data["DayOfWeek"] = (
        data["LocalTime"].dt.dayofweek
    )

    # Energy produced during each 5-minute interval
    data["Energy_MWh"] = (
        data["Power(MW)"] * (5 / 60)
    )

    return data


# ============================================================
# 5. LOAD ALL SITES
# ============================================================

def load_all_sites(data_folder="data"):

    files = get_csv_files(data_folder)

    if len(files) == 0:
        raise FileNotFoundError(
            "No CSV files found in the data folder."
        )

    site_metadata = create_site_metadata(files)

    all_sites = []

    for _, row in site_metadata.iterrows():

        site_data = process_site(
            row["File"],
            row["Site"],
            row["Latitude"],
            row["Longitude"],
            row["Capacity_MW"]
        )

        all_sites.append(site_data)

    master_df = pd.concat(
        all_sites,
        ignore_index=True
    )

    return master_df, site_metadata


# ============================================================
# 6. BASIC DATA QUALITY
# ============================================================

def calculate_data_quality(master_df):

    quality = {
        "Rows": len(master_df),
        "Columns": len(master_df.columns),
        "Missing_Values": int(
            master_df.isnull().sum().sum()
        ),
        "Duplicate_Rows": int(
            master_df.duplicated().sum()
        ),
        "Negative_Power_Values": int(
            (master_df["Power(MW)"] < 0).sum()
        ),
        "Zero_Power_Values": int(
            (master_df["Power(MW)"] == 0).sum()
        )
    }

    quality["Zero_Power_Percentage"] = (
        quality["Zero_Power_Values"]
        / quality["Rows"]
        * 100
    )

    return quality


# ============================================================
# 7. OVERALL POWER STATISTICS
# ============================================================

def calculate_power_statistics(master_df):

    power = master_df["Power(MW)"]

    statistics = {
        "Mean": power.mean(),
        "Median": power.median(),
        "Standard_Deviation": power.std(),
        "Minimum": power.min(),
        "Maximum": power.max(),
        "Q1": power.quantile(0.25),
        "Q3": power.quantile(0.75),
        "Skewness": power.skew(),
        "Kurtosis": power.kurtosis()
    }

    return statistics


# ============================================================
# 8. MONTHLY AVERAGE POWER BY SITE
# ============================================================

def monthly_average_power(master_df):

    result = (
        master_df
        .groupby(
            ["Site", "Month", "Month_Name"]
        )["Power(MW)"]
        .mean()
        .reset_index()
    )

    return result


# ============================================================
# 9. MONTHLY TOTAL ENERGY BY SITE
# ============================================================

def monthly_energy_by_site(master_df):

    result = (
        master_df
        .groupby(
            ["Site", "Month", "Month_Name"]
        )["Energy_MWh"]
        .sum()
        .reset_index()
    )

    return result


# ============================================================
# 10. REGIONAL MONTHLY ENERGY
# ============================================================

def regional_monthly_energy(master_df):

    result = (
        master_df
        .groupby(
            ["Month", "Month_Name"]
        )["Energy_MWh"]
        .sum()
        .reset_index()
    )

    return result


# ============================================================
# 11. MONTHLY POWER VARIABILITY
# ============================================================

def monthly_power_variability(master_df):

    result = (
        master_df
        .groupby(
            ["Site", "Month", "Month_Name"]
        )["Power(MW)"]
        .std()
        .reset_index(
            name="Power_Std_MW"
        )
    )

    return result


# ============================================================
# 12. HIGHEST GENERATION MONTH
# ============================================================

def highest_generation_month(master_df):

    monthly = monthly_energy_by_site(
        master_df
    )

    result = monthly.loc[
        monthly.groupby("Site")[
            "Energy_MWh"
        ].idxmax()
    ]

    return result.reset_index(drop=True)


# ============================================================
# 13. LOWEST GENERATION MONTH
# ============================================================

def lowest_generation_month(master_df):

    monthly = monthly_energy_by_site(
        master_df
    )

    result = monthly.loc[
        monthly.groupby("Site")[
            "Energy_MWh"
        ].idxmin()
    ]

    return result.reset_index(drop=True)


# ============================================================
# 14. HOURLY AVERAGE POWER BY SITE
# ============================================================

def hourly_average_power(master_df):

    result = (
        master_df
        .groupby(
            ["Site", "Hour"]
        )["Power(MW)"]
        .mean()
        .reset_index()
    )

    return result


# ============================================================
# 15. PEAK GENERATION HOUR
# ============================================================

def peak_generation_hour(master_df):

    hourly = hourly_average_power(
        master_df
    )

    result = hourly.loc[
        hourly.groupby("Site")[
            "Power(MW)"
        ].idxmax()
    ]

    return result.reset_index(drop=True)


# ============================================================
# 16. LOWEST ACTIVE GENERATION HOUR
# ============================================================

def lowest_active_generation_hour(master_df):

    hourly = hourly_average_power(
        master_df
    )

    active_hourly = hourly[
        hourly["Power(MW)"] > 0
    ]

    result = active_hourly.loc[
        active_hourly.groupby("Site")[
            "Power(MW)"
        ].idxmin()
    ]

    return result.reset_index(drop=True)


# ============================================================
# 17. DAILY GENERATION WINDOW
# ============================================================

def daily_generation_window(master_df):

    active_master = master_df[
        master_df["Power(MW)"] > 0
    ].copy()

    result = (
        active_master
        .groupby(
            ["Site", "Date"]
        )["LocalTime"]
        .agg(
            Start_Time="min",
            End_Time="max"
        )
        .reset_index()
    )

    # Generation duration
    result["Duration"] = (
        result["End_Time"]
        - result["Start_Time"]
    )

    # Duration in hours
    result["Duration_Hours"] = (
        result["Duration"]
        .dt.total_seconds()
        / 3600
    )

    # Month
    result["Month"] = (
        pd.to_datetime(
            result["Date"]
        ).dt.month
    )

    result["Month_Name"] = (
        pd.to_datetime(
            result["Date"]
        ).dt.month_name()
    )

    # Start hour
    result["Start_Hour"] = (
        result["Start_Time"].dt.hour
        + result["Start_Time"].dt.minute / 60
    )

    # End hour
    result["End_Hour"] = (
        result["End_Time"].dt.hour
        + result["End_Time"].dt.minute / 60
    )

    return result


# ============================================================
# 18. MONTHLY GENERATION WINDOW
# ============================================================

def monthly_generation_window(master_df):

    daily = daily_generation_window(
        master_df
    )

    result = (
        daily
        .groupby(
            ["Site", "Month"]
        )
        .agg(
            Average_Duration_Hours=(
                "Duration_Hours",
                "mean"
            ),
            Average_Start_Hour=(
                "Start_Hour",
                "mean"
            ),
            Average_End_Hour=(
                "End_Hour",
                "mean"
            )
        )
        .reset_index()
    )

    result["Month_Name"] = (
        result["Month"]
        .apply(
            lambda x: pd.Timestamp(
                year=2006,
                month=x,
                day=1
            ).strftime("%B")
        )
    )

    return result


# ============================================================
# 19. CAPACITY-NORMALIZED POWER
# ============================================================

def normalized_power(master_df):

    result = master_df.copy()

    result["Normalized_Power"] = (
        result["Power(MW)"]
        / result["Capacity_MW"]
    )

    result["Capacity_Utilization_Pct"] = (
        result["Normalized_Power"]
        * 100
    )

    return result


# ============================================================
# 20. MONTHLY CAPACITY UTILIZATION
# ============================================================

def monthly_capacity_utilization(master_df):

    data = normalized_power(
        master_df
    )

    result = (
        data
        .groupby(
            ["Site", "Month", "Month_Name"]
        )["Capacity_Utilization_Pct"]
        .mean()
        .reset_index()
    )

    return result


# ============================================================
# 21. SITE TOTAL GENERATION
# ============================================================

def site_total_generation(master_df):

    result = (
        master_df
        .groupby("Site")
        .agg(
            Total_Energy_MWh=(
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

    return result


# ============================================================
# 22. SITE PERFORMANCE SUMMARY
# ============================================================

def site_performance_summary(
    master_df,
    site_metadata
):

    generation = site_total_generation(
        master_df
    )

    result = generation.merge(
        site_metadata[
            [
                "Site",
                "Capacity_MW",
                "Latitude",
                "Longitude"
            ]
        ],
        on="Site",
        how="left"
    )

    result["Peak_Utilization_Pct"] = (
        result["Peak_Power_MW"]
        / result["Capacity_MW"]
        * 100
    )

    return result


# ============================================================
# 23. DAILY PROFILE SUMMARY
# ============================================================

def daily_profile_summary(master_df):

    hourly = hourly_average_power(
        master_df
    )

    result = (
        hourly
        .groupby("Site")["Power(MW)"]
        .agg(
            Average_Power="mean",
            Peak_Power="max"
        )
        .reset_index()
    )

    result["Peak_to_Average_Ratio"] = (
        result["Peak_Power"]
        / result["Average_Power"]
    )

    return result


# ============================================================
# 24. MONTHLY CAPACITY FACTOR
# ============================================================

def monthly_capacity_factor(
    master_df,
    site_metadata
):

    monthly = (
        master_df
        .groupby(
            ["Site", "Month", "Month_Name"]
        )["Energy_MWh"]
        .sum()
        .reset_index()
    )

    # Number of days in each month
    days_in_month = (
        master_df[
            ["Site", "Month", "Date"]
        ]
        .drop_duplicates()
        .groupby(
            ["Site", "Month"]
        )
        .size()
        .reset_index(
            name="Days"
        )
    )

    monthly = monthly.merge(
        days_in_month,
        on=["Site", "Month"],
        how="left"
    )

    monthly = monthly.merge(
        site_metadata[
            ["Site", "Capacity_MW"]
        ],
        on="Site",
        how="left"
    )

    # Maximum possible energy
    monthly["Maximum_Possible_Energy_MWh"] = (
        monthly["Capacity_MW"]
        * monthly["Days"]
        * 24
    )

    # Capacity factor
    monthly["Capacity_Factor_Pct"] = (
        monthly["Energy_MWh"]
        / monthly["Maximum_Possible_Energy_MWh"]
        * 100
    )

    return monthly


# ============================================================
# 25. YEARLY SITE SUMMARY
# ============================================================

def yearly_site_summary(
    master_df,
    site_metadata
):

    generation = (
        master_df
        .groupby("Site")
        .agg(
            Total_Energy_MWh=(
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

    result = generation.merge(
        site_metadata[
            [
                "Site",
                "Capacity_MW"
            ]
        ],
        on="Site",
        how="left"
    )

    # 2006 has 365 days
    result["Capacity_Factor_Pct"] = (
        result["Total_Energy_MWh"]
        / (
            result["Capacity_MW"]
            * 365
            * 24
        )
        * 100
    )

    result["Peak_Utilization_Pct"] = (
        result["Peak_Power_MW"]
        / result["Capacity_MW"]
        * 100
    )

    return result