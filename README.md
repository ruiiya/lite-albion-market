# lite-albion-market 2.0
Simple Albion Market data collector
```py
pip install -r requirements.txt
```
## For data collector
```py
py data_collector.py
```
## For black market flipping
```py
py client.py
```
## Command
```
clear / clear [bw/lh/ml/tf/fs/cl/bm/br]
csv / csv [bw/lh/ml/tf/fs/cl/bm/br]
set tier [3.0/4.1/...]
set quality [1,2,3,4,5]
set diff [num]
bulk [[bw/lh/ml/tf/fs/cl/br]]
```
## Example
```
clear
csv lh ml bm
set tier 6.0 6.1 7.0 7.1
set quality 1 2 3
set diff 1.3
bulk lh ml
```