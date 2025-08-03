#!/bin/bash
CONTAINER_ALREADY_STARTED="CONTAINER_ALREADY_STARTED_PLACEHOLDER"
if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
    touch $CONTAINER_ALREADY_STARTED
    python configure.py
    echo "--- configured ---"
    uvicorn smt.asgi:application --host 0.0.0.0 --port 8000
else
    uvicorn smt.asgi:application --host 0.0.0.0 --port 8000
fi
