import yaml, json, requests

with open('sites.yaml') as file:
    sites = yaml.safe_load(file)

def browse(dt, inputSites): 
    for site in inputSites:
        if site not in sites['sites']:
           raise Exception('Site ', site, ' is not registered') 
        
        print(sites['sites'][site])
        result = requests.post(checkout_endpoint(sites['sites'][site]['url']), data=json.dumps(dt), headers={
            'Content-Type': 'application/json'
        })
        dt = result.json()
    return dt

def checkout_endpoint(url):
    return url + '/checkout'
