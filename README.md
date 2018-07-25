![Drone CI Status](http://drone.connected-data.tools.bbc.co.uk/api/badges/bbc/connected-data-pseudocone/status.svg)

# Pseudocone Component

The function of the Pseudocone component is to fetch data that is used for offline scoring. It has two principle roles:
 1. to deliver a list of test users to Justicia (together with items they have consumed); and
 2. to deliver user history items to bramble to be used to generate recommendations (copies the behaviour of
 [Bristlecone](https://github.com/bbc/connected-data-bristlecone))
 instead of reading user actions from UAS it reads from an offline UAS dump. Implemented with gRPC on a default port
 `50057`.

## Run Service Locally
### With Virtualenv

1. Create a virtualenv, install dependencies:
```
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

2. Run the service:

* To do this you will have to set the $DATA_DUMP_FILE_NAME variable, which is a path to an anonymised UAS data dump sample.
THe sample can be found in the dropbox "data" directory: "DB_DATA/SCV/anonymised_uas_extract.json"
```
DATA_DUMP_FILE_NAME=$DATA_DUMP_FILE_NAME python3 -m app.pseudocone
```

### With Docker
1. Build the image:
```
docker build -t pseudocone:latest .
```

2. Run the image:
```
docker run -p 50057:50057 --env pseudocone:latest
```

## Interact with Service Locally
**Once the service is running**, to interact with the gRPC interface use the following process.
0. Get your/a user id:

1. Install [gRPCurl](https://github.com/fullstorydev/grpcurl):
    ```
    # ensure go path correctly set: export GOPATH="$HOME/go"
    export PATH="$GOPATH/bin:$PATH"
    go get github.com/fullstorydev/grpcurl/...
    go install github.com/fullstorydev/grpcurl/...
    ```
2. HealthCheck:

    This should return an empty response.
    ```
    grpcurl -protoset ./pseudocone.protoset -plaintext -d '{}' localhost:50057 pseudocone.PseudoconeService.HealthCheck
    ```
3. ListTestDataUsers

    ```
    grpcurl -protoset ./pseudocone.protoset -plaintext -d '{"limit":8, "offset":1, "users":[{"id":"1155"}], "start_interaction_time": "2018-02-01T00:00:26.318497Z", "test_period_duration":"P0Y1M7DT0H0M0S"}' localhost:50057 pseudocone.PseudoconeService.ListTestDataUsers
    ```
    * Offset parameter not yet implemented so non-functional.

4. ListInteractionItems

    ```
    grpcurl -protoset ./pseudocone.protoset -plaintext -d '{"user":{"id":"1155"}, "limit":3, "offset":1, "end_interaction_time": "2018-03-02T00:00:26.318497Z", "train_period_duration":"P0Y1M7DT0H0M0S"}' localhost:50057 pseudocone.PseudoconeService.ListInteractions

    ```
     * Offset parameter not yet implemented so non-functional.
## Tests
Run tests using:
```
pip3 install -r requirements_test.txt
python3 -m pytest --cov-report term-missing --cov=app -vv --cov-branch tests
```
## Compile magical protocol buffer service from pseudocone.proto

Generate the service stub and message definitions in Python:

```
    python -m grpc_tools.protoc -I. -I$GOPATH/src  -I$GOPATH/src/github.com/googleapis/googleapis  --python_out=./app --grpc_python_out=./app pseudocone.proto
```

Don't forget to rename the import path in `app/pseudocone_pb2_grpc.py` from:

```
    import pseudocone_pb2 as pseudocone__pb2
```

To:

```
    import app.pseudocone_pb2 as rubus__pb2
```

#### 2. Regenerate `.protoset` File
The `.protoset` file is needed to use `gRPCurl` and is generated using the `.proto` file.
To generate:
```
python -m grpc_tools.protoc -I. \
    -I$GOPATH/src \
    -I$GOPATH/src/github.com/googleapis/googleapis \
    --proto_path=. \
    --descriptor_set_out=pseudocone.protoset \
    --include_imports \
    pseudocone.proto
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
