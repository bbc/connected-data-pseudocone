![Drone CI Status](https://drone.datalab.rocks/api/badges/bbc/connected-data-pseudocone/status.svg)

# Pseudocone Component

The function of the Pseudocone component is to fetch data that is used for offline scoring. It has two principle roles:
 1. to deliver a list of test users to Justicia (together with items they have consumed); and
 2. to deliver user history items to bramble to be used to generate recommendations (copies the behaviour of
 [Bristlecone](https://github.com/bbc/connected-data-bristlecone))
 instead of reading user actions from UAS it reads from offline UAS JSON dumps "end_YYYY_MM_DD_window_30_resource_types_clip_activity_types_plays_limit_none.json" located in the anonymised_logs folder in the GCP bucket "pseudocone_data_dump_v2" in the bbc-datalab project, see [here](https://console.cloud.google.com/storage/browser/pseudocone_data_dump_v2/anonymised_logs/?project=bbc-datalab&folder=true&organizationId=33845241025&showFTMessage=false).

 Implemented with gRPC on a default port
 `50057`.

## Run Service Locally
### With Virtualenv

1. Create a virtualenv, install dependencies:
```
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

2. Set the environment variable
To run locally, you will have to download the GCP credentials and set the $GOOGLE_APPLICATION_CREDENTIALS variable to the json file with the credentials. 
```
gcloud iam service-accounts keys create --iam-account=pseudocone@bbc-datalab.iam.gserviceaccount.com key.json
export GOOGLE_APPLICATION_CREDENTIALS=key.json
```

3. Run the service:
```
python3 -m app.pseudocone
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

We created a smaller table for you to try the following queries: "anonymised_logs/users_logs_sample.json"

3. ListTestDataUsers
```
grpcurl -protoset ./pseudocone.protoset -plaintext -d '{"limit":8, "offset":1, "users":[{"id":"6fcba5ec5f0d00efa0a9ed3a5053a20f3bdc4fdc127497a7556a046ca61bd50e"}], "start_interaction_time": "2018-12-15T00:00:26.318497Z", "test_period_duration":"P0Y0M7DT0H0M0S", "dataset":"anonymised_logs/users_logs_sample.json"}' localhost:50057 pseudocone.PseudoconeService.ListTestDataUsers
```

* Offset parameter not yet implemented so non-functional.

4. ListInteractionItems
```
grpcurl -protoset ./pseudocone.protoset -plaintext -d '{"user": {"id": "6fcba5ec5f0d00efa0a9ed3a5053a20f3bdc4fdc127497a7556a046ca61bd50e"}, "dataset":"anonymised_logs/users_logs_sample.json", "end_interaction_time":"2019-01-15T00:02:10.5Z"}' localhost:50057 pseudocone.PseudoconeService.ListInteractions```
```

5. ListTestDataUsersBetweenDates
```
grpcurl -protoset ./pseudocone.protoset -plaintext -d '{"limit":8, "offset":1, "users":[{"id":"13f13c1631d66a5948a29f1f483c8e7f30f1b71b389cecf10eb19072bda39682"}, {"id": "6fcba5ec5f0d00efa0a9ed3a5053a20f3bdc4fdc127497a7556a046ca61bd50e"}], "start_interaction_time": "2019-01-01T00:00:26.318497Z", "end_interaction_time":"2019-01-15T00:02:10.5Z", "dataset":"anonymised_logs/users_logs_sample.json"}' localhost:50057 pseudocone.PseudoconeService.ListTestDataUsersBetweenDates

```

* Offset parameter not yet implemented so non-functional.

## Tests
Run tests using make:
```
make test
```
Run integration tests (you need GCP credentials for this):
```
GOOGLE_APPLICATION_CREDENTIALS=key.json pytest --cov-report term-missing --cov=app --cov-branch tests/ -vv -m "integration"
```

## Compile magical protocol buffer service from pseudocone.proto

Generate the service stub and message definitions in Python:

```
make proto
```


#### 2. Regenerate `.protoset` File
The `.protoset` file is needed to use `gRPCurl` and is generated using the `.proto` file.
To generate:
```
make protoset
```

### Code style
```
make lint
```

## Building & Deployment

This app is provided as with a Dockerfile which is used to build a container.
This should then be pushed to a container registry and deployed either as a
manual process or using something such as build triggers and a continuous
delivery platform like [Spinnaker](https://www.spinnaker.io/).
