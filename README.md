![Drone CI Status](http://drone.connected-data.tools.bbc.co.uk/api/badges/bbc/connected-data-pseudocone/status.svg)

# Pseudocone Component

Pseudocone Component copies the behaviour of [Bristlecone](https://github.com/bbc/connected-data-bristlecone) but instead of reading user actions from UAS it reads from an offline UAS dump. Implemented with gRPC on a default port `50057`.

## Run Service Locally
Before proceeding, set your UAS API key as an environmental variable: `UAS_API_KEY=<key>`. If you do not have a key, then you must request it either from within your team if your team already has a key, or from the UAS team if not.
### With Virtualenv

1. Create a virtualenv, install dependencies:
```
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

2. Run the service:
```
UAS_API_KEY=$UAS_API_KEY python3 -m app.pseudocone
```

### With Docker
1. Build the image:
```
docker build -t pseudocone:latest .
```

2. Run the image:
```
docker run -p 50057:50057 --env UAS_API_KEY=$UAS_API_KEY pseudocone:latest
```

## Interact with Service Locally
**Once the service is running**, to interact with the gRPC interface use the following process.
0. Get your/a user cookie:
    * Log into [bbc.co.uk](http://bbc.co.uk) and open up developer tools in your browser, find where to browse cookies and copy the value of your `ckns_atkn` cookie.
1. Install [gRPCurl](https://github.com/fullstorydev/grpcurl):
    ```
    # ensure go path correctly set: export GOPATH="$HOME/go"
    export PATH="$GOPATH/bin:$PATH
    go get github.com/fullstorydev/grpcurl/...
    go install github.com/fullstorydev/grpcurl/...
    ```
2. HealthCheck:

    ```
    # This should return an empty response.
    grpcurl -protoset ./pseudocone.protoset -plaintext -d '{}' localhost:50057 pseudocone.PseudoconeService.HealthCheck
    ```
3. ListContent
    ```
    # replace <user-cookie> with your cookie wrapped in double quotes
    grpcurl -protoset ./pseudocone.protoset -plaintext -d '{"user":{"cookie":<user-cookie>}, "limit":3, "offset":1}' localhost:50057 pseudocone.PseudoconeService.ListInteractions
    ```
## Tests
Run tests using:
```
pip3 install -r requirements_test.txt
python3 -m pytest --cov-report term-missing --cov=app -vv --cov-branch tests
```
## Making Changes to the `.proto` File
The following steps must be carried out when making changes to the `.proto` file:
#### 1. Regenerate service files `*_pb2.py` and `*_pb2_grpc.py`
These are the files/stubs used when writing code that interacts with the service. Simply run this command and make sure to replace `<service>`:
```bash
python -m grpc_tools.protoc \
  -I. \
  -I$GOPATH/src \
  -I$GOPATH/src/github.com/googleapis/googleapis \
  --python_out=./app/services \
  --grpc_python_out=./app/services \
  <service>.proto

```
Note: You may have to manually update the import statement in the `<service>_pb2_grpc.py` file from `import <service>_pb2` to `import app.services.<service>_pb2`.
#### 2. Regenerate `.protoset` File
The `.protoset` file is needed to use `gRPCurl` and is generated using the `.proto` file.
To generate:
```
python -m grpc_tools.protoc \                                                                             ✔  4210  16:42:43
    -I. \
    -I$GOPATH/src \
    -I$GOPATH/src/github.com/googleapis/googleapis \
    --proto_path=. \
    --descriptor_set_out=<service>.protoset \
    --include_imports \
    <service>.proto
```

### Code style
```
pycodestyle app
```

## Building & Deployment

This app is provided as with a Dockerfile which is used to build a container.
This should then be pushed to a container registry and deployed either as a
manual process or using something such as build triggers and a continuous
delivery platform like [Spinnaker](https://www.spinnaker.io/).
