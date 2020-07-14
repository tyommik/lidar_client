import json

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except json.JSONDecodeError as err:
    raise

LIDARS_PARAMS = config.get("lidars", [])
LOG_LEVEL = config.get("loglevel", "INFO").upper()
KEEPALIVE = 3 # seconds
QUEUE_MAX_SIZE = 500