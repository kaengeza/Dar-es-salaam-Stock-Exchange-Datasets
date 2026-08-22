from datetime import datetime
from typing import Union
from io import StringIO
import pandas as pd
import requests

class collection:
    def __init__(self):
        ...
        
    def collect(url: Union[str] = "https://dse.co.tz/")-> pd.DataFrame:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        tables   = pd.read_html(StringIO(response.text))
        new_data = tables[3].copy()
        today    = datetime.now().strftime("%Y-%m-%d")
        new_data["Date"] = today
        return new_data