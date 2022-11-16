from flask import Flask, request
from parse import parse as parseManifest, buildDT
from browse import browse
import yaml, json

app = Flask(__name__)

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
def resolve():
  if request.headers.get('Content-Type') != 'text/yaml':
    return "Body data is not YA", 400

  sites = request.args.get('sites')

  if sites == None:
    return "Sites must be provided", 400

  sites = sites.split(',')

  manifest = yaml.safe_load(request.data)
  dependencies = buildDT(parseManifest(manifest))
  try:
    return json.dumps(browse(dependencies, sites))
  except Exception as e:
    return str(e), 400

