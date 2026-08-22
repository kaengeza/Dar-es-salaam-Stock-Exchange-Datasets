from pathlib import Path
from typing import Union
import pandas as pd

def existing_data(file: Union[Path] = "dataset/ohlcv.csv")-> pd.DataFrame():
    if Path(file).exists():
        return pd.read_csv(file)
    return pd.DataFrame()
