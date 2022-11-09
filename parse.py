import yaml, json

yaml_path = "deployment.yaml"
json_path = "_definitions.json"

dependencies = []
MAX_DEPTH = 4

def get_definition_properties(uri):
    if uri[0] == '#':
        uri = uri.split('/')[2]
    with open(json_path) as file:
        definitions = json.loads(file.read())["definitions"]

        try:
            definition = definitions[uri]
        
            if 'required' in definition:
                return (definition['properties'], definition['required'])
            else:
                return (definition['properties'], [])
        except:
            print("Definition " + uri + " missing from definitions")
            exit(1)


def dive_manifest(currentNode, currentRef, parentName, currentDepth = 0):
    if currentDepth <= MAX_DEPTH:
        if type(currentNode) is dict:
            (properties, required) = get_definition_properties(currentRef)
            for key, value in currentNode.items():
                currentDef = properties[key]
                if type(value) is str:
                    if key in required:
                        dependencies.append({ str(parentName): value, 'depth': currentDepth })
                    print(dependencies)
                elif type(value) is dict:
                    dive_manifest(value, currentDef['$ref'], key, currentDepth + 1)
                elif type(value) is list:
                    dive_manifest(value, currentDef['items']['$ref'], key, currentDepth + 1)
        elif type(currentNode) is list:
                for value in currentNode:
                    dive_manifest(value, currentRef, parentName, currentDepth + 1)

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

        dive_manifest(manifest, uri, None)

if __name__ == '__main__':
    main()
