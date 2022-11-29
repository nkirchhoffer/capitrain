from flask import Flask, request
from parse import parse as parseManifest, buildDT
from browse import browse
import yaml, json, os, sys

app = Flask(__name__)
site_id = os.environ["SITE_ID"]

@app.post("/")
@app.errorhandler(400)
def parse():
  content_type = request.headers.get('Content-Type')
  if content_type != 'text/yaml':
      return "Body data is not YAML text", 400
  manifest = yaml.safe_load(request.data)
  dependencies = parseManifest(manifest)
  return json.dumps(buildDT(dependencies))

@app.post("/resolve")
@app.errorhandler(400)
@app.errorhandler(404)
def resolve():
  if request.headers.get('Content-Type') != 'text/yaml':
    return "Body data is not YAML", 400

  sites = request.args.get('sites')

  if sites == None:
    return "Sites must be provided", 400

  locations = sites.split(',')

  manifest = yaml.safe_load(request.data)
  dependencies = parseManifest(manifest)
  dt = buildDT(dependencies)
  try:
    computed_dt = browse(lookup(dt), locations)
  except Exception as e:
    return str(e), 400
  
  missing_deps = []
  for key, category in computed_dt.items():
    for res in category:
      if res['site'] == None:
        missing_deps.append('{0}/{1}'.format(key, res['name']))
  
  if len(missing_deps) > 0:
    return 'Dependencies {0} not located on sites [{1},{2}]'.format(', '.join(missing_deps), site_id, sites), 400
  return json.dumps(computed_dt)

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
