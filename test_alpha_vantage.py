import requests
import json

# Test the exact endpoint the user said works
url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=RELIANCE.BSE&outputsize=full&apikey=demo'

print('Testing exact endpoint user provided...')
print(f'URL: {url}')

try:
    response = requests.get(url, timeout=30)
    print(f'Status Code: {response.status_code}')
    data = response.json()
    
    keys = list(data.keys())
    print(f'Response keys: {keys}')
    
    if 'Information' in data:
        print(f'Information: {data["Information"]}')
    
    if 'Meta Data' in data:
        print(f'Meta Data: {data["Meta Data"]}')
    
    # Find time series key
    for key in keys:
        if 'Time Series' in key:
            ts = data[key]
            print(f'Found {key} with {len(ts)} entries')
            # Show first entry
            first_date = list(ts.keys())[0]
            print(f'First entry ({first_date}): {ts[first_date]}')
            break
except Exception as e:
    print(f'Error: {e}')
