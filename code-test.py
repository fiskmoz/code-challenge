import requests
import json
from termcolor import colored

# WHICH YEARS TO WORK WITH
possible_years = ["1973", "1976", "1979", "1982", "1985", "1988", "1991", "1994", "1998", "2002", "2006", "2010", "2014"]
highest_values = ["0"] * len(possible_years)
region_codes_with_highest = [""] * len(possible_years)
region_names_with_highest = [""] * len(possible_years)

# DO REQUEST TO GET PERCENT VALUES FROM SCB API, THE 3 VALUES THAT ARE IMPORTANT ARE [REGION, YEAR, VALUE]
session = requests.Session()
query = json.loads(open('query.json').read())
response = requests.post("http://api.scb.se/OV0104/v1/doris/sv/ssd/START/ME/ME0104/ME0104D/ME0104T4", json=query)
response_json = json.loads(response.content.decode('utf-8-sig'))

# ENUMERATE ALL REGION, YEAR, VALUE PAIRS. STORE THE HIGHEST VALUE FOR A YEAR AND CORRESPONDING REGION WHEN FOUND.
# data['values'][0] = THE PERCENT. FROM API IS GIVEN A LIST WITH A SINGLE ITEM.
# data['key'][0] = REGION CODE.
# data['key'][1] = YEAR.
for data in response_json['data']: 
    for index, year in enumerate(possible_years):
        if not data['key'][1] == year:
            continue
        if data['values'][0] == "..":
            continue
        if float(data['values'][0]) > float(highest_values[index]):
            highest_values[index] = data['values'][0]
            region_codes_with_highest[index] = data['key'][0]
        break

# REQUEST TO GET THE REGION CODE TO REGION NAME MAPPING
response = requests.get("http://api.scb.se/OV0104/v1/doris/sv/ssd/START/ME/ME0104/ME0104D/ME0104T4")
response_json = json.loads(response.content.decode('utf-8-sig'))

# ['variables'] CONTAINS MULTIPLE JSONS OBJECTS AS RESULTS. WE WANT THE FIRST ONE.
name_mapping = []
for mapping in response_json['variables']:
    name_mapping = json.loads(json.dumps(mapping))
    break

# MAP THE REGION CODES TO REGION NAMES AND APPEND THE NAMES ARRAY.
for with_highest, region_code in enumerate(region_codes_with_highest):
    for json_index, region_code_json in enumerate(name_mapping['values']):
        if not region_code == region_code_json:
            continue
        region_names_with_highest[with_highest] = name_mapping['valueTexts'][json_index]
        break

# PRINT WITH FUN COLORS :) 
for index, year in enumerate(possible_years): 
    print(colored("["+year+"]", 'cyan') + " " + colored(region_names_with_highest[index]+" : ", 'green') + colored(highest_values[index] + "% ", 'yellow'))