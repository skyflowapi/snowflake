#!/bin/bash
set -e
set -x

# Set script directory and root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT=$(dirname "$SCRIPT_DIR")

# Paths to dependencies
GOPROTOPATH="$GOPATH/pkg/mod/google.golang.org/protobuf@v1.31.0"
GRPC_GATEWAY_PATH="$GOPATH/pkg/mod/github.com/grpc-ecosystem/grpc-gateway/v2@v2.19.1"
OPENAPI_PATH="$GRPC_GATEWAY_PATH/protoc-gen-openapiv2"

# Protobuf compiler command with import paths
protoc="protoc \
    -I. \
    -I$ROOT/proto/ \
    -I$GRPC_GATEWAY_PATH \
    -I$OPENAPI_PATH \
    -I$GOPROTOPATH \
    -I$GOPATH/pkg/mod"

# Navigate to proto files directory
PROTO_DIR="$ROOT/proto"
cd "$PROTO_DIR"

# Remove old generated files
rm -rf "$ROOT/proto/"*.pb.*go

# Generate gRPC server, gateway, and Go files
$protoc --go_out="$ROOT/proto/" \
        --go-grpc_out="$ROOT/proto/" \
        --grpc-gateway_out=logtostderr=true,request_context=true,allow_delete_body=true:"$ROOT/proto/" \
        ./detokenize.proto