import sqlite3
import photon
import json
from datetime import datetime, timezone
import os
import csv_converter
from bulk_market import prepare_bm, prepare_royal, compare

locations = {
    "0007": "Thetford",
    "1002": "Lymhurst",
    "2004": "Bridgewatch",
    "3008": "Martlock",
    "4002": "FortSterling",
    "3005": "Caerleon",
    "3003": "BlackMarket"
}

shortname = {
    "bw": "Bridgewatch",
    "tf": "Thetford",
    "ml": "Martlock",
    "lh": "Lymhurst",
    "fs": "FortSterling",
    "cl": "Caerleon",
    "bm": "BlackMarket"
}

PLAYER_LOCATION = None
db = None
filters = ""
qualities = [1,2,3,4,5]

def parse_order(data):
    res = []
    for i in data:
        j = json.loads(i)
        # print(j)
        itemid, price, quality, enchant = j["ItemTypeId"], j["UnitPriceSilver"], j["QualityLevel"], j["EnchantmentLevel"]
        res.append((itemid, price, quality, enchant))
    return res

def do_sell_order(parameters):
    global db
    if db is None:
        print("[WARN] [SELL_ORDER] Unkown player location")
        return
    data = parse_order(parameters[0])
    try:
        for i in data:
            itemid, price, quality, enchant = i
            price = price // 10000
            cur = db.cursor()
            entry = cur.execute("select * from Data Where (id = ? and quality = ?)", (itemid,quality)).fetchone()
            if entry is None:
                cur.execute("insert into Data(id,quality,sell_min,sell_min_datetime,enchant) values(?,?,?,?,?)", (itemid,quality, price, datetime.now(timezone.utc),enchant))
                db.commit()
                print(f"[INFO:{PLAYER_LOCATION}] Add {itemid} to database")
            else:
                if entry[3] is None or price < entry[3]:
                    cur.execute("update Data set sell_min = ?, sell_min_datetime = ? where (id = ? and quality = ?)", (price, datetime.now(timezone.utc), itemid, quality))
                    print(f"[INFO:{PLAYER_LOCATION}] [SELL_ORDER] Update price {entry[0]} from {entry[3] or 0} to {price}")
                    db.commit()
                    entry = cur.execute("select * from Data Where (id = ?)", (itemid,)).fetchone()
        print(f"[INFO:{PLAYER_LOCATION}] [SELL_ORDER] Done {len(data)} ingests")
    except Exception as e:
        print(e)
    pass

def do_buy_order(parameters):
    global db
    if db is None:
        print("[WARN] [SELL_ORDER] Unkown player location")
        return
    data = parse_order(parameters[0])
    try:
        for i in data:
            itemid, price, quality, enchant = i
            price = price // 10000
            cur = db.cursor()
            entry = cur.execute("select * from Data Where (id = ? and quality = ?)", (itemid,quality)).fetchone()
            # print(entry)
            if entry is None:
                cur.execute("insert into Data(id,quality,buy_max,buy_max_datetime,enchant) values(?,?,?,?,?)", (itemid,quality, price, datetime.now(timezone.utc),enchant))
                db.commit()
                print(f"[INFO:{PLAYER_LOCATION}] Add {itemid} to database")
            else:
                if entry[4] is None or price > entry[4]:
                    cur.execute("update Data set buy_max = ?, buy_max_datetime = ? where (id = ? and quality = ?)", (price, datetime.now(timezone.utc), itemid, quality))
                    print(f"[INFO:{PLAYER_LOCATION}] [BUY_ORDER] Update price {entry[0]} from {entry[4] or 0} to {price}")
                    db.commit()
                    entry = cur.execute("select * from Data Where (id = ?)", (itemid,)).fetchone()
        print(f"[INFO:{PLAYER_LOCATION}] [BUY_ORDER] Done {len(data)} ingests")
    except Exception as e:
        print(e)
    pass

def join(parameters):
    global db, PLAYER_LOCATION
    PLAYER_LOCATION = parameters[8]
    db = None if PLAYER_LOCATION not in locations else sqlite3.connect(f"{locations[PLAYER_LOCATION]}.db", check_same_thread=False)
    if db:
        db.execute(f"""
            create table if not exists Data (
                id TEXT,
                quality int,
                enchant int,
                sell_min int,
                buy_max INTEGER,
                sell_min_datetime DATETIME,
                buy_max_datetime DATETIME
            )
        """)
    print(f"[INFO] Update player location: {PLAYER_LOCATION}")
    pass

def main():
    global db, PLAYER_LOCATION, filters, qualities
    p = photon.Photon()
    p.map(75, do_sell_order)
    p.map(76, do_buy_order)
    p.map(2, join)

    while True:
        a = input().strip().split(" ")
        if a[0] == "csv":
            ls = list(filter(None,[shortname.get(l, l) for l in a[1::]]))
            if len(ls) == 0:
                ls = locations.values()
            csv_converter.convert(locations=ls, filters=filters, qualities=qualities)

        if a[0] == "clear":
            ls = list(filter(None,[shortname.get(l, l) for l in a[1::]]))
            if len(ls) == 0:
                ls = locations.values()
            if db:
                db.close()
                PLAYER_LOCATION, db = None, None
            for l in ls:
                if os.path.exists(f"{l}.db"):
                    os.remove(f"{l}.db")

        if a[0] == "set":
            if len(a) < 3:
                print("[ERROR] set: Unkown command")
            elif a[1] == "tier":
                filters = " ".join(a[2::])
            elif a[1] == "quality":
                qualities = [int(i) for i in a[2::]]

        if a[0] == "bulk":
            ls = list(filter(None,[shortname.get(l, l) for l in a[1::]]))
            try:
                if len(ls) == 0:
                    print("[ERROR] set: Unkown command")
                else:
                    df_bm = prepare_bm(filters, qualities)
                    df_rl = prepare_royal(ls[0], filters, qualities)
                    df = compare(df_bm, df_rl)
                    dfqs = df[["name", "enchant", "sell_min_rl", "buy_max_bm", "diff_quick_sell", "quick_sell_desired"]].sort_values(by="diff_quick_sell",ascending=False)
                    dfso = df[["name", "enchant", "sell_min_rl", "sell_min_bm", "diff_sell_order", "sell_order_desired"]].sort_values(by="diff_sell_order",ascending=False)
                    print(dfqs[dfqs["diff_quick_sell"] > 1.2])
                    print(dfso[dfso["diff_sell_order"] > 1.2])
            except Exception as e:
                print("[ERROR] bulk:",e)

        if a[0] == "exit":
            break

if __name__ == "__main__":
    main()