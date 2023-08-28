#!/bin/bash
nohup nignx &
uvicorn main:app --host=0.0.0.0 --port=8200
