#!/bin/bash
# e.g., parameter $1 '195.148.22.62:8181/v1/policies/bts'
# e.g., parameter $2: @bts.rego
echo "DEBUG: call $1 with $2"
curl --location --request PUT "$1" -H 'Content-Type: text/plain' --data-binary "$2"
