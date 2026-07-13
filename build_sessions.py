import json
from collections import defaultdict
from pull_trades import pull_trades, get_prop_value

SESSION_ORDER = ["Asian", "London", "New York"]


def build_sessions(pages):
    sessions = defaultdict(lambda: {"pnl": 0, "wins": 0, "losses": 0, "trades": 0})

    for page in pages:
        props = page["properties"]
        session = get_prop_value(props.get("Session", {}))
        pnl = get_prop_value(props.get("P&L ($)", {}))
        outcome = get_prop_value(props.get("Outcome", {}))

        if session is None or pnl is None:
            continue

        sessions[session]["pnl"] += pnl
        sessions[session]["trades"] += 1
        if outcome == "Win":
            sessions[session]["wins"] += 1
        elif outcome == "Loss":
            sessions[session]["losses"] += 1

    result = []
    for session_name in SESSION_ORDER:
        s = sessions.get(session_name)
        if s is None:
            continue
        decided = s["wins"] + s["losses"]
        win_rate = round((s["wins"] / decided) * 100, 1) if decided > 0 else 0
        result.append({
            "session": session_name,
            "pnl": round(s["pnl"], 2),
            "trades": s["trades"],
            "win_rate": win_rate,
        })

    return result


def main():
    pages = pull_trades()
    result = build_sessions(pages)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
