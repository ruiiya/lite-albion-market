from common import shortname, locations, Filter
import csv_converter
from bulk_market import prepare_bm, prepare_royal, compare

def main():

    ao_filter = Filter()

    while True:
        a = input().strip().split(" ")

        try:
            if a[0] == "csv":
                ls = list(filter(None,[shortname.get(l, l) for l in a[1::]]))
                if len(ls) == 0:
                    ls = locations.values()
                csv_converter.convert(ls, ao_filter)

            if a[0] == "set":
                try:
                    if a[1] == "tier":
                        ao_filter.set_tier(" ".join(a[2::]))
                    elif a[1] == "quality":
                        qualities = [int(i) for i in a[2::]]
                        if len(qualities) == 0:
                            qualities = [1,2,3,4,5]
                        ao_filter.set_quality(qualities)
                    elif a[1] == "diff":
                        ao_filter.set_diff(float(a[2]))
                except Exception as e:
                    print("[Error] set: Unkown command - %s" % e)
            
            if a[0] == "bulk":
                ls = list(filter(None,[shortname.get(l, l) for l in a[1::]]))

                try:
                    if len(ls) == 0:
                        print("[ERROR] bulk: Unkown command")
                    else:
                        df_bm = prepare_bm(ao_filter)
                        df_rl = prepare_royal(ls[0], ao_filter)
                        df = compare(df_bm, df_rl, ao_filter)
                        dfqs = df[["name", "enchant", "sell_min_rl", "buy_max_bm", "diff_quick_sell", "quick_sell_desired"]].sort_values(
                            by="diff_quick_sell",ascending=False)
                        dfso = df[["name", "enchant", "sell_min_rl", "sell_min_bm", "diff_sell_order", "sell_order_desired"]].sort_values(
                            by="diff_sell_order",ascending=False)
                        print(dfqs[dfqs["diff_quick_sell"] > ao_filter.diff_show])
                        print(dfso[dfso["diff_sell_order"] > ao_filter.diff_show])
                except Exception as e:
                    print("[ERROR] bulk:",e)

            if a[0] == "exit":
                break
        except Exception as e:
            print("[Error] Unkown command - %s" % e)

if __name__ == "__main__":
    main()