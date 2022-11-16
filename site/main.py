from flask import Flask, request
import json
import os

app = Flask(__name__)

site_id = os.environ["SITE_ID"]

resources_path = "resources.json"
with open(resources_path) as file:
    resources = json.loads(file.read())

@app.post('/checkout')
@app.errorhandler(400)
def checkout():
    if(not request.is_json): 
        return "Input should be application/json", 400 
    deps = request.get_json()
    return lookup(deps)

def has_resource(resName, name):
    if resName not in resources:
        return False
    if name in resources[resName]:
        return True
    return False

def lookup(deps):
    for resName, value in deps.items():
        for i in range(len(value)):
            resource = deps[resName][i]
            if has_resource(resName, resource['name']):
                if deps[resName][i]['site'] != None:
                    site = deps[resName][i]['site']
                    deps[resName][i]['site'] = list([site, site_id])
                else:
                    deps[resName][i]['site'] = site_id
    return deps

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
