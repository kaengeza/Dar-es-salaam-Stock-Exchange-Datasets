from src.collection import collection
from src.utilis import existing_data
from src.cleaning import cleaning
from datetime import datetime
import pandas as pd

def main(filepath = "dataset/cleaned.csv"):
    new_data        = collection.collect()
    old_data        = existing_data()
    old_cleaned     = cleaning.cleaner(old_data)
    new_cleaned     = cleaning.cleaner(new_data)
    combined        = pd.concat([old_cleaned, new_cleaned], ignore_index=True)
    combined        = (combined.drop_duplicates(
                            subset=["date", "ticker"],
                            keep="last")
                            .sort_values(["date", "ticker"])
                            .reset_index(drop=True)
                          )
    
    combined.to_csv(filepath, index=False)
    
    
if __name__ == "__main__":
    main()
