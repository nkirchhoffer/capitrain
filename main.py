from flask import Flask, request
from parse import parse as parseManifest 
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
  return json.dumps(dependencies)