import yaml, json

yaml_path = "deployment.yaml"
json_path = "_definitions.json"

def get_definition_properties(uri):
    if uri[0] == '#':
        uri = uri.split('/')[2]
    with open(json_path) as file:
        definitions = json.loads(file.read())["definitions"]

        try:
            definition = definitions[uri]
            return (definition["properties"])
        except:
            print("Definition " + uri + " missing from definitions")
            exit(1)

def dive_manifest(currentNode, currentRef, currentDepth = 0):
    if type(currentNode) is dict:
        for key, value in currentNode.items():
            print("Current ref: " + currentRef)
            print(' '*currentDepth + key)
            if type(value) is dict or type(value) is list:
                definition = get_definition_properties(currentRef)
                currentNodeProp = definition[key]

                if 'items' in currentNodeProp:
                  if '$ref' in currentNodeProp["items"]:
                    dive_manifest(value, currentNodeProp["items"]["$ref"], currentDepth + 1)
                elif '$ref' in currentNodeProp:
                  dive_manifest(value, currentNodeProp["$ref"], currentDepth + 1)


    elif type(currentNode) is list:
        for value in currentNode:
            dive_manifest(value, currentRef, currentDepth + 1)


def main():
    with open(yaml_path) as file:
        manifest = yaml.safe_load(file)
        try:
            kind = manifest["kind"]
            apiVersion = manifest["apiVersion"]
        except:
            print("Kind or apiVersion missing from manifest, quitting")
            exit(1)

        if apiVersion == "v1":
          apiVersion = "core.v1"
        else:
          apiVersion = apiVersion.replace("/", ".")

        ref = "io.k8s.api." + apiVersion

        uri = ref + "." + kind

        dive_manifest(manifest, uri)
        
#        for name, prop in props.items():
#          if name == "apiVersion" or name == "kind" or name == "metadata":
#            continue
#          if name in manifest:
#            print(prop)

    


if __name__ == "__main__":
    main()