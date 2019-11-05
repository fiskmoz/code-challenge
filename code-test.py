import requests
import json
from termcolor import colored
import colorama

### make requests to get percent values from the scb API. the 3 values that are important are [region , year, value] ###
session = requests.Session()
query = json.loads(open('query.json').read())
response = requests.post("http://api.scb.se/OV0104/v1/doris/sv/ssd/START/ME/ME0104/ME0104D/ME0104T4", json=query)
response_json = json.loads(response.content.decode('utf-8-sig'))

### find all unique years to check results from. ###
possible_years = []
for data in response_json['data']:
    if  data['key'][1] in possible_years:
        continue
    possible_years.append(data['key'][1])
possible_years.sort()

### initialize help arrays depending on no. of election years ###
highest_values = ["0"] * len(possible_years)
region_codes_with_highest = [""] * len(possible_years)
region_names_with_highest = [""] * len(possible_years)

### enumerate all region, year, value pairs. ###
### store the highest value for a year and the corresponding region when found. ###
### data['values'][0] = the percent. api gives a list with a single item. ###
### data['key'][0] = region code. ###
### data['key'][1] = year. ###
for data in response_json['data']: 
    for index, year in enumerate(possible_years):
        if not data['key'][1] == year:
            continue
        if data['values'][0] == "..":
            continue
        if float(data['values'][0]) > float(highest_values[index]):
            highest_values[index] = data['values'][0]
            region_codes_with_highest[index] = data['key'][0]
        if float(data['values'][0]) == float(highest_values[index]):
            if str(region_codes_with_highest[index]) == data['key'][0]:
                continue
            region_codes_with_highest[index] = str(region_codes_with_highest[index]) + ',' + data['key'][0]
        break

### make a request to get the region code to region name mapping. ###
response = requests.get("http://api.scb.se/OV0104/v1/doris/sv/ssd/START/ME/ME0104/ME0104D/ME0104T4")
response_json = json.loads(response.content.decode('utf-8-sig'))

### ['variables'] contains multiple json objects, we want the first one. ### 
name_mapping = []
for mapping in response_json['variables']:
    name_mapping = json.loads(json.dumps(mapping))
    break

### map the region codes to region names and append the names array. ###
for with_highest, region_code in enumerate(region_codes_with_highest):
    region_codes = region_code.split(',')
    for region_code_multiple in region_codes:
        for json_index, region_code_json in enumerate(name_mapping['values']):
            if not region_code_multiple == region_code_json:
                continue
            region_names_with_highest[with_highest] = region_names_with_highest[with_highest] + "  " + name_mapping['valueTexts'][json_index]
            break

### print with fun colors.  :) ###  
colorama.init()
for index, year in enumerate(possible_years): 
    print(colored("["+year+"]", 'cyan') + colored(region_names_with_highest[index], 'green') + "  " + colored(highest_values[index] + "%  ", 'yellow'))

print(region_codes_with_highest)