#!/bin/bash

# e.g., parameter $1 'localhost:8181/v1/data/bts/contract'
# e.g., parameter $2: @contract.json
echo "DEBUG: call $1 with $2"
curl --location --request PUT "$1" -H 'Content-Type: application/json' -d "$2"
