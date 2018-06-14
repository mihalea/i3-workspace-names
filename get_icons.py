import json
import requests
r = requests.get('https://raw.githubusercontent.com/FortAwesome/Font-Awesome/master/advanced-options/metadata/icons.json')
j = json.loads(r.text)

print("icons = {")

for i in j:
    print("\"%s\": \"\\u%s\"," % (i.replace('-', ' '), j[i]['unicode']))


print("}")
