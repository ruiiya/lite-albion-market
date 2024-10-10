import pandas as pd
import sqlite3
import re
import os
from common import re_tiers, Filter

def regex_filter(val, filters):
    if val:
        mo = re.search(re_tiers(filters),val)
        if mo:
            return True
        else:
            return False
    else:
        return False

def convert(locations, filter: Filter):
    for v in locations:
        try:
            os.makedirs("Databases", exist_ok=True)
            if not os.path.exists(f"{v}.db"):
                continue
            print(f"Converting {v}.db...")
            conn = sqlite3.connect(f"{v}.db", isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
            df = pd.read_sql_query("SELECT * FROM Data", conn)
            df = df.sort_values(by=["id","quality"])
            df = df[df.quality.isin(filter.qualities)]
            df = df[df["id"].apply(regex_filter, filters=filter.tiers)]
            print(df)
            df.to_csv(f'Databases/{v}.csv', index=False)
        except Exception as e:
            print(e)
            continue