import pandas as pd
import sqlite3
import re
import numpy as np
import os

from common import re_tiers, Filter

pd.set_option('future.no_silent_downcasting', True)

items = pd.read_csv("items.csv")

def regex_filter(val, filters):
    if val:
        mo = re.search(re_tiers(filters),val)
        if mo:
            return True
        else:
            return False
    else:
        return False
    
def prepare_bm(filter: Filter):
    if os.path.exists("BlackMarket.db"):
        conn = sqlite3.connect(f"BlackMarket.db", isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
        df = pd.read_sql_query("SELECT * FROM Data", conn)
        df = df.sort_values(by=["id","quality"])
        df = df[df.quality.isin(filter.qualities)]
        df = df[df["id"].apply(regex_filter, filters = filter.tiers)]
        sell = df.groupby("id")["sell_min"].min().to_frame()
        buy = df.groupby("id")["buy_max"].min().to_frame()
        df = sell.merge(df[["id", "enchant", "sell_min", "buy_max"]], on="id", suffixes=("", "_y")).drop("sell_min_y", axis=1).drop_duplicates()
        df = buy.merge(df[["id", "enchant", "sell_min", "buy_max"]], on="id", suffixes=("", "_y")).drop("buy_max_y", axis=1).drop_duplicates()
        return df
    else:
        raise Exception("BlackMarket.db does not exists")

def prepare_royal(location, filter: Filter):
    if os.path.exists(f"{location}.db"):
        conn = sqlite3.connect(f"{location}.db", isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
        df = pd.read_sql_query("SELECT * FROM Data", conn)
        df = df.sort_values(by=["id","quality"])
        df = df[df.quality.isin(filter.qualities)]
        df = df[df["id"].apply(regex_filter, filters = filter.tiers)]
        sell = df.groupby("id")["sell_min"].mean().to_frame()
        buy = df.groupby("id")["buy_max"].mean().to_frame()
        df = sell.merge(df[["id", "enchant", "sell_min", "buy_max"]], on="id", suffixes=("", "_y")).drop("sell_min_y", axis=1).drop_duplicates()
        df = buy.merge(df[["id", "enchant", "sell_min", "buy_max"]], on="id", suffixes=("", "_y")).drop("buy_max_y", axis=1).drop_duplicates()
        return df
    else:
        raise Exception(f"{location}.db does not exists")

def compare(bm_df, royal_df, filter: Filter):
    merge = royal_df.merge(bm_df, how = "left", on = ["id", "enchant"], suffixes = ("_rl","_bm")).drop_duplicates()

    merge["diff_quick_sell"] = (merge["buy_max_bm"] * (1-0.04)) / merge["sell_min_rl"]
    merge["diff_sell_order"] = (merge["sell_min_bm"] * (1-0.04-0.025)) / merge["sell_min_rl"]
    merge["quick_sell_desired"] = (merge["buy_max_bm"] / (filter.diff_show) * (1 - 0.04)).fillna(0).astype(np.int64, errors='ignore')
    merge["sell_order_desired"] = (merge["sell_min_bm"] / (filter.diff_show) * (1 - 0.065)).fillna(0).astype(np.int64, errors='ignore')
    merge[["sell_min_rl", "sell_min_bm", "buy_max_bm"]] = merge[["sell_min_rl", "sell_min_bm", "buy_max_bm"]].fillna(0).astype(np.int64, errors='ignore')
    merge = merge[merge[["diff_sell_order", "diff_quick_sell"]].notna().any(axis=1)]
    merge = items.merge(merge, how = "right", on = "id")

    return merge
    