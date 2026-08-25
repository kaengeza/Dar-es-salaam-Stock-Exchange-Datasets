from datetime import datetime
from io import StringIO
from pathlib import Path
import pandas as pd
import requests

URL = "https://dse.co.tz/"
FILE = "ohlcv.csv"

import pandas as pd

class cleaning:
    def __init__(self, df: pd.DataFrame):
        ...
    def cleaner(df: pd.DataFrame)-> pd.DataFrame:
        df["Symbol"] = (df["Symbol"].astype(str).str.strip().str.upper())
        df["Date"]   = pd.to_datetime(df["Date"], errors="coerce")
        df["Change"] = (df["Change"]
                        .astype("string")
                        .str.extract(r"([-+]?\d+(?:\.\d+)?)", expand=False)
                        .astype(float)
                       )
        df["% Change"] = ((df["Change"]/100) * df['Close'])
        
        df           = df.rename(columns={"Symbol": "Ticker", "Turn over": "Turnover", "MCAP (TZS 'B)": "mktcap"})
        df           = df.rename(columns={"Out Standing Bid": "Bids", "Out Standing Offer": "Offers"})
        df           = df.rename(columns={col: col.lower() for col in df.columns})
        df           = df.drop_duplicates(inplace=False)
        
        for col in df.columns.difference(["date", "ticker", "change"]):
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.replace("TZS", "", regex=False)
                    .str.strip()
                    .pipe(pd.to_numeric, errors="coerce")
                 )

        columns = ['date', 'ticker','high', 'low', 'open', 
                   'prev close', 'close', 'change', '% change',
                   'volume', 'turnover', 'deals', 'bids', 
                   'offers', 'mktcap'
                    ]
        
        return df[columns].copy()

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
    new_data= cleaning.cleaner(new_data)
    

    # Load existing CSV
    existing_data = load_existing_data()
    existing_data = cleaning.cleaner(existing_data)


    # Combine
    combined = pd.concat(
        [existing_data, new_data],
        ignore_index=True
    )

    # Remove duplicate Date + Symbol
    combined = (
        combined
        .drop_duplicates(
            subset=["date", "ticker"],
            keep="last"
        )
        .sort_values(["date", "ticker"])
        .reset_index(drop=True)
    )

    

    # Save
    combined.to_csv(FILE, index=False)

    print(f"Downloaded: {len(new_data)} rows")
    print(f"Total records: {len(combined)}")
    print(f"Last date: {today}")


if __name__ == "__main__":
    main()
