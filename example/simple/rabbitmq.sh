#!/bin/bash

docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 -d rabbitmq:3-management
