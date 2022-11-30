# Cheops - Capitrain

This is our implementation of the Cheops mesh services that retrieve dependencies across multiple sites if needed.

## Context

This work is based of the [following paper](https://hal.inria.fr/hal-03770492/document) that introduces the mechanism of a geo-distributed solution, capable of managing clusters located on multiple sites.

## Our implementation

The user sends a Kubernetes YAML manifest (that describes a resource to deploy), and the script sends a response with the different dependencies, presented in a Decision Tree. Once this DT is computed, it is sent to the various Cheops agents on each user-specified site in order to retrieve the location of each dependency.

This system has been created to work as a mesh, each agent knowing all the others.

## Reference

**POST /resolve - Retrieve the dependencies and their locations**

- Request :
  - `Content-Type`: `text/yaml`
  - Body structure :
  ```YAML
  version: apps/v1
  kind: Deployment
  metadata:
    name: nginx
  spec:
    containers:
    - name: nginx
      image: nginx:1.14.2
      ports:
      - containerPort: 80
      volumeMounts:
      - name: data
        mountPath: /var/www/html
      - name: config
        mountPath: /etc/nginx/nginx.conf
        subPath: /etc/nginx/nginx.conf
      - name: cdn
        mountPath: /var/www/html/assets
        readOnly: true
    volumes:
    - name: data
      persistentVolumeClaim:
        claimName: nginx-data
    - name: config
      persistentVolumeClaim:
        claimName: nginx-config
    - name: cdn
      gcePersistentDisk:
        pdName: app-cdn
  ```
  - The manifest specified in the request must be a valid Kubernetes manifest
- Response :
  - `Content-Type`: `application/json`
  - Response accordingly to the example :

```JSON
  {
	"containers": [
			{
				"name": "nginx",
				"site": "site3"
			}
		],
		"gcePersistentDisk": [
			{
				"name": "app-cdn",
				"site": "site3"
			}
		],
		"persistentVolumeClaim": [
			{
				"name": "nginx-data",
				"site": "site1"
			},
			{
				"name": "nginx-config",
				"site": [
					"site1",
					"site2"
				]
			}
		]
	}
```


**POST /checkout - Check if the dependencies are located on the local cluster**

- Request :
  - `Content-Type`: `application/json`
  - Example of body :
  ```JSON
  {
	"containers": [
		{
			"name": "nginx",
			"site": null
		}
	],
	"gcePersistentDisk": [
		{
			"name": "app-cdn",
			"site": null 
		}
	],
	"persistentVolumeClaim": [
		{
			"name": "nginx-data",
			"site": null 
		},
		{
			"name": "nginx-config",
			"site": null
		}
	]
}
  ```
- Response :
  - `Content-Type`: `application/json`
  - Response accordingly to the request example
  ```JSON
  {
	"containers": [
		{
			"name": "nginx",
			"site": "site3"
		}
	],
	"gcePersistentDisk": [
		{
			"name": "app-cdn",
			"site": "site3"
		}
	],
	"persistentVolumeClaim": [
		{
			"name": "nginx-data",
			"site": "site1"
		},
		{
			"name": "nginx-config",
			"site": [
				"site1",
				"site2"
			]
		}
	]
	}
	```

## Building and hosting the agents

A deployment example is available through the `docker-compose.yaml` file. In order to make it work, you would have to build the image ahead of time with the command :

```bash
docker build -t cheops:latest .
```

The build process is described in the `Dockerfile`.

You can then run the 3 different sites with :

```bash
docker compose up -d
```

As you may see on the `docker-compose.yaml` file, we specify to each agent :
- a list of its own resources (`site/resourcesX.json`) (where X is the site ID)
  - you can edit the resources by adding them with the structure
    ```JSON
    {
      "resourceType": [
        "name1",
        "name2",
        ...
      ]
    }
    ```
- its own ID with the `SITE_ID` environment variable
- a list of all the deployed sites with `sites.yaml`
  - you can edit the sites by specifying its name and URL in YAML :
  ```YAML
  siteId:
    url: http://siteId:5000
  ```

You can add as many agents as required, as long as you add the site to the list and specify some resources for the said site.

## Limitations

Due to conception decisions (that we are **not** accountable for), our implementation tends to be as platform agnostic as possible. We think it may be counterproductive, as a **silver bullet** never exists. Here's why :

Kubernetes, and it's also true for each cloud platform, has its own standard for defining resources, we use the `_definitions.json` file that does not expose the same structure and typology for every resource it features. For example, different volumes can be defined differently, `gcePersistentDisk` has a `pdName` required field, whereas `secret` and `configMap` do not have any required field at all. It is a weakness from the "agnostic" approach : it is not possible to handle every single case, and will not be able to respond to future platform changes as the technology evolves.
- As mentioned in the paper (see [Context](#Context)), an Adapter must be implemented on each platform to translate its specific aspects into a generic YAML that can be parsed by a generic solution. 
- Because of this specific and agnostic approach, some garbage values are returned and we can do nothing about that. There is no **universal** way of knowing whether a field defined in the user-input manifest is a Kubernetes resource or not. It must be implemented **specifically**. For example, `volumeMounts` does **NOT** represent a Kubernetes resource, neither do `volumes`.

We think that this solution should not be generic as a whole, the process of parsing the dependencies being very different based on the platform, and should be considered as such.
As the solution for those different problems requires a change of the initial request and point of view, we decided to **not** implement them as they would not answer to the problem established.

## Contributors

- Nicolas Kirchhoffer <nicolas.kirchhoffer@imt-atlantique.net>
- Yan Imensar <yan.imensar@imt-atlantique.net>
- Florian Dussable <florian.dussable@imt-atlantique.net>
