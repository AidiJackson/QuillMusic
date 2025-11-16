#!/bin/bash
redis-server --daemonize yes
cd quillmusic/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
