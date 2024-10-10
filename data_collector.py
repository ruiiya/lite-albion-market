import sqlite3
import photon
import json
from datetime import datetime, timezone
from dateutil.parser import parse
from common import locations

db_data_collector = None
PLAYER_LOCATION = None

def parse_order(data):
    res = []
    for i in data:
        j = json.loads(i)
        # print(j)
        itemid, price, quality, enchant = j["ItemTypeId"], j["UnitPriceSilver"], j["QualityLevel"], j["EnchantmentLevel"]
        res.append((itemid, price, quality, enchant))
    return res

def do_sell_order(parameters):
    global db_data_collector
    if db_data_collector is None:
        print("[WARN] [SELL_ORDER] Unkown player location")
        return
    data = parse_order(parameters[0])
    try:
        for i in data:
            itemid, price, quality, enchant = i
            price = price // 10000
            cur = db_data_collector.cursor()
            entry = cur.execute("select * from Data Where (id = ? and quality = ?)", (itemid,quality)).fetchone()
            if entry is None:
                cur.execute("insert into Data(id,quality,sell_min,sell_min_datetime,enchant) values(?,?,?,?,?)", (itemid,quality, price, datetime.now(timezone.utc),enchant))
                db_data_collector.commit()
                print(f"[INFO:{PLAYER_LOCATION}] Add {itemid} to database")
            else:
                if entry[3] is None:
                    cur.execute("update Data set sell_min = ?, sell_min_datetime = ? where (id = ? and quality = ?)", (price, datetime.now(timezone.utc), itemid, quality))
                    print(f"[INFO:{PLAYER_LOCATION}] [SELL_ORDER] Update price {entry[0]} to {price}")
                    db_data_collector.commit()
                elif (datetime.now(timezone.utc) - parse(entry[5])).total_seconds() / 60 > 30:
                    cur.execute("update Data set sell_min = ?, sell_min_datetime = ? where (id = ? and quality = ?)", (price, datetime.now(timezone.utc), itemid, quality))
                    print(f"[INFO:{PLAYER_LOCATION}] [SELL_ORDER] Change outdated order {entry[0]}")
                    db_data_collector.commit()
                elif entry[3] is None or price < entry[3]:
                    cur.execute("update Data set sell_min = ?, sell_min_datetime = ? where (id = ? and quality = ?)", (price, datetime.now(timezone.utc), itemid, quality))
                    print(f"[INFO:{PLAYER_LOCATION}] [SELL_ORDER] Update price {entry[0]} from {entry[3] or 0} to {price}")
                    db_data_collector.commit()
        print(f"[INFO:{PLAYER_LOCATION}] [SELL_ORDER] Done {len(data)} ingests")
    except Exception as e:
        print(e)
    pass

def do_buy_order(parameters):
    global db_data_collector
    if db_data_collector is None:
        print("[WARN] [SELL_ORDER] Unkown player location")
        return
    data = parse_order(parameters[0])
    try:
        for i in data:
            itemid, price, quality, enchant = i
            price = price // 10000
            cur = db_data_collector.cursor()
            entry = cur.execute("select * from Data Where (id = ? and quality = ?)", (itemid,quality)).fetchone()
            # print(entry)
            if entry is None:
                cur.execute("insert into Data(id,quality,buy_max,buy_max_datetime,enchant) values(?,?,?,?,?)", (itemid,quality, price, datetime.now(timezone.utc),enchant))
                db_data_collector.commit()
                print(f"[INFO:{PLAYER_LOCATION}] Add {itemid} to database")
            else:
                if entry[4] is None:
                    cur.execute("update Data set buy_max = ?, buy_max_datetime = ? where (id = ? and quality = ?)", (price, datetime.now(timezone.utc), itemid, quality))
                    print(f"[INFO:{PLAYER_LOCATION}] [BUY_ORDER] Update price {entry[0]} to {price}")
                    db_data_collector.commit()
                elif (datetime.now(timezone.utc) - parse(entry[6])).total_seconds() / 60 > 30:
                    cur.execute("update Data set buy_max = ?, buy_max_datetime = ? where (id = ? and quality = ?)", (price, datetime.now(timezone.utc), itemid, quality))
                    print(f"[INFO:{PLAYER_LOCATION}] [BUY_ORDER] Change outdated order {entry[0]}")
                    db_data_collector.commit
                elif price > entry[4]:
                    cur.execute("update Data set buy_max = ?, buy_max_datetime = ? where (id = ? and quality = ?)", (price, datetime.now(timezone.utc), itemid, quality))
                    print(f"[INFO:{PLAYER_LOCATION}] [BUY_ORDER] Update price {entry[0]} from {entry[4] or 0} to {price}")
                    db_data_collector.commit()
        print(f"[INFO:{PLAYER_LOCATION}] [BUY_ORDER] Done {len(data)} ingests")
    except Exception as e:
        print(e)
    pass

def join(parameters):
    global db_data_collector, PLAYER_LOCATION
    PLAYER_LOCATION = parameters[8]
    db_data_collector = None if PLAYER_LOCATION not in locations else sqlite3.connect(f"{locations[PLAYER_LOCATION]}.db", check_same_thread=False)
    if db_data_collector:
        db_data_collector.execute(f"""
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
    p = photon.Photon()
    p.map(75, do_sell_order)
    p.map(76, do_buy_order)
    p.map(2, join)

    input()

if __name__ == "__main__":
    main()