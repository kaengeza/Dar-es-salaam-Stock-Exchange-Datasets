from datetime import datetime
from io import StringIO
from pathlib import Path
import pandas as pd
import requests

URL = "https://dse.co.tz/"
FILE = "ohlcv.csv"


def load_existing_data():
    if Path(FILE).exists():
        return pd.read_csv(FILE)
    return pd.DataFrame()


def clean_data(df):
    df = df.copy()

    df["Symbol"] = (
        df["Symbol"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df


def main():
    # Get DSE website
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
    # Read tables from website
    tables = pd.read_html(StringIO(response.text))

    # Select market table
    new_data = tables[3].copy()

    # Add date
    today = datetime.now().strftime("%Y-%m-%d")
    new_data["Date"] = today

    # Clean new data
    new_data = clean_data(new_data)

    # Load existing CSV
    existing_data = load_existing_data()

    if not existing_data.empty:
        existing_data = clean_data(existing_data)

    # Combine
    combined = pd.concat(
        [existing_data, new_data],
        ignore_index=True
    )

    # Remove duplicate Date + Symbol
    combined = (
        combined
        .drop_duplicates(
            subset=["Date", "Symbol"],
            keep="last"
        )
        .sort_values(["Date", "Symbol"])
        .reset_index(drop=True)
    )

    # Save
    combined.to_csv(FILE, index=False)

    print(f"Downloaded: {len(new_data)} rows")
    print(f"Total records: {len(combined)}")
    print(f"Last date: {today}")


if __name__ == "__main__":
    main()
