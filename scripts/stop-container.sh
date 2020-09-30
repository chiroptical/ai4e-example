#!/usr/bin/env bash

container_id=($(docker ps -q))
docker stop ${container_id[-1]}
