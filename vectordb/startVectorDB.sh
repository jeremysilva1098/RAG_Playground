#!/bin/bash

docker run -d -p 6333:6333 -v $(pwd)/data:/snapshots qdrant/qdrant ./qdrant --storage-snapshot /snapshots/latest.snapshot
