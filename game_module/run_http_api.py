"""Small runner script to start the HTTP API with uvicorn.

Run from your virtualenv:

    python -m game_module.run_http_api

Or directly:

    uvicorn game_module.http_api:app --host 127.0.0.1 --port 8000
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("game_module.http_api:app", host="127.0.0.1", port=8000, log_level="info")
