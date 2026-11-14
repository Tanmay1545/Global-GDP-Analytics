
import pandas as pd
from sqlalchemy import create_engine
from getpass import getpass

# 1. Get Neon database connection string
database_url = input("Paste your Neon connection string: ")

# 2. Connect to Neon PostgreSQL
database_url = database_url.replace(
    "postgresql://",
    "postgresql+psycopg://",
    1
)

engine = create_engine(database_url)

try:
    # 3. Read World Bank CSV
    df = pd.read_csv(
        "data/gdp_data.csv",
        skiprows=4
    )

    # 4. Identify year columns
    year_columns = [
        col for col in df.columns
        if str(col).isdigit() and len(str(col)) == 4
    ]

    # 5. Convert wide data into long format
    df = df.melt(
        id_vars=["Country Name", "Country Code"],
        value_vars=year_columns,
        var_name="Year",
        value_name="GDP"
    )

    # 6. Clean data
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["GDP"] = pd.to_numeric(df["GDP"], errors="coerce")

    df = df.dropna(
        subset=["Country Name", "Country Code", "Year", "GDP"]
    )

    df = df[df["GDP"] > 0]
    df["Year"] = df["Year"].astype(int)

    # 7. Upload data to Neon PostgreSQL
    df.to_sql(
        "gdp_data",
        engine,
        if_exists="replace",
        index=False,
        chunksize=5000
    )

    # 8. Create database index
    with engine.begin() as connection:
        connection.exec_driver_sql(
            'CREATE INDEX IF NOT EXISTS idx_gdp_country_year '
            'ON gdp_data ("Country Code", "Year")'
        )

    print("\nSUCCESS! GDP data uploaded to Neon.")
    print("Total records:", len(df))
    print("Database table: gdp_data")

except Exception as error:
    print("\nERROR:", error)

finally:
    engine.dispose()
