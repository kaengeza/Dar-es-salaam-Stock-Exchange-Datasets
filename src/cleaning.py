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

