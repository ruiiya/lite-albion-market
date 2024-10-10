from dotenv import load_dotenv
import os

load_dotenv()

locations = {
    "0007": "Thetford",
    "1002": "Lymhurst",
    "2004": "Bridgewatch",
    "3008": "Martlock",
    "4002": "FortSterling",
    "3005": "Caerleon",
    "3003": "BlackMarket",
    "0301": "Thetford",
    "1301": "Lymhurst",
    "2301": "Bridgewatch",
    "3301": "Martlock",
    "4301": "FortSterling",
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

class Filter:
    def __init__(self) -> None:
        self.tiers = os.getenv("SET_FILTER_TIER")
        self.diff_show = float(os.getenv("LEAST_DIFF_SHOW"))
        self.qualities = [int(i) for i in os.getenv("SET_FILTER_QUALITY").split(",")]
    
    def set_tier(self, tiers):
        self.tiers = tiers
    
    def set_quality(self, qualities):
        self.qualities = qualities

    def set_diff(self, diff):
        self.diff_show = diff

def re_tiers(tiers):
    if tiers == "" or tiers is None:
        return ".*"
    tl = tiers.split(" ")
    re_l = []
    d = {}
    for t in tl:
        tier, enchant = t.split(".")
        if enchant is None:
            enchant = [0,1,2,3,4]
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