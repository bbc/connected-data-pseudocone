.PHONY: all grpc lint test

all: grpc

install_dependencies:
	pipenv install -d

proto:
	@echo 'Generating Python code from pseudocone.proto'
	pipenv run python3 -m grpc_tools.protoc \
		-I. \
		-I$(GOPATH)/src \
		-I$(GOPATH)/src/github.com/googleapis/googleapis \
		--python_out=./app/ \
		--grpc_python_out=./app/ \
		pseudocone.proto
	sed -ie 's/import pseudocone_pb2/import app.pseudocone_pb2/g' app/pseudocone_pb2_grpc.py
	# delete sed backup:
	rm -f app/services/pseudocone_pb2_grpc.pye

protoset:
	@echo 'Generating protoset from pseudocone.proto'
	pipenv run python3 -m grpc_tools.protoc \
		-I. \
		-I$(GOPATH)/src \
		-I$(GOPATH)/src/github.com/googleapis/googleapis \
		--proto_path=. \
		--descriptor_set_out=pseudocone.protoset \
		--include_imports \
		pseudocone.proto

test:
	@echo 'Running unit tests'
	pytest --cov-report term-missing --cov=app --cov-branch tests/ -vv -m "not integration"

integrationtest:
	@echo 'Running integration tests'
	pytest --cov-report term-missing --cov=app --cov-branch tests/ -vv -m "integration"

lint:
	@echo 'Cheking code for style'
	pycodestyle app tests
