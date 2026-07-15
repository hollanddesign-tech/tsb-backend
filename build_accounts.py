import os
import json
from collections import defaultdict
from dotenv import load_dotenv
from pull_trades import pull_trades, pull_database, get_prop_value

load_dotenv()

ACCOUNTS_DB_ID = os.environ.get("ACCOUNTS_DB_ID", "your_accounts_database_id_here")


def build_accounts():
    account_pages = pull_database(ACCOUNTS_DB_ID)
    accounts = {}
    for page in account_pages:
        props = page["properties"]
        accounts[page["id"]] = {
            "name": get_prop_value(props.get("Name", {})),
            "starting_balance": get_prop_value(props.get("Starting Balance", {})) or 0,
            "status": get_prop_value(props.get("Status", {})),
            "type": get_prop_value(props.get("Type", {})),
        }

    stats = defaultdict(lambda: {"pnl": 0, "wins": 0, "losses": 0, "trades": 0})

    trades = pull_trades()
    for page in trades:
        props = page["properties"]
        account_ids = get_prop_value(props.get("Account", {})) or []
        pnl = get_prop_value(props.get("P&L ($)", {})) or 0
        outcome = get_prop_value(props.get("Outcome", {}))

        for account_id in account_ids:
            s = stats[account_id]
            s["pnl"] += pnl
            s["trades"] += 1
            if outcome == "Win":
                s["wins"] += 1
            elif outcome == "Loss":
                s["losses"] += 1

    result = []
    for account_id, info in accounts.items():
        s = stats.get(account_id, {"pnl": 0, "wins": 0, "losses": 0, "trades": 0})
        decided = s["wins"] + s["losses"]
        win_rate = round((s["wins"] / decided) * 100, 1) if decided > 0 else 0
        current_balance = round(info["starting_balance"] + s["pnl"], 2)

        result.append({
            "name": info["name"],
            "type": info["type"],
            "status": info["status"],
            "starting_balance": info["starting_balance"],
            "current_balance": current_balance,
            "total_pnl": round(s["pnl"], 2),
            "win_rate": win_rate,
            "trades": s["trades"],
        })

    return result


def main():
    result = build_accounts()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
