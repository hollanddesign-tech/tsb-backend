import os
from dotenv import load_dotenv
from pull_trades import pull_database, get_prop_value

load_dotenv()
SETUPS_DB_ID = os.environ.get("SETUPS_DB_ID", "MISSING")

print(f"SETUPS_DB_ID being used: {SETUPS_DB_ID}")

pages = pull_database(SETUPS_DB_ID)
print(f"Number of pages returned: {len(pages)}")

if pages:
    print("\nFirst page's property names:")
    print(list(pages[0]["properties"].keys()))

    print("\nFirst page's raw values:")
    for key in pages[0]["properties"]:
        print(f"  {key}: {get_prop_value(pages[0]['properties'][key])}")
