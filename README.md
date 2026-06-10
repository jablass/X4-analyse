# Theoretical maximum average resource respawn per hour
[**View Results on Google Sheets**](https://docs.google.com/spreadsheets/d/1s8Q6Mee9K6SXmWFGr_mVOvv8X93FvGrtI8tmoLjRszc/edit?usp=sharing)
## Setup & Usage

- Run awk script on you save file and output into `data/resourceNodeCounts.txt`
```bash
gawk -f scrapeSave.awk data/save.xml > data/resourceNodeCounts.txt
```
- Put `regionyields.xml` from game files into `data`
- Run python script `calcReplenishRate.py`
- Find csv with results in `data/sector_ware_replenish_rates.csv` 
