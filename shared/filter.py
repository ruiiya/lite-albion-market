"""
Filter utility for market data handling.
Used by both collector and market_app components.
"""
import re
from .constants import DEFAULT_TIER, DEFAULT_DIFF_SHOW, DEFAULT_QUALITIES

class Filter:
    """Filter class for market data queries and display."""
    
    def __init__(self, tiers=None, diff_show=None, qualities=None):
        """Initialize filter with optional custom values or defaults."""
        self.tiers = tiers if tiers is not None else DEFAULT_TIER
        self.diff_show = diff_show if diff_show is not None else DEFAULT_DIFF_SHOW
        self.qualities = qualities if qualities is not None else DEFAULT_QUALITIES.copy()
    
    def set_tier(self, tiers):
        """Set the tier filter."""
        self.tiers = tiers
    
    def set_quality(self, qualities):
        """Set the quality filter."""
        self.qualities = qualities

    def set_diff(self, diff):
        """Set the minimum price difference to show."""
        self.diff_show = diff
        
    def __str__(self):
        """String representation of the filter."""
        return f"Filter(tiers={self.tiers}, qualities={self.qualities}, diff_show={self.diff_show})"

def re_tiers(tiers):
    """
    Convert tiers string (e.g. "4.0 5.1") to regex pattern for item filtering.
    
    Args:
        tiers: String describing tiers to filter for (e.g. "4.0 5.1")
        
    Returns:
        Regex pattern string
    """
    if tiers == "" or tiers is None:
        return ".*"
    tl = tiers.split(" ")
    re_l = []
    d = {}
    for t in tl:
        tier, enchant = t.split(".")
        if enchant is None:
            enchant = [0, 1, 2, 3, 4]
        if tier in d:
            d[tier].append(enchant)
        else:
            d[tier] = [enchant]
    for k in d.keys():
        contain_zero = ("0" in d[k])
        if contain_zero: 
            d[k].remove("0")
        re_s = "(^T%s[^@]+%s$)" % (k, "" if len(d[k]) == 0 else f"(@[{''.join(d[k])}]){'?' if contain_zero else ''}")
        re_l.append(re_s)
    return "|".join(re_l)

def regex_filter(val, filters):
    """
    Apply tier regex filter to an item ID.
    
    Args:
        val: The item ID to test
        filters: The tier filter string
        
    Returns:
        True if item matches the filter, False otherwise
    """
    if val:
        mo = re.search(re_tiers(filters), val)
        if mo:
            return True
        else:
            return False
    else:
        return False