#!/bin/bash
CONTAINER_ALREADY_STARTED="CONTAINER_ALREADY_STARTED_PLACEHOLDER"
if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
    touch $CONTAINER_ALREADY_STARTED
    python configure.py
    echo "--- configured ---"
    python manage.py runserver 0.0.0.0:8000
else
    python manage.py runserver 0.0.0.0:8000
fi
