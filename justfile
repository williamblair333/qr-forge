# qr-forge — run `just` for this list.
# Each recipe is one line; the commands are the ones the README documents.

# list recipes
default:
    @just --list

# install the Python deps for running without Docker (Python 3.12+)
setup:
    pip install --no-cache-dir -r requirements.txt

# run on the host without Docker on :8002 (add --reload while editing)
run *args:
    uvicorn app.main:app --host 0.0.0.0 --port 8002 {{args}}

# build and start the container on :8002
start:
    docker compose up --build --detach

# stop and remove the container
stop:
    docker compose down

# container state
status:
    docker compose ps
