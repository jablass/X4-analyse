import csv
import json
import re

with open('data/mapNames.json', 'r') as jsonFile:
    map_names_structure = json.load(jsonFile)

# get sector macro to ingame name mapping 
sector_names = {}
for cluster in map_names_structure['data']:
    for sector in cluster['sectors']:
        sector_names[sector['name'].lower()] = sector['qsnaAttributes']['name']

# get max yield and respawndelay for each ware and node type
pattern = r'id="([^"]+)"|ware="([^"]+)"|respawndelay="([^"]+)"|yield="([^"]+)"'
nodetype_properties = {}
with open('data/regionyields.xml') as xmlfile:
    for line in xmlfile:
        if line.startswith(r'  <definition id="'):
            matches = re.findall(pattern, line)
            nodetype = matches[0][0]
            nodetype_properties[nodetype] = {}
            for m in matches:
                if m[1]: nodetype_properties[nodetype]["ware"] = m[1]
                if m[2]: nodetype_properties[nodetype]["respawndelay_min"] = int(m[2]) # minutes
                if m[3]: nodetype_properties[nodetype]["yield_max"] = int(m[3])

# get number of occurences of each node type per sector
sector_resource_nodes_counts = {}
with open('data/resourceNodeCounts.txt', 'r') as file:
    sector = None
    for line in file:
        if line[0] != '\t':
            sector = line.strip()
        else:
            nodetype, num = line.split()
            sector_resource_nodes_counts.setdefault(sector, {nodetype : None})
            sector_resource_nodes_counts[sector][nodetype] = int(num)

# sum of expectation value of yields per hour for each sector and ware
# this is a theoretical maximum average value that assumes
# that every node is instantly mined as soon as it spawns 
sector_ware_replenish_rates = {} # in max_yield/hour
for resource_sector, nodetypes_count in sector_resource_nodes_counts.items():
    sector_name = sector_names[resource_sector]
    sector_ware_replenish_rates.setdefault(sector_name, {})
    for nodetype, num in nodetypes_count.items():
        ware = nodetype_properties[nodetype]["ware"]
        # divide max possible yield by 2 to get expectation value of uniform distribution
        replenish_rate_h = round(num * nodetype_properties[nodetype]["yield_max"] 
                               / 2 / nodetype_properties[nodetype]["respawndelay_min"] * 60)
        sector_ware_replenish_rates[sector_name].setdefault(ware, 0)
        sector_ware_replenish_rates[sector_name][ware] += replenish_rate_h

for sector_name, ware_replenish_rate in sector_ware_replenish_rates.items():
    for ware, replenish_rate in ware_replenish_rate.items():
        print(sector_name, "\t", ware, replenish_rate)

#write as csv
columns = ['helium', 'hydrogen', 'methane', 'ice', 'ore', 'silicon', 'nividium', 'rawscrap', 'rawkhaakscrap']
with open("data/sector_ware_replenish_rates.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["sector"] + columns)
    for sector, ware_rates in sector_ware_replenish_rates.items():
        writer.writerow([sector] + [ware_rates.get(col, "") for col in columns])
