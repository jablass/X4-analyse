# Theoretical maximum average resource respawn per hour
[**View Results on Google Sheets**](https://docs.google.com/spreadsheets/d/e/2PACX-1vT0UCXIvy-lPUlhDiixayuxFop5omFXGqYU6sUrry-u_vuwk1nKN7cKMMnAKe1elREvl5OmDdED6YYS/pubhtml )
## Setup & Usage

- Run awk script on you save file and output into `data/resourceNodeCounts.txt`
```bash
gawk -f scrapeSave.awk data/save.xml > data/resourceNodeCounts.txt
```
- Put `regionyields.xml` from game files into `data`
- Run python script `calcReplenishRate.py`
- Find csv with results in `data/sector_ware_replenish_rates.csv` 