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

# boundary names
boundary_pattern = r'id="([^"]+)"'
boundary_names = []
with open('data/regionyields.xml') as xmlfile:
    for line in xmlfile:
        if line.startswith(r'    <boundary id="'):
            matches = re.findall(boundary_pattern, line)
            boundary_names.append(matches[0])
print(boundary_names)

# gatherspeeds
gatherspeed_pattern = r'id="([^"]+)"|rating="([^"]+)"'
gatherspeed_rating = {}
with open('data/regionyields.xml') as xmlfile:
    for line in xmlfile:
        if line.startswith(r'    <gatherspeed id="'):
            matches = re.findall(gatherspeed_pattern, line)
            gatherspeed_rating[matches[0][0]] = int(matches[1][1])
print(gatherspeed_rating)

# yield
yield_pattern = r'id="([^"]+)"'
yield_ware_pattern = r'id="([^"]+)"|yield="([^"]+)"|respawndelay="([^"]+)"'
yieldid_properties = {}
current_yield_sting = None
with open('data/regionyields.xml') as xmlfile:
    for line in xmlfile:
        if line.startswith(r'    <yield id="'):
            matches = re.findall(yield_pattern, line)
            current_yield_sting = matches[0]
        if line.startswith(r'      <ware id="') and current_yield_sting:
            matches = re.findall(yield_ware_pattern, line)

            ware = matches[0][0]
            yield_max = matches[1][1]
            respawndelay_min = matches[2][2]
            yieldid = ware + "_" + current_yield_sting

            yieldid_properties[yieldid] = {}
            yieldid_properties[yieldid]["ware"] = ware
            yieldid_properties[yieldid]["respawndelay_min"] = int(respawndelay_min)
            yieldid_properties[yieldid]["yield_max"] = int(yield_max)
print(yieldid_properties)

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
sector_ware_max_yields = {} # sum of max possble yields
sector_ware_rating = {} # average rating

for resource_sector, nodetypes_count in sector_resource_nodes_counts.items():
    sector_name = sector_names[resource_sector]
    sector_ware_replenish_rates.setdefault(sector_name, {})
    sector_ware_max_yields.setdefault(sector_name, {})
    sector_ware_rating.setdefault(sector_name, {})
    for nodetype, num in nodetypes_count.items():
        splits = nodetype.split("_")
        boundary = splits[0] + "_" + splits[1]
        yield_id = splits[2] + "_" + splits[3]
        gatherspeed_string = splits[4]

        ware = yieldid_properties[yield_id]["ware"]
        max_yield = yieldid_properties[yield_id]["yield_max"]

        # divide max possible yield by 2 to get expectation value of uniform distribution
        replenish_rate_h = round(num *  max_yield / 2 / yieldid_properties[yield_id]["respawndelay_min"] * 60)
        sector_ware_replenish_rates[sector_name].setdefault(ware, 0)
        sector_ware_replenish_rates[sector_name][ware] += replenish_rate_h

        sector_ware_max_yields[sector_name].setdefault(ware, 0)
        sector_ware_max_yields[sector_name][ware] += max_yield
        sector_ware_rating[sector_name].setdefault(ware, 0)
        sector_ware_rating[sector_name][ware] += max_yield * gatherspeed_rating[gatherspeed_string]
    
    # calculate average star rating    
    for ware, sum_yield in sector_ware_max_yields[sector_name].items():
        sector_ware_rating[sector_name][ware] = round(sector_ware_rating[sector_name][ware]/sum_yield/3, 2)

for sector_name, ware_replenish_rate in sector_ware_replenish_rates.items():
    for ware, replenish_rate in ware_replenish_rate.items():
        print(sector_name, "\t", ware, replenish_rate, sector_ware_max_yields[sector_name][ware], sector_ware_rating[sector_name][ware])

#write as csv
columns = ['helium', 'hydrogen', 'methane', 'ice', 'ore', 'silicon', 'nividium', 'rawscrap', 'rawkhaakscrap']
with open("data/sector_ware_replenish_rates.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["sector"] + columns)
    for sector, ware_rates in sector_ware_replenish_rates.items():
        writer.writerow([sector] + [ware_rates.get(col, "") for col in columns])

columns = ['helium', 'hydrogen', 'methane', 'ice', 'ore', 'silicon', 'nividium', 'rawscrap', 'rawkhaakscrap']
with open("data/sector_ware_rates_rating_max.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["sector"] + [item 
                                  for col in columns
                                  for item in (col + "_rate", col + "_rating", col + "_max")
                                  ])
    for sector, ware_rates in sector_ware_replenish_rates.items():
        writer.writerow([sector] + [item 
                                    for col in columns
                                    for item in (
                                        ware_rates.get(col, ""),
                                        sector_ware_rating[sector].get(col, ""),
                                        sector_ware_max_yields[sector].get(col, ""))
                                        ])