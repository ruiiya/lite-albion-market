import pandas as pd
import sqlite3
import re
import os

def re_tiers(tiers):
    if tiers == "" or tiers is None:
        return ".*"
    tl = tiers.split(" ")
    re_l = []
    d = {}
    for t in tl:
        tier, enchant = t.split(".")
        if tier in d:
            d[tier].append(enchant)
        else:
            d[tier] = [enchant]
    for k in d.keys():
        contain_zero = ("0" in d[k])
        if contain_zero: d[k].remove("0")
        re_s = "(^T%s[^@]+%s$)" % (k , "" if len(d[k]) == 0 else f"(@[{''.join(d[k])}]){'?' if contain_zero else ''}")
        re_l.append(re_s)
    return "|".join(re_l)
    pass

def regex_filter(val, filters):
    if val:
        mo = re.search(re_tiers(filters),val)
        if mo:
            return True
        else:
            return False
    else:
        return False

def convert(locations, filters, qualities):
    for v in locations:
        try:
            if not os.path.exists(f"{v}.db"):
                continue
            print(f"Converting {v}.db...")
            conn = sqlite3.connect(f"{v}.db", isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
            df = pd.read_sql_query("SELECT * FROM Data", conn)
            df = df.sort_values(by=["id","quality"])
            df = df[df.quality.isin(qualities)]
            df = df[df["id"].apply(regex_filter, filters=filters)]
            print(df)
            df.to_csv(f'{v}.csv', index=False)
        except Exception as e:
            print(e)
            continue

