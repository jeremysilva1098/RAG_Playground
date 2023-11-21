#!/bin/bash

# start the vector db
cd vectordb
/bin/bash startVectorDB.sh

# build the app docker container
cd ../app
docker buildx build --platform=linux/x86_64 -t rag_playground .

# run the app
docker run -p 5000:5000 rag_playground