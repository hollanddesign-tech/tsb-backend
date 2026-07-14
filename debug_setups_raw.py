import os
import json
from dotenv import load_dotenv
from pull_trades import pull_database

load_dotenv()
SETUPS_DB_ID = os.environ.get("SETUPS_DB_ID")

pages = pull_database(SETUPS_DB_ID)
props = pages[0]["properties"]

print("RAW 'Win Rate' property:")
print(json.dumps(props["Win Rate"], indent=2))

print("\nRAW 'Times Used' property:")
print(json.dumps(props["Times Used"], indent=2))
