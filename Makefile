.PHONY: build test vet

build:
	go build -o btcmi-app ./...

test:
	go test ./...

vet:
	go vet ./...
