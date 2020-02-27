#!/bin/sh

#exec "$@"

uvicorn fastapi_hello_world:app --reload --host 0.0.0.0 --port 8000
