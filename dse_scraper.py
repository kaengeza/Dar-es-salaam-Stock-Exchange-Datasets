"""
DSE (Dar es Salaam Stock Exchange) Data Scraper
Fetches OHLCV data from the DSE website and maintains a local CSV file.
"""

from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Optional

import pandas as pd
import requests


# Configuration
DSE_URL = "https://dse.co.tz/"
DATA_FILE = "ohlcv.csv"

# Expected columns after cleaning
REQUIRED_COLUMNS = [
    "date",
    "ticker",
    "high",
    "low",
    "open",
    "prev close",
    "close",
    "change",
    "% change",
    "volume",
    "turnover",
    "deals",
    "bids",
    "offers",
    "mktcap",
]

# Column rename mapping
COLUMN_RENAME_MAP = {
    "Symbol": "ticker",
    "Turn over": "turnover",
    "MCAP (TZS 'B)": "mktcap",
    "Out Standing Bid": "bids",
    "Out Standing Offer": "offers",
}


class DataCleaner:
    """Handles data cleaning and validation for DSE market data."""

    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize DSE market data.

        Args:
            df: Raw DataFrame from DSE website

        Returns:
            Cleaned and standardized DataFrame
        """
        if df.empty:
            return pd.DataFrame(columns=REQUIRED_COLUMNS)

        df = df.copy()

        # Clean Symbol/Ticker
        if "Symbol" in df.columns:
            df["Symbol"] = (
                df["Symbol"].astype(str).str.strip().str.upper()
            )

        # Parse Date
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Extract Change percentage
        if "Change" in df.columns:
            df["Change"] = (
                df["Change"]
                .astype(str)
                .str.extract(r"([-+]?\d+(?:\.\d+)?)", expand=False)
                .astype(float)
            )

        # Calculate % Change if not present
        if "% Change" not in df.columns and "Change" in df.columns:
            df["% Change"] = (df["Change"] / 100) * df.get("Close", 0)

        # Rename columns
        df = df.rename(columns=COLUMN_RENAME_MAP)
        df = df.rename(columns={col: col.lower() for col in df.columns})

        # Remove duplicates
        df = df.drop_duplicates(inplace=False)

        # Clean numeric columns
        numeric_cols = df.columns.difference(
            ["date", "ticker", "change"]
        )
        for col in numeric_cols:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.replace("TZS", "", regex=False)
                    .str.strip()
                    .pipe(pd.to_numeric, errors="coerce")
                )

        # Select and reorder required columns
        return df[REQUIRED_COLUMNS].copy()


class DSEScraper:
    """Handles fetching and managing DSE market data."""

    def __init__(self, url: str = DSE_URL, data_file: str = DATA_FILE):
        self.url = url
        self.data_file = Path(data_file)
        self.cleaner = DataCleaner()

    def fetch_latest_data(self) -> Optional[pd.DataFrame]:
        """
        Fetch latest market data from DSE website.

        Returns:
            DataFrame with new market data or None if fetch fails
        """
        try:
            response = requests.get(self.url, timeout=30)
            response.raise_for_status()

            # Read HTML tables
            tables = pd.read_html(StringIO(response.text))

            # Extract market table (typically table 3)
            if len(tables) <= 3:
                print("Error: Could not find market data table")
                return None

            new_data = tables[3].copy()

            # Add today's date
            today = datetime.now().strftime("%Y-%m-%d")
            new_data["Date"] = today

            return new_data

        except requests.RequestException as e:
            print(f"Error fetching data from DSE: {e}")
            return None
        except Exception as e:
            print(f"Error processing data: {e}")
            return None

    def load_existing_data(self) -> pd.DataFrame:
        """
        Load existing data from CSV file.

        Returns:
            DataFrame with existing data or empty DataFrame
        """
        if self.data_file.exists():
            try:
                return pd.read_csv(self.data_file)
            except Exception as e:
                print(f"Error reading existing data: {e}")
                return pd.DataFrame()
        return pd.DataFrame()

    def combine_data(
        self, existing: pd.DataFrame, new: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Combine existing and new data, removing duplicates.

        Args:
            existing: Existing market data
            new: New market data

        Returns:
            Combined and deduplicated DataFrame
        """
        combined = pd.concat([existing, new], ignore_index=True)

        # Remove duplicates (keep latest)
        combined = (
            combined.drop_duplicates(subset=["date", "ticker"], keep="last")
            .sort_values(["date", "ticker"])
            .reset_index(drop=True)
        )

        return combined

    def save_data(self, df: pd.DataFrame) -> None:
        """Save data to CSV file."""
        df.to_csv(self.data_file, index=False)

    def run(self) -> bool:
        """
        Main execution: fetch, clean, combine, and save data.

        Returns:
            True if successful, False otherwise
        """
        # Fetch new data
        print("Fetching latest DSE data...")
        new_data = self.fetch_latest_data()
        if new_data is None:
            return False

        # Clean new data
        print("Cleaning new data...")
        new_data = self.cleaner.clean(new_data)

        # Load and clean existing data
        print("Loading existing data...")
        existing_data = self.load_existing_data()
        if not existing_data.empty:
            existing_data = self.cleaner.clean(existing_data)

        # Combine
        print("Combining data...")
        combined = self.combine_data(existing_data, new_data)

        # Save
        print("Saving data...")
        self.save_data(combined)

        # Summary
        today = datetime.now().strftime("%Y-%m-%d")
        print("\n" + "=" * 50)
        print(f"✓ Downloaded: {len(new_data)} rows")
        print(f"✓ Total records: {len(combined)}")
        print(f"✓ Last update: {today}")
        print("=" * 50)

        return True


def main():
    """Main entry point."""
    scraper = DSEScraper()
    success = scraper.run()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
