#!/bin/bash
# e.g., parameter $1 'localhost:8181/v1/policies/bts'
# e.g., parameter $2: @bts.rego
echo "DEBUG: call $1 with $2"
curl --location --request PUT "$1" -H 'Content-Type: text/plain' --data-binary "$2"
